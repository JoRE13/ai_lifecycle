from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import time
from typing import Iterable
from urllib import error, request

from dotenv import load_dotenv

import pandas as pd


ROOT = Path(__file__).resolve().parent
TEST_CASES_PATH = ROOT / "test_cases.csv"

load_dotenv()
load_dotenv(ROOT / ".env")
DEFAULT_MODEL = os.getenv("LLM_AS_JUDGE_MODEL", "openai/gpt-5.4-nano")


@dataclass(frozen=True)
class JudgeCategory:
    name: str
    description: str
    scale_anchor_1: str
    scale_anchor_5: str


RECOMMENDED_CATEGORIES: tuple[JudgeCategory, ...] = (
    JudgeCategory(
        name="mathematical_correctness",
        description="Is the response mathematically correct and consistent with the student's state?",
        scale_anchor_1="Contains clear mathematical mistakes or misleading claims.",
        scale_anchor_5="Mathematically correct and fully consistent with the case.",
    ),
    JudgeCategory(
        name="pedagogical_helpfulness",
        description="How useful is the response for helping the student learn or continue correctly?",
        scale_anchor_1="Unhelpful, confusing, or misleading.",
        scale_anchor_5="Highly useful, well targeted, and supports learning effectively.",
    ),
    JudgeCategory(
        name="policy_compliance",
        description="Does the response obey the requested mode boundaries, such as hint/check/reveal behavior?",
        scale_anchor_1="Clearly violates the intended response policy.",
        scale_anchor_5="Fully respects the intended mode behavior.",
    ),
    JudgeCategory(
        name="clarity",
        description="Is the Icelandic response clear, readable, and natural for a student?",
        scale_anchor_1="Hard to understand or poorly phrased.",
        scale_anchor_5="Very clear, natural, and easy to follow.",
    ),
    JudgeCategory(
        name="specificity",
        description="Does the response point to the relevant issue or next step with enough precision?",
        scale_anchor_1="Too vague to be actionable.",
        scale_anchor_5="Precise and directly actionable.",
    ),
)


def normalize_image_key(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip().replace("\\", "/")
    return Path(text).stem.lower()


def recommend_categories() -> list[str]:
    return [category.name for category in RECOMMENDED_CATEGORIES]


def _judge_response_schema(categories: Iterable[JudgeCategory]) -> dict[str, object]:
    category_names = [category.name for category in categories]
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "overall_score": {"type": "integer", "minimum": 1, "maximum": 5},
            "summary": {"type": "string"},
            "scores": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    name: {"type": "integer", "minimum": 1, "maximum": 5}
                    for name in category_names
                },
                "required": category_names,
            },
        },
        "required": ["overall_score", "summary", "scores"],
    }


def build_single_model_judge_prompt(
    *,
    row: pd.Series,
    categories: Iterable[JudgeCategory] = RECOMMENDED_CATEGORIES,
) -> str:
    categories_text = "\n".join(
        [
            (
                f"- {category.name}: {category.description}\n"
                f"  1 = {category.scale_anchor_1}\n"
                f"  5 = {category.scale_anchor_5}"
            )
            for category in categories
        ]
    )

    return f"""
You are evaluating one tutor response for a handwritten math tutoring case.

Case metadata:
- case_id: {row['case_id']}
- expected_mode: {row['expected_mode']}
- expected_verdict: {row['expected_verdict_meta']}
- test_category: {row['test_category']}
- error_type: {row['test_error_type']}

Model output:
- prompt_version: {row['prompt_version']}
- verdict: {row['verdict']}
- response_type: {row['response_type']}
- message_is: {row['message_is']}

Score this single response from 1 to 5 on each category below:
{categories_text}

Return JSON only in this shape:
{{
  "overall_score": 1,
  "summary": "short justification",
  "scores": {{
    "mathematical_correctness": 1,
    "pedagogical_helpfulness": 1,
    "policy_compliance": 1,
    "clarity": 1,
    "specificity": 1
  }}
}}
""".strip()


