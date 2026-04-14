# Qualitative Analysis Tables (Guidelines v2)

Scoring uses annotation-guideline v2 anchors with deterministic heuristics and one-line rationales per case.

## Prompt-Level Summary

| prompt_version   |   total_cases |   correct_verdicts |   correct_rate |   correctness_correct |   correctness_incorrect |   correctness_unclear |   correctness_rate |   policy_violations |   answer_leakage_cases |   avg_hint_usefulness |   avg_clarity |   avg_latency |
|:-----------------|--------------:|-------------------:|---------------:|----------------------:|------------------------:|----------------------:|-------------------:|--------------------:|-----------------------:|----------------------:|--------------:|--------------:|
| flash_dev_v5     |            50 |                 49 |             98 |                    44 |                       1 |                     5 |                 88 |                   0 |                      1 |                  4.48 |          3.96 |         22.47 |
| flash_low        |            50 |                 46 |             92 |                    38 |                       4 |                     8 |                 76 |                   0 |                      1 |                  4.35 |          3.82 |          2.85 |
| flash_med        |            50 |                 48 |             96 |                    45 |                       2 |                     3 |                 90 |                   0 |                      3 |                  4.17 |          3.84 |         22.76 |
| flash_med_v5     |            50 |                 49 |             98 |                    45 |                       1 |                     4 |                 90 |                   0 |                      3 |                  4.17 |          3.84 |         24.33 |
| flash_med_v6     |            50 |                 43 |             86 |                    41 |                       6 |                     3 |                 82 |                   0 |                      3 |                  3.91 |          4.06 |         16.73 |
| lite_med         |            50 |                 47 |             94 |                    37 |                       3 |                    10 |                 74 |                   0 |                      3 |                  4.17 |          4.08 |          7.84 |
| old              |            50 |                 48 |             96 |                    48 |                       2 |                     0 |                 96 |                   0 |                      2 |                  4.35 |          4.62 |        nan    |

## Prompt x Mode Summary

| prompt_version   | mode           |   cases |   correct_verdicts |   correct_rate |   correctness_rate |   policy_violations |   answer_leakage_cases | avg_hint_usefulness   |   avg_clarity | avg_latency   |
|:-----------------|:---------------|--------:|-------------------:|---------------:|-------------------:|--------------------:|-----------------------:|:----------------------|--------------:|:--------------|
| flash_dev_v5     | check_solution |      22 |                 21 |           95.5 |               77.3 |                   0 |                      0 | -                     |          4    | 20.2          |
| flash_dev_v5     | hint           |      23 |                 23 |          100   |               95.7 |                   0 |                      1 | 4.48                  |          4.57 | 21.93         |
| flash_dev_v5     | reveal         |       5 |                  5 |          100   |              100   |                   0 |                      0 | -                     |          1    | 34.93         |
| flash_low        | check_solution |      22 |                 19 |           86.4 |               59.1 |                   0 |                      0 | -                     |          3.86 | 2.62          |
| flash_low        | hint           |      23 |                 22 |           95.7 |               87   |                   0 |                      1 | 4.35                  |          4.35 | 2.58          |
| flash_low        | reveal         |       5 |                  5 |          100   |              100   |                   0 |                      0 | -                     |          1.2  | 5.12          |
| flash_med        | check_solution |      22 |                 20 |           90.9 |               81.8 |                   0 |                      0 | -                     |          3.73 | 25.42         |
| flash_med        | hint           |      23 |                 23 |          100   |               95.7 |                   0 |                      3 | 4.17                  |          4.57 | 17.55         |
| flash_med        | reveal         |       5 |                  5 |          100   |              100   |                   0 |                      0 | -                     |          1    | 35.02         |
| flash_med_v5     | check_solution |      22 |                 21 |           95.5 |               81.8 |                   0 |                      0 | -                     |          3.55 | 24.13         |
| flash_med_v5     | hint           |      23 |                 23 |          100   |               95.7 |                   0 |                      3 | 4.17                  |          4.74 | 19.31         |
| flash_med_v5     | reveal         |       5 |                  5 |          100   |              100   |                   0 |                      0 | -                     |          1    | 48.3          |
| flash_med_v6     | check_solution |      22 |                 17 |           77.3 |               77.3 |                   0 |                      0 | -                     |          4.14 | 16.19         |
| flash_med_v6     | hint           |      23 |                 21 |           91.3 |               82.6 |                   0 |                      3 | 3.91                  |          4.65 | 13.94         |
| flash_med_v6     | reveal         |       5 |                  5 |          100   |              100   |                   0 |                      0 | -                     |          1    | 31.43         |
| lite_med         | check_solution |      22 |                 19 |           86.4 |               50   |                   0 |                      0 | -                     |          4.27 | 8.41          |
| lite_med         | hint           |      23 |                 23 |          100   |               91.3 |                   0 |                      3 | 4.17                  |          4.39 | 5.84          |
| lite_med         | reveal         |       5 |                  5 |          100   |              100   |                   0 |                      0 | -                     |          1.8  | 14.51         |
| old              | check_solution |      22 |                 20 |           90.9 |               90.9 |                   0 |                      0 | -                     |          5    | -             |
| old              | hint           |      23 |                 23 |          100   |              100   |                   0 |                      2 | 4.35                  |          4.78 | -             |
| old              | reveal         |       5 |                  5 |          100   |              100   |                   0 |                      0 | -                     |          2.2  | -             |

## Files

- Row-level: `qualitative_scores_all_prompts.csv`
- Prompt summary: `qualitative_summary_by_prompt.csv`
- Prompt x mode summary: `qualitative_summary_by_prompt_and_mode.csv`