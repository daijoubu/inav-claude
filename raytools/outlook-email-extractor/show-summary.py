#!/usr/bin/env python3
"""
Quick script to show category summary from categorized timeline
"""
import json

# Load categorized timeline
with open('categorized-timeline.json', 'r') as f:
    data = json.load(f)

categorized_entries = data['categorized_timeline']

# Calculate category hours
category_hours = {}
total_hours = 0

for entry in categorized_entries:
    cat = entry['category']
    hours = entry.get('duration_hours', 0)
    category_hours[cat] = category_hours.get(cat, 0) + hours
    total_hours += hours

# Print tab-separated summary
for cat in sorted(category_hours.keys(), key=lambda x: category_hours[x], reverse=True):
    hours = category_hours[cat]
    percentage = (hours / total_hours * 100) if total_hours > 0 else 0
    print(f'{cat}\t{percentage:.1f}\t{hours:.2f}')
