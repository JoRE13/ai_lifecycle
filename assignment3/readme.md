# Assignment 3:

## Files

- `agentic.py`: Runs the model on all examples for each prompt version and saves outputs to CSV.
- `review.py`: Computes evaluation metrics from each `results_*.csv` file.
- `qualitative_review.py`: Runs rubric-based qualitative scoring and summary tables.
- `assignment3.csv`: Ground-truth dataset metadata (`image`, `mode`, `expected_verdict`, etc.).
- `prompts/v1.txt`, `prompts/v2.txt`, `prompts/v3.txt`, `prompts/v4.txt`: Prompt variants.
- `prompts/version_notes.md`: Version notes describing what changed between prompts and why.
- `img/`: Input images of problems and student solutions.
- `results_v1.csv`, `results_v2.csv`, `results_v3.csv`, `results_v4.csv`: Model outputs per prompt version.

## How it works

For each prompt version in `agentic.py`:

1. Load the prompt from `prompts/<version>.txt`.
2. Iterate through rows in `assignment3.csv`.
3. Open the corresponding image from `img/`.
4. Call Gemini (`models/gemini-3-flash-preview`) with:
   - prompt text
   - mode from dataset row
   - image
5. Enforce JSON output shape via `pydantic` schema:
   - `verdict`
   - `response_type`
   - `message_is`
6. Save outputs to `results_<version>.csv`.

The script retries on temporary server errors with exponential backoff.

## Evaluation metrics (`review.py`)

`review.py` computes two metrics per prompt version:

1. `Accuracy of verdicts`

- Fraction where `verdict == expected_verdict`.

2. `Ratio of non feasible results`

- Fraction where the action type contradicts the verdict according to these rules:
  - `fix_first` must imply `verdict == incorrect`
  - `hint` must imply `verdict == correct_so_far`
  - `full_solution` must imply `verdict == fully_solved`
  - `ask_clarification` must imply `verdict == unclear`

## Current quantitative results (50 rows per prompt)

| Prompt | Rows | Verdict accuracy | Non-feasible ratio |
| ------ | ---: | ---------------: | -----------------: |
| v1     |   50 |           ? |             ? |
| v2     |   50 |           ? |             ? |
| v3     |   50 |           ? |             ? |
| v4     |   50 |           ? |             ? |

## Run instructions

From the `assignment3` directory:

```bash
python3 agentic.py
python3 review.py
```

Required packages:

```bash
pip install google-genai pillow pandas pydantic
```

## Known issues / cleanup suggestions

- File paths in `agentic.py` are relative to the current working directory. Run from `assignment3/` or update paths to be script-relative.
