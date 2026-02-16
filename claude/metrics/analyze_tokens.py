#!/usr/bin/env python3
"""
Analyze token usage from CSV and generate summary report.
"""

import csv
from collections import defaultdict
from datetime import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, "token-usage.csv")
SUMMARY_FILE = os.path.join(SCRIPT_DIR, "summary.md")


def load_data():
    """Load token usage data from CSV."""
    records = []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['total_tokens'] = int(row['total_tokens'])
            row['tool_uses'] = int(row['tool_uses'])
            row['duration_ms'] = int(row['duration_ms'])
            records.append(row)
    return records


def analyze(records):
    """Aggregate statistics by agent/skill."""
    stats = defaultdict(lambda: {
        'count': 0,
        'total_tokens': 0,
        'total_tool_uses': 0,
        'total_duration_ms': 0,
        'tasks': []
    })

    for r in records:
        agent = r['agent_or_skill']
        stats[agent]['count'] += 1
        stats[agent]['total_tokens'] += r['total_tokens']
        stats[agent]['total_tool_uses'] += r['tool_uses']
        stats[agent]['total_duration_ms'] += r['duration_ms']
        stats[agent]['tasks'].append(r['task_description'])

    # Calculate averages
    for agent, data in stats.items():
        data['avg_tokens'] = data['total_tokens'] / data['count']
        data['avg_tool_uses'] = data['total_tool_uses'] / data['count']
        data['avg_duration_ms'] = data['total_duration_ms'] / data['count']

    return dict(stats)


def generate_summary(stats, records):
    """Generate markdown summary report."""
    total_tokens = sum(r['total_tokens'] for r in records)
    total_invocations = len(records)

    # Sort by total tokens (descending)
    sorted_agents = sorted(stats.items(), key=lambda x: x[1]['total_tokens'], reverse=True)

    lines = [
        "# Token Usage Summary",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total Records:** {total_invocations}",
        f"**Total Tokens:** {total_tokens:,}",
        "",
        "---",
        "",
        "## By Agent/Skill (Sorted by Total Tokens)",
        "",
        "| Agent/Skill | Invocations | Total Tokens | Avg Tokens | Avg Duration |",
        "|-------------|-------------|--------------|------------|--------------|",
    ]

    for agent, data in sorted_agents:
        lines.append(
            f"| {agent} | {data['count']} | {data['total_tokens']:,} | "
            f"{data['avg_tokens']:,.0f} | {data['avg_duration_ms']/1000:.1f}s |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Token Distribution",
        "",
    ])

    for agent, data in sorted_agents:
        pct = (data['total_tokens'] / total_tokens) * 100
        bar = "#" * int(pct / 2)
        lines.append(f"**{agent}:** {pct:.1f}% {bar}")

    lines.extend([
        "",
        "---",
        "",
        "## Recommendations",
        "",
    ])

    # Find highest token consumers
    if sorted_agents:
        top_agent = sorted_agents[0][0]
        top_tokens = sorted_agents[0][1]['avg_tokens']
        lines.append(f"- **Highest consumer:** `{top_agent}` averaging {top_tokens:,.0f} tokens/invocation")

        if top_tokens > 20000:
            lines.append(f"  - Consider breaking into smaller tasks or using more targeted prompts")

    return "\n".join(lines)


def main():
    records = load_data()
    stats = analyze(records)
    summary = generate_summary(stats, records)

    with open(SUMMARY_FILE, 'w') as f:
        f.write(summary)

    print(f"Summary written to {SUMMARY_FILE}")
    print(f"\nQuick stats:")
    print(f"  Total invocations: {len(records)}")
    print(f"  Total tokens: {sum(r['total_tokens'] for r in records):,}")

    print(f"\nTop consumers:")
    sorted_agents = sorted(stats.items(), key=lambda x: x[1]['total_tokens'], reverse=True)
    for agent, data in sorted_agents[:5]:
        print(f"  {agent}: {data['total_tokens']:,} tokens ({data['count']} invocations)")


if __name__ == "__main__":
    main()