def build_single_model_judge_dataframe(
    results_csv: str | Path,
    *,
    test_cases_csv: str | Path = TEST_CASES_PATH,
    categories: Iterable[JudgeCategory] = RECOMMENDED_CATEGORIES,
    show_progress: bool = True,
) -> pd.DataFrame:
    results_df = pd.read_csv(results_csv).copy()
    test_cases_df = pd.read_csv(test_cases_csv).copy()
    results_df.columns = results_df.columns.str.strip()
    test_cases_df.columns = test_cases_df.columns.str.strip()

    results_df["image_key"] = results_df["file_path"].map(normalize_image_key)
    test_cases_df["image_key"] = test_cases_df["image"].map(normalize_image_key)

    test_cases_df = test_cases_df.rename(
        columns={
            "id": "case_id",
            "mode": "expected_mode",
            "expected_verdict": "expected_verdict_meta",
            "category": "test_category",
            "error_type": "test_error_type",
        }
    )

    merged = (
        test_cases_df[
            ["case_id", "image_key", "expected_mode", "expected_verdict_meta", "test_category", "test_error_type"]
        ]
        .merge(results_df, on="image_key", how="inner")
        .sort_values("case_id")
        .reset_index(drop=True)
    )

    prompts: list[str] = []
    total = len(merged)
    for index, row in enumerate(merged.itertuples(index=False), start=1):
        if show_progress and (index == 1 or index == total or index % 5 == 0):
            print(f"Building judge prompts: {index}/{total}")
        prompts.append(build_single_model_judge_prompt(row=pd.Series(row._asdict()), categories=categories))

    merged["judge_categories"] = ", ".join(recommend_categories())
    merged["judge_prompt"] = prompts
    return merged


def summarize_results_file(results_csv: str | Path, *, show_progress: bool = True) -> pd.DataFrame:
    scored = build_single_model_judge_dataframe(results_csv, show_progress=show_progress)
    columns = [
        "case_id",
        "prompt_version",
        "expected_mode",
        "expected_verdict_meta",
        "verdict",
        "response_type",
        "judge_categories",
        "judge_prompt",
    ]
    return scored[columns]


def _extract_json_object(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Response did not contain a JSON object")
    return text[start : end + 1]


def call_openrouter_judge(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    categories: Iterable[JudgeCategory] = RECOMMENDED_CATEGORIES,
    max_retries: int = 5,
) -> dict[str, object]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "JudgeResponse",
                "strict": True,
                "schema": _judge_response_schema(categories),
            },
        },
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "ai_lifecycle_llm_as_judge",
    }

    for attempt in range(max_retries):
        try:
            req = request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with request.urlopen(req) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            return json.loads(_extract_json_object(content))
        except error.HTTPError as exc:
            if attempt == max_retries - 1:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"OpenRouter HTTP {exc.code}: {detail}") from exc
            wait = 2 ** attempt
            print(f"Judge request failed with HTTP {exc.code}, retrying in {wait}s...")
            time.sleep(wait)
        except Exception:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"Judge request failed, retrying in {wait}s...")
            time.sleep(wait)


def run_llm_as_judge(
    results_csv: str | Path,
    *,
    output_csv: str | Path | None = None,
    model: str = DEFAULT_MODEL,
    categories: Iterable[JudgeCategory] = RECOMMENDED_CATEGORIES,
    show_progress: bool = True,
) -> pd.DataFrame:
    df = build_single_model_judge_dataframe(
        results_csv,
        categories=categories,
        show_progress=show_progress,
    )

    scored_rows: list[dict[str, object]] = []
    total = len(df)
    for index, row in enumerate(df.itertuples(index=False), start=1):
        if show_progress:
            print(f"Scoring {index}/{total}: case_id={row.case_id}")

        judge_result = call_openrouter_judge(
            row.judge_prompt,
            model=model,
            categories=categories,
        )

        flat_scores = {
            f"judge_{category.name}": judge_result["scores"].get(category.name)
            for category in categories
        }
        scored_rows.append(
            {
                **row._asdict(),
                "judge_model": model,
                "judge_overall_score": judge_result.get("overall_score"),
                "judge_summary": judge_result.get("summary"),
                **flat_scores,
            }
        )

        if show_progress:
            current_avg = sum(r["judge_overall_score"] for r in scored_rows) / len(scored_rows)
            print(f"Completed {index}/{total} | running overall average: {current_avg:.2f}")

    scored_df = pd.DataFrame(scored_rows)
    if output_csv is None:
        results_path = Path(results_csv)
        output_csv = results_path.with_name(f"{results_path.stem}_judge_scores.csv")
    scored_df.to_csv(output_csv, index=False)
    write_judge_summary_tables(scored_df, output_csv=output_csv, show_progress=show_progress)
    if show_progress:
        print(f"Saved judge scores to {output_csv}")
    return scored_df


