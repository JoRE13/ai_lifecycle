import argparse
import csv
import json
import math
from pathlib import Path


def dequote(value: str | None) -> str:
    s = "" if value is None else str(value).strip()
    while len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    return s


def to_float(value: str | None) -> float | None:
    s = dequote(value)
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return xs[int(k)]
    return xs[f] * (c - k) + xs[c] * (k - f)


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [{k: dequote(v) for k, v in row.items()} for row in reader]


def parse_mode_from_metadata(metadata: str) -> str:
    if not metadata:
        return ""
    try:
        obj = json.loads(metadata)
    except json.JSONDecodeError:
        return ""
    mode = obj.get("mode", "") if isinstance(obj, dict) else ""
    return str(mode)


def parse_latency_from_metadata(metadata: str) -> float | None:
    if not metadata:
        return None
    try:
        obj = json.loads(metadata)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    lat = obj.get("latency")
    try:
        return float(lat) if lat is not None else None
    except (TypeError, ValueError):
        return None


def parse_thought_tokens_from_metadata(metadata: str) -> float | None:
    if not metadata:
        return None
    try:
        obj = json.loads(metadata)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    thoughts = obj.get("thought_tokens")
    try:
        return float(thoughts) if thoughts is not None else None
    except (TypeError, ValueError):
        return None


