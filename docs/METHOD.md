# Method and interpretation

The unit of analysis is a participant response at a numbered turn within a conversation. An ordinal participant turn is not a shared question or topic across interviews. Each curve is an average over the responses observed at that position.

## Four review cues

Turn number and average word count are separately min-max scaled within each eligible series. At least 100 responses are required per turn. Differences use consecutive turn positions only; a missing or suppressed position is never bridged.

1. **Euclidean distance:** the largest distance between adjacent normalized points where word count declines. For equally spaced turns, this largely follows the largest absolute decline.
2. **Percentage drop:** the largest relative decline from the preceding turn. A zero preceding mean cannot have a downward transition to another nonnegative mean.
3. **Discrete slope change:** the most negative change between adjacent normalized slopes, followed by a decline. This is an acceleration heuristic, not a continuous geometric curvature estimate.
4. **Direction change:** the largest angle between adjacent normalized segments where the later segment declines.

Three-point cues are reported at the response following the bend. Ties select the earliest eligible cue. A flat or increasing series has no downward cue. Any noisy series can still contain a largest local decline: the method has no learned decision boundary, statistical significance test, or calibrated confidence score. The four cues reuse the same signal and are not independent votes.

## Sensitivity views

- **All turns:** retains all recorded participant response slots, including zero-word slots.
- **Exclude first:** removes the first participant response to check opening acknowledgments.
- **Exclude final:** removes the final participant response in each transcript, rather than just the last pooled turn. A final response is a structural position, not an adjudicated completion label.
- **Same conversations through turn 10:** restricts the sample to conversations that reached at least ten participant responses and compares their first ten turns. This keeps the set of conversations fixed, but selects longer interviews and does not represent the full sample.

Groups are shown separately so that different interview structures are not hidden by a pooled average. Some group/view combinations have no cells meeting the minimum sample size; the demo reports that directly.

## Data quality

The parser recognizes line-start `Assistant:`, `AI:`, and `User:` labels. It checks missing opening labels, empty messages and consecutive identical roles. A role-like line inside a quoted response could be ambiguous; no manual transcript coding was performed. Word counts use a documented Unicode token pattern, retaining apostrophes inside words. Different tokenizers can produce different counts.

The fresh public run parsed 14,495 participant response slots, including three zero-word slots. Sixteen empty role-labelled messages were found overall and recorded in the audit. Zero-word response slots are retained as zeros, not silently dropped or imputed. Full source checksums and the source revision are preserved. SQL and Python means/counts were compared across every cohort and turn.

## What the current evidence supports

It supports a reproducible descriptive analysis of response length and sensitivity to sample/turn choices. It can help select material for review.

It does not establish engagement, fatigue, dissatisfaction, interview quality, a causal effect of the agent, or an intervention threshold. Short answers may reflect completion, concise questions, conversational style, or topic changes. Human judgments, contextual review and a separate validation study would be needed to distinguish these explanations.
