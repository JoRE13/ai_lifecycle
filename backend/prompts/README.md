# Prompt Versioning

This backend keeps multiple prompt variants so behavior can be switched without rewriting files.

## Prompt Sets

- `modes/`:
  - Legacy single-pass-style mode prompts (`v1`).
- `modes_v2/`:
  - Strict legibility-aware mode prompts (`v2`).
- `modes_v2_expert/`:
  - Expert-mode prompts for `check_solution`:
  - `clarity/check_solution/prompt.txt`
  - `strict/check_solution/prompt.txt`
- `legibility_v2/prompt.txt`:
  - Dedicated pass-1 legibility checker prompt used by the two-pass pipeline.

## Runtime Switches

- `QUERY_PROMPT_VARIANT`:
  - `v1` -> use `modes/`
  - `v2` -> use `modes_v2/` (default)
- `QUERY_PIPELINE_MODE`:
  - `two_pass` -> run legibility pass, then reasoning pass if legible (default)
  - `single_pass` -> skip legibility pass and run reasoning pass only

## Request Field

- `expert_mode` form field on `POST /query`:
  - `off` (default)
  - `clarity`
  - `strict`

When `QUERY_PROMPT_VARIANT=v2`, `mode=check_solution`, and `expert_mode != off`,
the backend loads the corresponding expert prompt from `modes_v2_expert/`.

## Notes

- Two-pass mode is safer for unreadable handwriting but adds latency.
- Single-pass mode is lower latency but less robust against unreadable-input failure cases.