def safe_mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def fmt(value: float | int | None, digits: int = 3) -> str:
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    return f"{value:.{digits}f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute observability metrics from Langfuse observations export")
    parser.add_argument("--csv", required=True, help="Path to observations CSV export")
    parser.add_argument("--out-csv", required=True, help="Path for summary CSV output")
    parser.add_argument("--out-md", required=True, help="Path for markdown summary output")
    parser.add_argument("--input-rate-per-1m", type=float, default=0.0, help="USD per 1M input tokens")
    parser.add_argument("--output-rate-per-1m", type=float, default=0.0, help="USD per 1M output tokens")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    rows = load_rows(csv_path)

    spans = [r for r in rows if r.get("type") == "SPAN" and r.get("name") == "gemini-call"]
    gens = [r for r in rows if r.get("type") == "GENERATION" and r.get("name") == "gemini-generation"]
    events = [r for r in rows if r.get("type") == "EVENT"]
    server_errors = [r for r in rows if r.get("type") == "EVENT" and r.get("name") == "server_error"]

    span_latency = [to_float(r.get("latency")) for r in spans]
    span_latency = [x for x in span_latency if x is not None]

    gen_metadata_latency = [parse_latency_from_metadata(r.get("metadata", "")) for r in gens]
    gen_metadata_latency = [x for x in gen_metadata_latency if x is not None]
    thought_tokens = [parse_thought_tokens_from_metadata(r.get("metadata", "")) for r in gens]
    thought_tokens = [x for x in thought_tokens if x is not None]

    input_usage = [to_float(r.get("inputUsage")) for r in gens]
    output_usage = [to_float(r.get("outputUsage")) for r in gens]
    total_usage = [to_float(r.get("totalUsage")) for r in gens]

    input_usage = [x for x in input_usage if x is not None]
    output_usage = [x for x in output_usage if x is not None]
    total_usage = [x for x in total_usage if x is not None]

    logged_total_cost = [to_float(r.get("totalCost")) for r in gens]
    logged_total_cost = [x for x in logged_total_cost if x is not None]

    sum_input = int(sum(input_usage)) if input_usage else 0
    sum_output = int(sum(output_usage)) if output_usage else 0
    sum_total = int(sum(total_usage)) if total_usage else 0
    sum_thought = int(sum(thought_tokens)) if thought_tokens else max(0, sum_total - (sum_input + sum_output))
    output_plus_thought = sum_output + sum_thought
    token_accounting_delta = sum_total - (sum_input + sum_output + sum_thought)

    mode_counts: dict[str, int] = {}
    for r in gens:
        mode = parse_mode_from_metadata(r.get("metadata", "")) or "unknown"
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

    # For Gemini 3 Flash Preview paid tier, output pricing includes thought tokens.
    est_total_cost = (sum_input / 1_000_000.0) * args.input_rate_per_1m + (output_plus_thought / 1_000_000.0) * args.output_rate_per_1m
    est_cost_per_call = est_total_cost / len(gens) if gens else 0.0

    summary = {
        "source_csv": str(csv_path),
        "observation_rows": len(rows),
        "span_calls": len(spans),
        "generation_calls": len(gens),
        "event_rows": len(events),
        "server_error_events": len(server_errors),
        "latency_source_for_reporting": "SPAN.latency (seconds)",
        "latency_avg_sec": safe_mean(span_latency),
        "latency_p95_sec": percentile(span_latency, 95),
        "generation_metadata_latency_avg_sec": safe_mean(gen_metadata_latency),
        "generation_metadata_latency_p95_sec": percentile(gen_metadata_latency, 95),
        "input_tokens_sum": sum_input,
        "output_tokens_sum": sum_output,
        "thought_tokens_sum": sum_thought,
        "billed_output_tokens_sum": output_plus_thought,
        "token_accounting_delta": token_accounting_delta,
        "total_tokens_sum": sum_total,
        "tokens_per_call_avg": (sum_total / len(gens)) if gens else None,
        "logged_total_cost_usd_sum": sum(logged_total_cost) if logged_total_cost else 0.0,
        "input_rate_per_1m_usd": args.input_rate_per_1m,
        "output_rate_per_1m_usd": args.output_rate_per_1m,
        "estimated_total_cost_usd": est_total_cost,
        "estimated_cost_per_interaction_usd": est_cost_per_call,
        "mode_counts": json.dumps(mode_counts, ensure_ascii=True),
        "notes": "If logged_total_cost_usd_sum is 0, Langfuse pricing tiers were not configured. Estimated output cost uses billed_output_tokens_sum = output_tokens_sum + thought_tokens_sum.",
    }

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)

    out_md = Path(args.out_md)
    lines = [
        "# Langfuse Observability Summary",
        "",
        f"- Source CSV: `{csv_path.name}`",
        f"- Observation rows: {summary['observation_rows']}",
        f"- SPAN calls: {summary['span_calls']}",
        f"- GENERATION calls: {summary['generation_calls']}",
        f"- Server error events: {summary['server_error_events']}",
        "",
        "## Latency",
        "",
        f"- Reporting basis: {summary['latency_source_for_reporting']}",
        f"- Average latency: {fmt(summary['latency_avg_sec'])} s",
        f"- P95 latency: {fmt(summary['latency_p95_sec'])} s",
        "",
        "## Token Usage",
        "",
        f"- Input tokens (sum): {summary['input_tokens_sum']}",
        f"- Output tokens (sum): {summary['output_tokens_sum']}",
        f"- Thought tokens (sum): {summary['thought_tokens_sum']}",
        f"- Billed output tokens (output + thought): {summary['billed_output_tokens_sum']}",
        f"- Total tokens (sum): {summary['total_tokens_sum']}",
        f"- Token accounting delta (should be 0): {summary['token_accounting_delta']}",
        f"- Average total tokens per interaction: {fmt(summary['tokens_per_call_avg'])}",
        "",
        "## Cost",
        "",
        f"- Logged cost total (from export): ${fmt(summary['logged_total_cost_usd_sum'], 6)}",
        f"- Estimated total cost (using configured rates): ${fmt(summary['estimated_total_cost_usd'], 6)}",
        f"- Estimated cost per interaction: ${fmt(summary['estimated_cost_per_interaction_usd'], 6)}",
        f"- Input rate used: ${fmt(summary['input_rate_per_1m_usd'], 6)} per 1M tokens",
        f"- Output rate used: ${fmt(summary['output_rate_per_1m_usd'], 6)} per 1M tokens",
        "",
        "## Mode Split",
        "",
        f"- {summary['mode_counts']}",
        "",
        "## Note",
        "",
        f"- {summary['notes']}",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote: {out_csv}")
    print(f"Wrote: {out_md}")


if __name__ == "__main__":
    main()
