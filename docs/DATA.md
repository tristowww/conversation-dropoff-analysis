# Data source and attribution

## Public interviews

Source: **Anthropic Interviewer**, released by Anthropic with its December 4, 2025 research article, *Introducing Anthropic Interviewer: What 1,250 professionals told us about working with AI*.

- [Official dataset](https://huggingface.co/datasets/Anthropic/AnthropicInterviewer)
- [Official research article](https://www.anthropic.com/research/anthropic-interviewer)
- [Pinned source card](https://huggingface.co/datasets/Anthropic/AnthropicInterviewer/blob/c9e1ec1e6b093712b9c42235c7303ece647490e9/README.md)
- Source revision: `c9e1ec1e6b093712b9c42235c7303ece647490e9`
- Accessed and analyzed: November 12, 2026

The release contains 1,000 general-workforce interviews, 125 creative-professional interviews and 125 scientist interviews. The publisher states that participants consented to public release of the transcripts. This is a public research sample, not employee data collected by this project.

The card's license section states **data under CC-BY and code under MIT**. Its metadata header says `license: mit`; this project follows the more specific data-license statement for data and derived results. A CC-BY version is not specified in that section, so none is invented here. Attribution and links are retained with the derived aggregates.

Attribution: Kunal Handa, Michael Stern, Saffron Huang, Jerry Hong, Esin Durmus, Miles McCain, Grace Yun, AJ Alt, Thomas Millar, Alex Tamkin, Jane Leibrock, Stuart Ritchie, and Deep Ganguli (2025), *Introducing Anthropic Interviewer: What 1,250 professionals told us about working with AI*.

Changes: transcripts were parsed into role-labelled messages, participant word counts were calculated, and cohort/turn aggregates and sensitivity analyses were produced. Interview text and transcript IDs are not redistributed. Nothing in the analysis implies publisher endorsement.

| File | SHA-256 |
| --- | --- |
| workforce transcripts | `09ff307d42ebc8ed0b0ba25f41ffe2e50e9baa0b3c1ab4133ee528118817aab4` |
| creative transcripts | `d4e865b9959671990ceb51089c7494dbeed7560f9a623da873e6eb0f1b6506b4` |
| scientist transcripts | `338677e4a4ec17824cb5bfbc9242c8a37e7041157d34fb65e7e6fb58ea3f407a` |

Raw files are downloaded only when the reproduction script is run. They remain under the ignored `.local-data/` directory by default. Shared CSV/JSON results and the browser example retain only aggregate cells with at least 100 responses; no participant text or IDs are embedded. Public visibility does not make re-identification or individual profiling appropriate, and neither is attempted here.

## Synthetic controls

The committed numeric example uses random seed 19, with 120 invented conversations in each of three scenarios: a decline beginning at turn 7, an exactly flat series, and a noisy-flat series. All have 12 participant turns. These counts are generated independently of the public transcripts. They are not anonymized records, human ratings, or empirical findings about employees.