def write_judge_summary_tables(
    scored_df: pd.DataFrame,
    *,
    output_csv: str | Path,
    show_progress: bool = True,
) -> tuple[Path, Path]:
    output_path = Path(output_csv)
    prompt_summary_path = output_path.with_name(f"{output_path.stem}_summary_by_prompt.csv")
    mode_summary_path = output_path.with_name(f"{output_path.stem}_summary_by_mode.csv")

    working = scored_df.copy()
    numeric_columns = [
        "judge_overall_score",
        "judge_mathematical_correctness",
        "judge_pedagogical_helpfulness",
        "judge_policy_compliance",
        "judge_clarity",
        "judge_specificity",
        "latency",
    ]
    for column in numeric_columns:
        if column in working.columns:
            working[column] = pd.to_numeric(working[column], errors="coerce")

    working["verdict_correct"] = (
        working["verdict"].astype(str).str.strip().str.lower()
        == working["expected_verdict_meta"].astype(str).str.strip().str.lower()
    )

    prompt_summary = (
        working.groupby("prompt_version", dropna=False)
        .agg(
            cases=("case_id", "count"),
            verdict_accuracy_pct=("verdict_correct", lambda s: round(s.mean() * 100, 1)),
            avg_overall=("judge_overall_score", "mean"),
            avg_math=("judge_mathematical_correctness", "mean"),
            avg_helpfulness=("judge_pedagogical_helpfulness", "mean"),
            avg_policy=("judge_policy_compliance", "mean"),
            avg_clarity=("judge_clarity", "mean"),
            avg_specificity=("judge_specificity", "mean"),
            avg_latency_s=("latency", "mean"),
        )
        .reset_index()
    )

    mode_summary = (
        working.groupby("expected_mode", dropna=False)
        .agg(
            cases=("case_id", "count"),
            verdict_accuracy_pct=("verdict_correct", lambda s: round(s.mean() * 100, 1)),
            avg_overall=("judge_overall_score", "mean"),
            avg_math=("judge_mathematical_correctness", "mean"),
            avg_helpfulness=("judge_pedagogical_helpfulness", "mean"),
            avg_policy=("judge_policy_compliance", "mean"),
            avg_clarity=("judge_clarity", "mean"),
            avg_specificity=("judge_specificity", "mean"),
            avg_latency_s=("latency", "mean"),
        )
        .reset_index()
        .rename(columns={"expected_mode": "mode"})
    )

    round_columns = [
        "avg_overall",
        "avg_math",
        "avg_helpfulness",
        "avg_policy",
        "avg_clarity",
        "avg_specificity",
        "avg_latency_s",
    ]
    for df in (prompt_summary, mode_summary):
        for column in round_columns:
            if column in df.columns:
                df[column] = df[column].round(2)

    prompt_summary.to_csv(prompt_summary_path, index=False)
    mode_summary.to_csv(mode_summary_path, index=False)

    if show_progress:
        print(f"Saved prompt summary to {prompt_summary_path}")
        print(f"Saved mode summary to {mode_summary_path}")

    return prompt_summary_path, mode_summary_path


if __name__ == "__main__":
    df = run_llm_as_judge(ROOT / "results_flash_med_v6.csv", show_progress=True)
    print(df[["case_id", "prompt_version", "judge_overall_score"]].head())
