"""Calculate review cues; these heuristics do not measure disengagement."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import math
import re
import statistics

WORD = re.compile(r"\b[\w]+(?:['’][\w]+)*\b", re.UNICODE)
MARKER = re.compile(r"^(Assistant|AI|User):[ \t]*", re.MULTILINE)


@dataclass(frozen=True)
class Turn:
    conversation_id: str
    cohort: str
    turn: int
    words: int
    final: bool


def parse_transcript(text: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Parse the publisher's line-start role labels without calling any model.

    Both Assistant and AI label interviewer messages. Ambiguous role-label text
    inside a response requires separate review; this parser cannot infer intent.
    """
    matches = list(MARKER.finditer(text))
    if not matches or text[:matches[0].start()].strip():
        raise ValueError('Transcript has missing or unrecognized opening role label.')
    messages = []
    for i, m in enumerate(matches):
        role = 'user' if m.group(1) == 'User' else 'assistant'
        body = text[m.end():matches[i+1].start() if i+1 < len(matches) else len(text)].strip()
        messages.append((role, body))
    issues = []
    if any(not body for _, body in messages):
        issues.append('empty_message')
    if any(a[0] == b[0] for a, b in zip(messages, messages[1:])):
        issues.append('consecutive_same_role')
    return messages, issues


def user_turns(conversation_id: str, cohort: str, messages: list[tuple[str, str]]) -> list[Turn]:
    users = [body for role, body in messages if role == 'user']
    return [Turn(conversation_id, cohort, i+1, len(WORD.findall(body)), i+1 == len(users))
            for i, body in enumerate(users)]


def aggregate(turns: list[Turn], scenario: str = 'all_turns', cohort: str = 'all') -> list[dict]:
    selected = [t for t in turns if cohort == 'all' or t.cohort == cohort]
    if scenario == 'exclude_first':
        selected = [t for t in selected if t.turn != 1]
    elif scenario == 'exclude_final':
        selected = [t for t in selected if not t.final]
    elif scenario == 'fixed_cohort_10':
        lengths = defaultdict(int)
        for t in selected:
            lengths[t.conversation_id] = max(lengths[t.conversation_id], t.turn)
        selected = [t for t in selected if lengths[t.conversation_id] >= 10 and t.turn <= 10]
    elif scenario != 'all_turns':
        raise ValueError('Unknown scenario: ' + scenario)
    bins = defaultdict(list)
    for t in selected:
        if t.turn < 1 or t.words < 0:
            raise ValueError('Turns must be positive and word counts nonnegative.')
        bins[t.turn].append(t.words)
    return [{'turn': k, 'n': len(v), 'mean_words': statistics.mean(v),
             'median_words': statistics.median(v)} for k, v in sorted(bins.items())]


def detect(rows: list[dict], min_n: int = 100) -> dict:
    """Find the largest observed changes, without a significance threshold.

    All methods reuse the same response-length series and are not independent
    evidence. Curvature is a discrete slope difference, not geometric curvature.
    Adjacent differences never bridge a filtered/missing turn.
    """
    if not isinstance(min_n, int) or min_n < 1:
        raise ValueError('min_n must be a positive integer.')
    seen = set()
    for r in rows:
        if r['turn'] in seen:
            raise ValueError('Duplicate turn summary.')
        seen.add(r['turn'])
        if (not isinstance(r['turn'], int) or r['turn'] < 1 or
                not isinstance(r['n'], int) or r['n'] < 1 or
                not math.isfinite(r['mean_words']) or r['mean_words'] < 0):
            raise ValueError('Invalid turn summary.')
    points = sorted([dict(r) for r in rows if r['n'] >= min_n], key=lambda r: r['turn'])
    result = {'min_n': min_n, 'eligible_turns': [r['turn'] for r in points],
              'excluded_turns': [r['turn'] for r in rows if r['n'] < min_n],
              'methods': {name: None for name in ['euclidean', 'percentage', 'curvature', 'direction']}}
    if len(points) < 2:
        return result
    xr = points[-1]['turn'] - points[0]['turn'] or 1
    low = min(r['mean_words'] for r in points)
    yr = max(r['mean_words'] for r in points) - low or 1
    for r in points:
        r['x'] = (r['turn'] - points[0]['turn']) / xr
        r['y'] = (r['mean_words'] - low) / yr
    methods = result['methods']
    for a, b in zip(points, points[1:]):
        if b['turn'] != a['turn'] + 1 or b['mean_words'] >= a['mean_words']:
            continue
        distance = math.hypot(b['x']-a['x'], b['y']-a['y'])
        percentage = 100 * (b['mean_words']-a['mean_words']) / a['mean_words']
        for key, score in [('euclidean', distance), ('percentage', percentage)]:
            prior = methods[key]
            if prior is None or (score > prior['score'] if key == 'euclidean' else score < prior['score']):
                methods[key] = {'turn': b['turn'], 'score': score}
    for a, b, c in zip(points, points[1:], points[2:]):
        if b['turn'] != a['turn']+1 or c['turn'] != b['turn']+1 or c['mean_words'] >= b['mean_words']:
            continue
        d1, d2 = b['y']-a['y'], c['y']-b['y']
        curve = d2-d1
        if curve < 0 and (methods['curvature'] is None or curve < methods['curvature']['score']):
            methods['curvature'] = {'turn': c['turn'], 'score': curve}
        v1, v2 = (b['x']-a['x'], d1), (c['x']-b['x'], d2)
        ratio = sum(x*y for x,y in zip(v1,v2)) / (math.hypot(*v1)*math.hypot(*v2))
        angle = math.degrees(math.acos(max(-1, min(1, ratio))))
        if methods['direction'] is None or angle > methods['direction']['score']:
            methods['direction'] = {'turn': c['turn'], 'score': angle}
    return result


SCENARIOS = ['all_turns', 'exclude_first', 'exclude_final', 'fixed_cohort_10']


def study(turns: list[Turn], min_n: int = 100) -> dict:
    cohorts = ['all'] + sorted({t.cohort for t in turns})
    output = {'min_n': min_n, 'conversations': len({t.conversation_id for t in turns}),
              'user_turns': len(turns), 'cohorts': {}}
    for cohort in cohorts:
        output['cohorts'][cohort] = {}
        for scenario in SCENARIOS:
            rows = aggregate(turns, scenario, cohort)
            output['cohorts'][cohort][scenario] = {'rows': rows, 'detection': detect(rows, min_n)}
    return output
