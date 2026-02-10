# Prompt Version Notes (Assignment 3)

This document records prompt iterations, what changed between versions, and why.
It is intended to satisfy the submission requirement: "all prompts tried, with version notes."

## Prompt files tried
- `assignment3/prompts/v1.txt`
- `assignment3/prompts/v2.txt`
- `assignment3/prompts/v3.txt`
- `assignment3/prompts/v4.txt`

## Summary table
| Version | What Changed | Why We Changed It | Observed Impact |
|---|---|---|---|
| `v1` | Baseline role + mode instructions + JSON schema. | Establish a simple control prompt and output contract. | Quant: `96.0%` verdict accuracy, `2.0%` non-feasible. |
| `v2` | Added stronger internal reasoning order and more explicit behavior rules (including `ask_clarification`). | Reduce ambiguity and improve policy compliance in `hint` / `check_solution`. | Quant: `94.0%` accuracy, `12.0%` non-feasible (regression in response-type consistency). |
| `v3` | Added few-shot examples for hint/check/reveal/unclear cases while keeping v2 structure. | Anchor behavior with concrete examples instead of only instruction prose. | Quant: `94.0%` accuracy, `0.0%` non-feasible (fixed v2 policy mismatch behavior). |
| `v4` | Expanded prompt significantly: step-by-step analysis checklist, explicit error taxonomy, stricter mode logic, JSON rules, and richer examples. | Improve consistency and pedagogical quality under varied inputs. | Quant: `96.0%` accuracy, `0.0%` non-feasible (best quantitative tradeoff). |

## Detailed notes per version

### v1 (baseline)
- Core elements:
  - Tutor role
  - Mode branching (`check_solution`, `hint`, `reveal`)
  - Icelandic language constraint
  - JSON output schema (`verdict`, `response_type`, `message_is`)
- Limitation observed:
  - Under-specified edge-case handling (ambiguity, action-type consistency).

### v2 (instruction-heavy revision)
- Changes vs v1:
  - Added explicit internal process: evaluate full student solution before responding.
  - Added clearer mode behaviors and first-error policy.
  - Added `ask_clarification` response option and unclear-input handling.
- Why:
  - Reduce hallucinated confidence and enforce better mode discipline.
- What happened:
  - Verdict accuracy remained high, but response-type policy mismatches increased in hint-error cases.

### v3 (few-shot grounding)
- Changes vs v2:
  - Added examples showing correct output style across modes and verdicts.
  - Included explicit examples for unclear input and fully solved hint behavior.
- Why:
  - Convert abstract rules into concrete target patterns.
- What happened:
  - Non-feasible outputs dropped to zero while keeping strong accuracy.

### v4 (comprehensive policy + pedagogy prompt) help from LLM
- Changes vs v3:
  - Added stricter analysis framework (problem parsing, step validation, error classification).
  - Added pedagogy/tone constraints and clearer safeguard language.
  - Expanded output requirements and consistency rules.
- Why:
  - Improve robustness and educational quality without sacrificing structured output compliance.
- What happened:
  - Matched best verdict accuracy and retained zero non-feasible rate.

## How to reproduce
From `assignment3/`:
```bash
python agentic.py
python review.py
python qualitative_review.py
```

## Metrics source of truth
- Quantitative summary derived from:
  - `assignment3/results_v1.csv`
  - `assignment3/results_v2.csv`
  - `assignment3/results_v3.csv`
  - `assignment3/results_v4.csv`
- Qualitative summary derived from:
  - `assignment3/qualitative_summary_by_prompt.csv`
