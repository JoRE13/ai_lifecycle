# Langfuse Observability Summary

- Source CSV: `langfuse_observations_export.csv`
- Observation rows: 76
- SPAN calls: 37
- GENERATION calls: 37
- Server error events: 2

## Latency

- Reporting basis: SPAN.latency (seconds)
- Average latency: 24.823 s
- P95 latency: 87.697 s

## Token Usage

- Input tokens (sum): 136816
- Output tokens (sum): 4710
- Thought tokens (sum): 77136
- Billed output tokens (output + thought): 81846
- Total tokens (sum): 218662
- Token accounting delta (should be 0): 0
- Average total tokens per interaction: 5909.784

## Cost

- Logged cost total (from export): $0.000000
- Estimated total cost (using configured rates): $0.313946
- Estimated cost per interaction: $0.008485
- Input rate used: $0.500000 per 1M tokens
- Output rate used: $3.000000 per 1M tokens

## Mode Split

- {"check_solution": 16, "reveal": 3, "hint": 18}

## Note

- If logged_total_cost_usd_sum is 0, Langfuse pricing tiers were not configured. Estimated output cost uses billed_output_tokens_sum = output_tokens_sum + thought_tokens_sum.