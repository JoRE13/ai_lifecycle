import argparse
import csv
import json
from pathlib import Path

import pandas as pd


def normalize_text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def normalize_id(value: str) -> str:
    s = str(value).strip()
    if not s:
        return ""
    try:
        return str(int(float(s)))
    except ValueError:
        return s


def feasibility_mask(verdict: pd.Series, response_type: pd.Series) -> pd.Series:
    v = verdict.str.lower()
    r = response_type.str.lower()
    return (
        (r.eq("fix_first") & ~v.eq("incorrect"))
        | (r.eq("hint") & ~v.eq("correct_so_far"))
        | (r.eq("full_solution") & ~v.eq("fully_solved"))
        | (r.eq("ask_clarification") & ~v.eq("unclear"))
    )


def compute_metrics(df: pd.DataFrame, pred_col: str, exp_col: str, response_col: str) -> dict[str, float | int]:
    if df.empty:
        return {
            "rows": 0,
            "verdict_accuracy": 0.0,
            "non_feasible_count": 0,
            "non_feasible_ratio": 0.0,
        }

    pred = normalize_text(df[pred_col])
    exp = normalize_text(df[exp_col])
    response = normalize_text(df[response_col])

    verdict_accuracy = float((pred.str.lower() == exp.str.lower()).mean())
    non_feasible = feasibility_mask(pred, response)

    return {
        "rows": int(len(df)),
        "verdict_accuracy": verdict_accuracy,
        "non_feasible_count": int(non_feasible.sum()),
        "non_feasible_ratio": float(non_feasible.mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute Assignment 4 evaluation summary and compare with A3 baseline")
    parser.add_argument("--input", required=True, help="Path to Assignment 4 result CSV")
    parser.add_argument("--a3-v4", required=True, help="Path to assignment3/results_v4.csv")
    parser.add_argument("--out-tested", required=True, help="Path to tested subset CSV")
    parser.add_argument("--out-summary-csv", required=True, help="Path to one-row summary CSV")
    parser.add_argument("--out-summary-md", required=True, help="Path to markdown summary")
    parser.add_argument("--out-mismatches", required=True, help="Path to mismatch breakdown CSV")
    args = parser.parse_args()

    input_path = Path(args.input)
    a3_path = Path(args.a3_v4)

    a4 = pd.read_csv(input_path)
    # Handle the typo in source files while keeping compatibility.
    pred_col = "recieved_verdict" if "recieved_verdict" in a4.columns else "received_verdict"

    for col in ["id", "mode", "image", "category", "error_type", "expected_verdict", pred_col, "response_type", "message_is"]:
        if col in a4.columns:
            a4[col] = normalize_text(a4[col])

    a4["id_normalized"] = a4["id"].map(normalize_id) if "id" in a4.columns else ""
    tested = a4[a4[pred_col] != ""].copy()

    if "image" in tested.columns:
        tested["image_num"] = tested["image"].str.extract(r"(\d+)").astype(int)
    else:
        tested["image_num"] = pd.NA

    a3 = pd.read_csv(a3_path)
    for col in ["file_path", "expected_verdict", "verdict", "response_type"]:
        a3[col] = normalize_text(a3[col])
    a3["image_num"] = a3["file_path"].str.extract(r"(\d+)").astype(int)

    a3_subset = a3[a3["image_num"].isin(tested["image_num"])].copy()

    a4_metrics = compute_metrics(tested, pred_col, "expected_verdict", "response_type")
    a3_subset_metrics = compute_metrics(a3_subset, "verdict", "expected_verdict", "response_type")
    a3_full_metrics = compute_metrics(a3, "verdict", "expected_verdict", "response_type")

    tested["verdict_match"] = tested[pred_col].str.lower() == tested["expected_verdict"].str.lower()
    tested["policy_non_feasible"] = feasibility_mask(tested[pred_col], tested["response_type"])

    mismatches = tested[~tested["verdict_match"]].copy()

    tested_subset_cols = [
        "id_normalized",
        "mode",
        "image",
        "category",
        "error_type",
        "expected_verdict",
        pred_col,
        "response_type",
        "verdict_match",
        "policy_non_feasible",
    ]
    tested_subset_cols = [c for c in tested_subset_cols if c in tested.columns]
    tested[tested_subset_cols].rename(columns={pred_col: "received_verdict"}).to_csv(args.out_tested, index=False, encoding="utf-8-sig")

    mismatch_cols = [
        "id_normalized",
        "mode",
        "image",
        "category",
        "error_type",
        "expected_verdict",
        pred_col,
        "response_type",
        "message_is",
    ]
    mismatch_cols = [c for c in mismatch_cols if c in mismatches.columns]
    mismatches[mismatch_cols].rename(columns={pred_col: "received_verdict"}).to_csv(args.out_mismatches, index=False, encoding="utf-8-sig")

    mode_counts = tested["mode"].value_counts().to_dict() if "mode" in tested.columns else {}

    summary = {
        "source_file": str(input_path),
        "template_rows": int(len(a4)),
        "tested_rows": int(len(tested)),
        "meets_min_20_cases": bool(len(tested) >= 20),
        "tested_mode_counts": json.dumps(mode_counts, ensure_ascii=True),
        "a4_verdict_accuracy": a4_metrics["verdict_accuracy"],
        "a4_non_feasible_count": a4_metrics["non_feasible_count"],
        "a4_non_feasible_ratio": a4_metrics["non_feasible_ratio"],
        "a4_mismatch_count": int(len(mismatches)),
        "a4_mismatch_ids": json.dumps(mismatches["id_normalized"].tolist(), ensure_ascii=True),
        "a3_v4_subset_rows": a3_subset_metrics["rows"],
        "a3_v4_subset_verdict_accuracy": a3_subset_metrics["verdict_accuracy"],
        "a3_v4_subset_non_feasible_ratio": a3_subset_metrics["non_feasible_ratio"],
        "delta_accuracy_vs_a3_subset": a4_metrics["verdict_accuracy"] - a3_subset_metrics["verdict_accuracy"],
        "delta_non_feasible_ratio_vs_a3_subset": a4_metrics["non_feasible_ratio"] - a3_subset_metrics["non_feasible_ratio"],
        "a3_v4_full_rows": a3_full_metrics["rows"],
        "a3_v4_full_verdict_accuracy": a3_full_metrics["verdict_accuracy"],
        "a3_v4_full_non_feasible_ratio": a3_full_metrics["non_feasible_ratio"],
        "notes": "A4 metrics are computed only on tested rows where received verdict is present.",
    }

    with Path(args.out_summary_csv).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)

    lines = [
        "# Assignment 4 Evaluation Summary",
        "",
        f"- Source file: `{input_path.name}`",
        f"- Template rows: {summary['template_rows']}",
        f"- Tested rows: {summary['tested_rows']}",
        f"- Meets >=20 case requirement: {summary['meets_min_20_cases']}",
        f"- Mode distribution (tested): {summary['tested_mode_counts']}",
        "",
        "## A4 Prototype Results (tested rows only)",
        "",
        f"- Verdict accuracy: {summary['a4_verdict_accuracy']:.2%}",
        f"- Non-feasible count: {summary['a4_non_feasible_count']}",
        f"- Non-feasible ratio: {summary['a4_non_feasible_ratio']:.2%}",
        f"- Mismatch count: {summary['a4_mismatch_count']}",
        f"- Mismatch IDs: {summary['a4_mismatch_ids']}",
        "",
        "## Comparison to A3 v4 Baseline (same tested subset)",
        "",
        f"- A3 v4 subset rows: {summary['a3_v4_subset_rows']}",
        f"- A3 v4 subset verdict accuracy: {summary['a3_v4_subset_verdict_accuracy']:.2%}",
        f"- A3 v4 subset non-feasible ratio: {summary['a3_v4_subset_non_feasible_ratio']:.2%}",
        f"- Delta accuracy (A4 - A3 subset): {summary['delta_accuracy_vs_a3_subset']:+.2%}",
        f"- Delta non-feasible ratio (A4 - A3 subset): {summary['delta_non_feasible_ratio_vs_a3_subset']:+.2%}",
        "",
        "## Reference: A3 v4 Full Dataset",
        "",
        f"- A3 v4 full rows: {summary['a3_v4_full_rows']}",
        f"- A3 v4 full verdict accuracy: {summary['a3_v4_full_verdict_accuracy']:.2%}",
        f"- A3 v4 full non-feasible ratio: {summary['a3_v4_full_non_feasible_ratio']:.2%}",
        "",
        "## Note",
        "",
        f"- {summary['notes']}",
    ]

    Path(args.out_summary_md).write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote tested subset: {args.out_tested}")
    print(f"Wrote summary CSV: {args.out_summary_csv}")
    print(f"Wrote summary MD: {args.out_summary_md}")
    print(f"Wrote mismatches CSV: {args.out_mismatches}")


if __name__ == "__main__":
    main()
