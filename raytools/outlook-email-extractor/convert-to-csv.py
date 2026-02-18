#!/usr/bin/env python3
"""
Convert Outlook Email Extraction JSON to CSV

Usage:
    python convert-to-csv.py input.json output.csv

Or paste JSON data directly when prompted.
"""

import json
import csv
import sys
from pathlib import Path


def convert_json_to_csv(json_data, output_file):
    """Convert email extraction JSON to CSV format."""

    # Handle both direct data and wrapped format
    if isinstance(json_data, dict) and 'emails' in json_data:
        emails = json_data['emails']
    else:
        emails = json_data

    if not emails:
        print("No emails found in JSON data")
        return

    # CSV columns
    fieldnames = [
        'Index',
        'Subject',
        'Timestamp',
        'To (Count)',
        'To (Addresses)',
        'Body Preview',
        'Word Count'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for email in emails:
            # Join multiple To addresses with semicolon
            to_addresses = '; '.join(email.get('toAddresses', []))

            writer.writerow({
                'Index': email.get('index', ''),
                'Subject': email.get('subject', ''),
                'Timestamp': email.get('timestamp', ''),
                'To (Count)': email.get('toCount', 0),
                'To (Addresses)': to_addresses,
                'Body Preview': email.get('bodyPreview', ''),
                'Word Count': email.get('bodyWordCount', 0)
            })

    print(f"✓ Converted {len(emails)} emails to CSV: {output_file}")


def main():
    if len(sys.argv) == 3:
        # File input mode
        input_file = sys.argv[1]
        output_file = sys.argv[2]

        if not Path(input_file).exists():
            print(f"Error: Input file not found: {input_file}")
            sys.exit(1)

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        convert_json_to_csv(data, output_file)

    elif len(sys.argv) == 1:
        # Interactive mode - paste JSON
        print("Outlook Email JSON to CSV Converter")
        print("=" * 60)
        print("\nPaste your JSON data below (Ctrl+D when done):")
        print()

        json_text = sys.stdin.read()

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON - {e}")
            sys.exit(1)

        output_file = input("\nEnter output CSV filename (e.g., emails.csv): ").strip()
        if not output_file:
            output_file = "outlook-emails.csv"

        convert_json_to_csv(data, output_file)

    else:
        print("Usage:")
        print("  python convert-to-csv.py input.json output.csv")
        print("  OR")
        print("  python convert-to-csv.py   (then paste JSON)")
        sys.exit(1)


if __name__ == '__main__':
    main()
