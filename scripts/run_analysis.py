"""Build aggregate diagnostics from the public interviews and synthetic controls."""
import argparse
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from conversation_dropoff.analysis import Turn, aggregate, parse_transcript, study, user_turns
from download_anthropic import EXPECTED


def synthetic():
    rng = random.Random(19)
    turns = []
    for group in ['injected_decline', 'flat', 'noisy_flat']:
        for i in range(120):
            for k in range(1, 13):
                words = (80 if k < 7 else 30) if group == 'injected_decline' else 80
                if group != 'flat':
                    words += rng.randint(-4, 4)
                turns.append(Turn(f'{group}-{i:03}', group, k, words, k == 12))
    return turns


def run(data_dir, output):
    output.mkdir(parents=True, exist_ok=True)
    turns, source_files = [], []
    audit = {'transcripts': 0, 'role_sequence_issues': Counter(), 'empty_user_responses': 0,
             'duplicate_ids': 0, 'role_message_counts': Counter(), 'sql_python_aggregation_match': False}
    ids = set()
    for cohort in ['workforce', 'creatives', 'scientists']:
        path = data_dir / f'{cohort}.csv'
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != EXPECTED[cohort]:
            raise ValueError('Source checksum mismatch: ' + cohort)
        source_files.append({'cohort': cohort, 'sha256': digest})
        with path.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ['transcript_id', 'text']:
                raise ValueError('Unexpected dataset schema.')
            for row in reader:
                key = row['transcript_id']
                if key in ids:
                    audit['duplicate_ids'] += 1
                    raise ValueError('Duplicate transcript ID.')
                ids.add(key)
                messages, issues = parse_transcript(row['text'])
                audit['role_sequence_issues'].update(issues)
                audit['role_message_counts'].update(role for role, _ in messages)
                records = user_turns(key, cohort, messages)
                audit['empty_user_responses'] += sum(t.words == 0 for t in records)
                if not records:
                    raise ValueError('Transcript without user responses.')
                turns.extend(records)
                audit['transcripts'] += 1
    # Independent SQL aggregation is checked against Python for every cohort/turn.
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE turns (conversation_id TEXT, cohort TEXT, turn INTEGER, words INTEGER, final INTEGER, PRIMARY KEY(conversation_id, turn))')
    db.executemany('INSERT INTO turns VALUES (?, ?, ?, ?, ?)', [(t.conversation_id,t.cohort,t.turn,t.words,t.final) for t in turns])
    sql_rows = list(db.execute((ROOT/'sql/turn_summary.sql').read_text()))
    for cohort,k,n,mean in sql_rows:
        reference = next(r for r in aggregate(turns, cohort=cohort) if r['turn'] == k)
        assert n == reference['n'] and abs(mean-reference['mean_words']) < 1e-9
    audit['sql_python_aggregation_match'] = True
    db.close()
    public = study(turns)
    public['source'] = {'dataset': 'Anthropic/AnthropicInterviewer',
                        'revision': 'c9e1ec1e6b093712b9c42235c7303ece647490e9',
                        'files': source_files}
    fake = synthetic()
    synthetic_result = study(fake)
    with (ROOT/'data/synthetic_turns.csv').open('w',newline='',encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['conversation_id','cohort','turn','words','final'])
        writer.writerows((t.conversation_id,t.cohort,t.turn,t.words,int(t.final)) for t in fake)
    (output/'data_quality.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    with (output/'turn_summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=['cohort','scenario','turn','n','mean_words','median_words'])
        writer.writeheader()
        for cohort, scenarios in public['cohorts'].items():
            for scenario, value in scenarios.items():
                for r in value['rows']:
                    # Suppress sparse aggregate cells in the shared CSV/JSON/UI.
                    if r['n'] >= 100:
                        writer.writerow({'cohort':cohort,'scenario':scenario,**r})
    # Shared results show only >=100-response cells; counts are not transcript IDs.
    for result in [public,synthetic_result]:
        for scenarios in result['cohorts'].values():
            for value in scenarios.values():
                value['rows'] = [r for r in value['rows'] if r['n'] >= 100]
    (output/'anthropic_aggregate.json').write_text(json.dumps(public,indent=2),encoding='utf-8')
    (output/'synthetic_checks.json').write_text(json.dumps(synthetic_result,indent=2),encoding='utf-8')
    bundle={'public':public,'synthetic':synthetic_result}
    (ROOT/'demo/data.js').write_text('window.EXAMPLE_DATA = '+json.dumps(bundle)+';\n',encoding='utf-8')
    print(json.dumps({'transcripts':audit['transcripts'],'user_turns':len(turns),
                      'role_sequence_issues':dict(audit['role_sequence_issues']),
                      'empty_user_responses':audit['empty_user_responses'],
                      'sql_python_match':True,'baseline':public['cohorts']['all']['all_turns']['detection']['methods']}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir',type=Path,default=Path('.local-data/anthropic'))
    p.add_argument('--output',type=Path,default=ROOT/'results')
    args=p.parse_args()
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'demo').mkdir(exist_ok=True)
    run(args.data_dir,args.output)
