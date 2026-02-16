# Token Usage Metrics

Track token consumption by agent and skill to identify optimization opportunities.

## Files

- `token-usage.csv` - Raw usage data
- `summary.md` - Aggregated statistics (updated periodically)

## Data Format

| Column | Description |
|--------|-------------|
| timestamp | ISO 8601 timestamp |
| agent_or_skill | Agent type or skill name |
| total_tokens | Total tokens consumed |
| tool_uses | Number of tool invocations |
| duration_ms | Execution time in milliseconds |
| task_description | Brief description of task |

## How to Log

After each agent/skill invocation, the usage block contains:
```
<usage>total_tokens: XXXXX
tool_uses: X
duration_ms: XXXXX</usage>
```

Add a row to `token-usage.csv` with this data.

## Analysis

Run the analysis script to generate summary:
```bash
python3 claude/metrics/analyze_tokens.py
```
