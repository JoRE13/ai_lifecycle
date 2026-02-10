# Qualitative Analysis Tables (Guidelines v2)

Scoring uses annotation-guideline v2 anchors with deterministic heuristics and one-line rationales per case.

## Prompt-Level Summary

| prompt_version   |   total_cases |   correctness_correct |   correctness_incorrect |   correctness_unclear |   correctness_rate |   policy_violations |   answer_leakage_cases |   avg_hint_usefulness |   avg_clarity |
|:-----------------|--------------:|----------------------:|------------------------:|----------------------:|-------------------:|--------------------:|-----------------------:|----------------------:|--------------:|
| v1               |            50 |                    45 |                       2 |                     3 |                 90 |                   1 |                      1 |                  3.87 |          4.64 |
| v2               |            50 |                    39 |                       3 |                     8 |                 78 |                   6 |                      1 |                  3.57 |          4.66 |
| v3               |            50 |                    47 |                       3 |                     0 |                 94 |                   0 |                      1 |                  4.3  |          4.8  |
| v4               |            50 |                    48 |                       2 |                     0 |                 96 |                   0 |                      2 |                  4.35 |          4.62 |

## Prompt x Mode Summary

| prompt_version   | mode           |   cases |   correctness_rate |   policy_violations |   answer_leakage_cases | avg_hint_usefulness   |   avg_clarity |
|:-----------------|:---------------|--------:|-------------------:|--------------------:|-----------------------:|:----------------------|--------------:|
| v1               | check_solution |      22 |               86.4 |                   0 |                      0 | -                     |          4.77 |
| v1               | hint           |      23 |               91.3 |                   1 |                      1 | 3.87                  |          4.87 |
| v1               | reveal         |       5 |              100   |                   0 |                      0 | -                     |          3    |
| v2               | check_solution |      22 |               81.8 |                   0 |                      0 | -                     |          4.91 |
| v2               | hint           |      23 |               69.6 |                   6 |                      1 | 3.57                  |          4.91 |
| v2               | reveal         |       5 |              100   |                   0 |                      0 | -                     |          2.4  |
| v3               | check_solution |      22 |               90.9 |                   0 |                      0 | -                     |          4.95 |
| v3               | hint           |      23 |               95.7 |                   0 |                      1 | 4.3                   |          5    |
| v3               | reveal         |       5 |              100   |                   0 |                      0 | -                     |          3.2  |
| v4               | check_solution |      22 |               90.9 |                   0 |                      0 | -                     |          5    |
| v4               | hint           |      23 |              100   |                   0 |                      2 | 4.35                  |          4.78 |
| v4               | reveal         |       5 |              100   |                   0 |                      0 | -                     |          2.2  |

## Files

- Row-level: `qualitative_scores_all_prompts.csv`
- Prompt summary: `qualitative_summary_by_prompt.csv`
- Prompt x mode summary: `qualitative_summary_by_prompt_and_mode.csv`