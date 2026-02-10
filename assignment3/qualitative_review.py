"""
Qualitative evaluation runner aligned to Annotation Guidelines v2.

Guideline dimensions:
- Correctness: Correct / Incorrect / Unclear
- Hint Usefulness: 1..5 (N/A outside hint mode)
- Clarity: 1..5

Outputs (v2):
- qualitative_scores_all_prompts.csv
- qualitative_summary_by_prompt.csv
- qualitative_summary_by_prompt_and_mode.csv
- qualitative_tables.md
- manual_review_sample.csv

Notes:
- This script is heuristic, not a symbolic math verifier.
- It is designed for consistent large-batch scoring + auditability.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parent
META_FILE = ROOT / "assignment3.csv"
PROMPT_VERSIONS = ["v1", "v2", "v3", "v4"]

SCORED_OUT = ROOT / "qualitative_scores_all_prompts.csv"
SUMMARY_OUT = ROOT / "qualitative_summary_by_prompt.csv"
MODE_SUMMARY_OUT = ROOT / "qualitative_summary_by_prompt_and_mode.csv"
TABLES_OUT = ROOT / "qualitative_tables.md"
MANUAL_SAMPLE_OUT = ROOT / "manual_review_sample.csv"


def norm_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def norm_token(value: Any) -> str:
    return norm_text(value).lower()


def is_response_type_policy_violation(verdict: str, response_type: str) -> bool:
    rt = norm_token(response_type)
    vd = norm_token(verdict)
    if rt == "fix_first" and vd != "incorrect":
        return True
    if rt == "hint" and vd != "correct_so_far":
        return True
    if rt == "full_solution" and vd != "fully_solved":
        return True
    if rt == "ask_clarification" and vd != "unclear":
        return True
    return False


def has_any_pattern(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def detect_answer_leakage(mode: str, message: str) -> bool:
    if norm_token(mode) != "hint":
        return False

    t = message.lower()
    leakage_patterns = [
        r"\bsvari[dt]?\s+er\b",
        r"\blokasvar\b",
        r"\blausnin\s+er\b",
        r"\bx\s*=\s*[-+]?\d+([.,]\d+)?\b",
        r"^\s*\$?.*=\s*[-+]?\d+([.,]\d+)?\s*$",
    ]
    return has_any_pattern(t, leakage_patterns)


def contradiction_with_verdict(verdict: str, message: str) -> bool:
    vd = norm_token(verdict)
    t = message.lower()

    positive_patterns = [
        r"\bvel\s+gert\b",
        r"\bfrab[ae]rt\b",
        r"\br[eé]tt\b",
        r"\b[aá]\s+r[eé]ttri\s+lei[dh]\b",
    ]
    negative_patterns = [
        r"\bekki\s+alveg\s+r[eé]tt\b",
        r"\bvilla\b",
        r"\brangt\b",
        r"\bmist[oe]k\b",
    ]
    unclear_patterns = [
        r"\b[oó]lj[óo]s\b",
        r"\bskrifa[dt]?\s+aftur\b",
        r"\bclarif",
        r"\bvantar\s+uppl",
    ]

    has_pos = has_any_pattern(t, positive_patterns)
    has_neg = has_any_pattern(t, negative_patterns)
    has_unclear = has_any_pattern(t, unclear_patterns)

    if vd == "incorrect" and has_pos and not has_neg:
        return True
    if vd in ("fully_solved", "correct_so_far") and has_neg and not has_pos:
        return True
    if vd == "unclear" and not has_unclear:
        return True
    return False


def score_correctness(
    expected_verdict: str,
    predicted_verdict: str,
    response_type: str,
    message: str,
) -> tuple[str, str]:
    exp_v = norm_token(expected_verdict)
    pred_v = norm_token(predicted_verdict)
    msg = norm_text(message)

    if not pred_v:
        return "Unclear", "Missing verdict field."
    if not msg:
        return "Unclear", "Missing explanation text."
    if pred_v != exp_v:
        return "Incorrect", f"Verdict mismatch (expected {exp_v}, got {pred_v})."
    if is_response_type_policy_violation(pred_v, response_type):
        return "Unclear", "Verdict and response_type combination is policy-inconsistent."
    if contradiction_with_verdict(pred_v, msg):
        return "Unclear", "Explanation language contradicts the predicted verdict."

    return "Correct", "Verdict and explanation are consistent with expected behavior."


def score_hint_usefulness(
    mode: str,
    expected_verdict: str,
    predicted_verdict: str,
    response_type: str,
    message: str,
) -> tuple[str, str]:
    if norm_token(mode) != "hint":
        return "N/A", "Not scored outside hint mode."

    exp_v = norm_token(expected_verdict)
    pred_v = norm_token(predicted_verdict)
    rt = norm_token(response_type)
    msg = norm_text(message)
    msg_l = msg.lower()

    if not msg:
        return "1", "Empty hint content."
    if detect_answer_leakage(mode, msg):
        return "1", "Possible answer leakage detected in hint mode."
    if pred_v != exp_v:
        return "1", "Verdict mismatch likely makes hint misleading."
    if is_response_type_policy_violation(pred_v, rt):
        return "1", "Hint action type conflicts with verdict policy."

    # Base score by expected tutoring behavior
    if exp_v == "incorrect":
        score = 4 if rt == "fix_first" else 2
    elif exp_v == "correct_so_far":
        score = 4 if rt == "hint" else 2
    elif exp_v == "fully_solved":
        score = 4 if rt == "explanation" else 2
    elif exp_v == "unclear":
        score = 4 if rt == "ask_clarification" else 1
    else:
        score = 3

    words = len(msg.split())
    has_question = "?" in msg
    generic_patterns = [
        r"\bathuga[dtu]*\b",
        r"\bprofa[dtu]*\s+aftur\b",
        r"\bhugsa[dtu]*\s+um\b",
    ]

    # Apply style adjustments
    if words < 7:
        score -= 1
    if words > 85:
        score -= 1
    if has_any_pattern(msg_l, generic_patterns):
        score -= 1
    if exp_v == "correct_so_far" and rt == "hint" and has_question:
        score += 1

    score = max(1, min(5, int(score)))

    rationale = {
        1: "Not helpful/misleading for current student state.",
        2: "Guidance is vague or weakly actionable.",
        3: "Partly useful but lacks precision.",
        4: "Clear and useful next-step guidance.",
        5: "Clear, actionable, and tightly scoped hint.",
    }[score]
    return str(score), rationale


def score_clarity(message: str) -> tuple[int, str]:
    msg = norm_text(message)
    if not msg:
        return 1, "No readable content."

    words = len(msg.split())
    lines = msg.count("\n") + 1
    symbol_heavy = len(re.findall(r"[{}\\\\]", msg)) > 12
    garbled = "Ã" in msg

    if words <= 5:
        score = 2
    elif words <= 45:
        score = 5
    elif words <= 90:
        score = 4
    elif words <= 150:
        score = 3
    else:
        score = 2

    if lines > 10:
        score -= 1
    if symbol_heavy:
        score -= 1
    if garbled:
        score -= 1

    score = max(1, min(5, score))
    rationale = {
        1: "Very unclear and hard to parse.",
        2: "Hard to understand due to phrasing/structure.",
        3: "Understandable with effort.",
        4: "Clear and readable for students.",
        5: "Very clear and concise.",
    }[score]
    return score, rationale


def build_scored_rows() -> pd.DataFrame:
    meta = pd.read_csv(META_FILE)[
        ["image", "id", "mode", "expected_verdict", "category", "error_type"]
    ]

    rows: list[dict[str, Any]] = []
    for version in PROMPT_VERSIONS:
        result_path = ROOT / f"results_{version}.csv"
        result_df = pd.read_csv(result_path)
        result_df["image"] = result_df["file_path"].str.replace("./img/", "", regex=False)

        merged = result_df.merge(meta, on=["image", "expected_verdict"], how="left")
        for r in merged.itertuples(index=False):
            message = norm_text(r.message_is)
            response_type = norm_text(r.response_type)
            verdict = norm_text(r.verdict)
            expected_verdict = norm_text(r.expected_verdict)
            mode = norm_text(r.mode)

            correctness, correctness_rationale = score_correctness(
                expected_verdict,
                verdict,
                response_type,
                message,
            )
            hint_score, hint_rationale = score_hint_usefulness(
                mode,
                expected_verdict,
                verdict,
                response_type,
                message,
            )
            clarity, clarity_rationale = score_clarity(message)

            policy_violation = is_response_type_policy_violation(verdict, response_type)
            answer_leakage = detect_answer_leakage(mode, message)

            audit_rationale = (
                f"Correctness={correctness}; "
                f"Hint={hint_score}; Clarity={clarity}. "
                f"Main: {correctness_rationale}"
            )

            rows.append(
                {
                    "prompt_version": version,
                    "id": r.id,
                    "image": r.image,
                    "mode": mode,
                    "category": r.category,
                    "error_type": r.error_type,
                    "expected_verdict": expected_verdict,
                    "verdict": verdict,
                    "response_type": norm_token(response_type),
                    "policy_violation": policy_violation,
                    "answer_leakage": answer_leakage,
                    "correctness_label": correctness,
                    "correctness_rationale": correctness_rationale,
                    "hint_usefulness_1_5": hint_score,
                    "hint_usefulness_rationale": hint_rationale,
                    "clarity_1_5": clarity,
                    "clarity_rationale": clarity_rationale,
                    "audit_rationale": audit_rationale,
                    "message_is": message,
                }
            )

    return pd.DataFrame(rows)


def save_outputs(scored: pd.DataFrame) -> None:
    scored.to_csv(SCORED_OUT, index=False, encoding="utf-8-sig")

    hint_numeric = pd.to_numeric(
        scored["hint_usefulness_1_5"].replace("N/A", pd.NA), errors="coerce"
    )

    summary = (
        scored.assign(hint_usefulness_numeric=hint_numeric)
        .groupby("prompt_version")
        .agg(
            total_cases=("id", "count"),
            correctness_correct=("correctness_label", lambda s: (s == "Correct").sum()),
            correctness_incorrect=("correctness_label", lambda s: (s == "Incorrect").sum()),
            correctness_unclear=("correctness_label", lambda s: (s == "Unclear").sum()),
            correctness_rate=("correctness_label", lambda s: (s == "Correct").mean()),
            policy_violations=("policy_violation", "sum"),
            answer_leakage_cases=("answer_leakage", "sum"),
            avg_hint_usefulness=("hint_usefulness_numeric", "mean"),
            avg_clarity=("clarity_1_5", "mean"),
        )
        .reset_index()
    )
    summary["correctness_rate"] = (summary["correctness_rate"] * 100).round(1)
    summary["avg_hint_usefulness"] = summary["avg_hint_usefulness"].round(2)
    summary["avg_clarity"] = summary["avg_clarity"].round(2)
    summary.to_csv(SUMMARY_OUT, index=False, encoding="utf-8-sig")

    mode_summary = (
        scored.assign(hint_usefulness_numeric=hint_numeric)
        .groupby(["prompt_version", "mode"])
        .agg(
            cases=("id", "count"),
            correctness_rate=("correctness_label", lambda s: (s == "Correct").mean()),
            policy_violations=("policy_violation", "sum"),
            answer_leakage_cases=("answer_leakage", "sum"),
            avg_hint_usefulness=("hint_usefulness_numeric", "mean"),
            avg_clarity=("clarity_1_5", "mean"),
        )
        .reset_index()
    )
    mode_summary["correctness_rate"] = (mode_summary["correctness_rate"] * 100).round(1)
    mode_summary["avg_hint_usefulness"] = mode_summary["avg_hint_usefulness"].round(2)
    mode_summary["avg_clarity"] = mode_summary["avg_clarity"].round(2)
    mode_summary.to_csv(MODE_SUMMARY_OUT, index=False, encoding="utf-8-sig")

    md_lines = [
        "# Qualitative Analysis Tables (Guidelines v2)",
        "",
        (
            "Scoring uses annotation-guideline v2 anchors with deterministic heuristics "
            "and one-line rationales per case."
        ),
        "",
        "## Prompt-Level Summary",
        "",
        summary.to_markdown(index=False),
        "",
        "## Prompt x Mode Summary",
        "",
        mode_summary.fillna("-").to_markdown(index=False),
        "",
        "## Files",
        "",
        f"- Row-level: `{SCORED_OUT.name}`",
        f"- Prompt summary: `{SUMMARY_OUT.name}`",
        f"- Prompt x mode summary: `{MODE_SUMMARY_OUT.name}`",
    ]
    TABLES_OUT.write_text("\n".join(md_lines), encoding="utf-8")


def build_manual_sample(scored: pd.DataFrame) -> None:
    """Create a compact stratified sample for manual trust checking."""
    samples: list[pd.DataFrame] = []
    for version, group in scored.groupby("prompt_version"):
        correct = group[group["correctness_label"] == "Correct"]
        non_correct = group[group["correctness_label"] != "Correct"]

        correct_pick = correct.sample(n=min(3, len(correct)), random_state=42)
        non_correct_pick = non_correct.sample(n=min(2, len(non_correct)), random_state=42)
        samples.append(pd.concat([correct_pick, non_correct_pick], ignore_index=True))

    sample_df = pd.concat(samples, ignore_index=True).sort_values(["prompt_version", "id"])
    sample_cols = [
        "prompt_version",
        "id",
        "image",
        "mode",
        "expected_verdict",
        "verdict",
        "response_type",
        "correctness_label",
        "hint_usefulness_1_5",
        "clarity_1_5",
        "policy_violation",
        "answer_leakage",
        "audit_rationale",
        "message_is",
    ]
    sample_df[sample_cols].to_csv(MANUAL_SAMPLE_OUT, index=False, encoding="utf-8-sig")


def main() -> None:
    scored = build_scored_rows()
    save_outputs(scored)
    build_manual_sample(scored)
    print(f"Wrote {SCORED_OUT.name}")
    print(f"Wrote {SUMMARY_OUT.name}")
    print(f"Wrote {MODE_SUMMARY_OUT.name}")
    print(f"Wrote {TABLES_OUT.name}")
    print(f"Wrote {MANUAL_SAMPLE_OUT.name}")


if __name__ == "__main__":
    main()
