#!/usr/bin/env python3
"""
Convert Calendar Events JSON to CSV

Converts calendar event extraction results to CSV format.

Usage:
    python convert-calendar-to-csv.py calendar-events.json events.csv
    python convert-calendar-to-csv.py  # Interactive mode - paste JSON
"""

import json
import csv
import sys


def convert_json_to_csv(json_data, output_file):
    """Convert calendar JSON to CSV format"""

    # Handle both full output format and just events array
    events = json_data['events'] if 'events' in json_data else json_data

    # Define CSV columns
    fieldnames = [
        'Day',
        'Date',
        'Time',
        'Title',
        'Location',
        'Status',
        'Recurring',
        'Canceled',
        'All Day'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for event in events:
            row = {
                'Day': event.get('day_of_week', ''),
                'Date': event.get('date', ''),
                'Time': event.get('time', ''),
                'Title': event.get('title', ''),
                'Location': event.get('location', ''),
                'Status': event.get('status', ''),
                'Recurring': 'Yes' if event.get('is_recurring', False) else 'No',
                'Canceled': 'Yes' if event.get('is_canceled', False) else 'No',
                'All Day': 'Yes' if event.get('all_day', False) else 'No'
            }
            writer.writerow(row)

    print(f"✓ Converted {len(events)} events to {output_file}")


def main():
    if len(sys.argv) == 3:
        # File mode
        input_file = sys.argv[1]
        output_file = sys.argv[2]

        print(f"Reading from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        convert_json_to_csv(json_data, output_file)

    elif len(sys.argv) == 1:
        # Interactive mode
        print("Paste the JSON data (press Enter, then Ctrl+D when done):")
        json_text = sys.stdin.read()

        json_data = json.loads(json_text)

        output_file = input("Enter output CSV filename (e.g., events.csv): ")
        convert_json_to_csv(json_data, output_file)

    else:
        print("Usage:")
        print("  python convert-calendar-to-csv.py calendar-events.json events.csv")
        print("  python convert-calendar-to-csv.py  # Interactive mode")
        sys.exit(1)


if __name__ == '__main__':
    main()
