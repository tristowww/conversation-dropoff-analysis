# Public example findings

## Question

Where does response length decline in AI-led research interviews, and is the answer stable enough to choose a review window?

## Observed results

Fresh analysis of the official public Anthropic Interviewer release: 1,250 interview transcripts and 14,495 parsed participant response slots. At least 100 responses per turn are required. Three zero-word participant slots are retained as zero. No engagement ratings are available.

| View, all groups | Largest absolute change | Largest percentage drop | Slope change | Direction change |
| --- | --- | --- | --- | --- |
| All turns | 10 | 14 | 4 | 4 |
| Exclude first response | 10 | 14 | 4 | 4 |
| Exclude each final response | 4 | 14 | 4 | 4 |
| Same conversations through turn 10 | 10 | 10 | 4 | 4 |

Numbers are participant turn positions selected by the heuristics, not measured dropout events. They identify different features of the curve, so a single universal warning turn would overstate the evidence.

The pooled series also conceals group differences. The all-turn creative-group results point to turn 9, while the scientist-group results point to turn 3. Excluding final responses moves the creative-group cues to turn 5. The same-conversation-through-10 view does not meet the 100-response minimum in either small specialist group. The interactive example shows the eligible sample sizes.

## What I would recommend

Review the question and response context around the flagged windows. In particular, check whether a short answer occurs because a question invites a short answer or because the conversation is closing. Compare within groups before deciding whether to shorten or change an interview. Any change should be evaluated using additional evidence about the participant experience.

The pattern is sensitive to the method, cohort and handling of final responses. The next useful step is contextual human review, followed by validation against independent ratings. This run alone does not justify intervening automatically at turn 4, 10, or 14.

## Checks that constrain the interpretation

- A seeded synthetic step decline is recovered at its known turn, 7, by all four methods.
- A flat synthetic series yields no cue.
- A noisy-flat synthetic series still yields a cue at turn 11. This illustrates why cue agreement is not proof of an engagement change.
- Twelve unit tests cover parsing, controls, sample filtering, missing turns, scale invariance and final-response handling.
- SQL and Python aggregates agree within floating-point tolerance for every cohort and turn.

These are method/implementation checks. No human validation, calibrated confidence estimate or prediction-accuracy result is claimed.

See the [source and attribution](DATA.md), [method](METHOD.md), and machine-readable `results/` files. Results are a secondary analysis by Teresa Ristow, not a conclusion or endorsement from the dataset publisher.
