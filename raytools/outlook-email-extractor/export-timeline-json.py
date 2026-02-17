#!/usr/bin/env python3
"""
Export Complete Timeline as JSON

Creates a chronological JSON export of all email, calendar, and Teams data
with complete message bodies and event details.

Usage:
    python export-timeline-json.py
    python export-timeline-json.py --output timeline-2026-01-31.json
    python export-timeline-json.py --week "2026-01-24"  # Specify target week start date
"""

import json
import sys
import csv
import argparse
from datetime import datetime, timedelta
from collections import defaultdict


def parse_calendar_events(calendar_file):
    """Parse calendar events with full details"""
    with open(calendar_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    events = []
    for event in data.get('events', []):
        # Parse date and time
        date_str = event.get('date', '')
        time_str = event.get('time', '')

        # Create a sortable datetime for this event
        dt = parse_event_datetime(date_str, time_str)

        entry = {
            'type': 'calendar_event',
            'datetime': dt.isoformat() if dt else None,
            'timestamp': dt.timestamp() if dt else None,
            'date': date_str,
            'day_of_week': event.get('day_of_week', ''),
            'time': time_str,
            'title': event.get('title', ''),
            'location': event.get('location', ''),
            'description': event.get('description', ''),
            'organizer': event.get('organizer', ''),
            'status': event.get('status', ''),
            'is_canceled': event.get('is_canceled', False),
            'is_recurring': event.get('is_recurring', False),
            'all_day': event.get('all_day', False)
        }

        events.append(entry)

    return events


def parse_event_datetime(date_str, time_str):
    """Parse calendar event date and time into datetime object"""
    if not date_str:
        return None

    try:
        # Parse date: "Monday, January 26, 2026"
        date_part = datetime.strptime(date_str, '%A, %B %d, %Y')

        # Parse time if available and not all-day
        if time_str and time_str != 'All day' and ' - ' in time_str:
            # Get start time: "10:00 AM - 10:30 AM"
            start_time_str = time_str.split(' - ')[0].strip()
            time_part = datetime.strptime(start_time_str, '%I:%M %p')

            # Combine date and time
            return datetime.combine(date_part.date(), time_part.time())
        else:
            # All-day or no time - use start of day
            return datetime.combine(date_part.date(), datetime.min.time())

    except ValueError as e:
        print(f"Warning: Could not parse date/time '{date_str}' / '{time_str}': {e}")
        return None


def parse_emails(email_file):
    """Parse sent emails with full details"""
    with open(email_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    emails = []
    for email in data.get('emails', []):
        timestamp_str = email.get('timestamp', '')

        # Parse timestamp
        dt = parse_email_datetime(timestamp_str)

        entry = {
            'type': 'email_sent',
            'datetime': dt.isoformat() if dt else None,
            'timestamp': dt.timestamp() if dt else None,
            'timestamp_raw': timestamp_str,
            'subject': email.get('subject', ''),
            'to_addresses': email.get('toAddresses', []),
            'to_count': email.get('toCount', 0),
            'body_preview': email.get('bodyPreview', ''),
            'body_word_count': email.get('bodyWordCount', 0)
        }

        emails.append(entry)

    return emails


def parse_email_datetime(timestamp_str):
    """Parse email timestamp into datetime object"""
    if not timestamp_str or timestamp_str == 'Unknown':
        return None

    # Format: "12/18/2025"
    if '/' in timestamp_str and len(timestamp_str.split('/')) == 3:
        try:
            return datetime.strptime(timestamp_str, '%m/%d/%Y')
        except ValueError:
            pass

    # Format: "Fri 4:58 PM", "Wed 12:06 PM"
    # These are relative - would need week context to convert to absolute datetime
    # For now, we'll estimate based on day abbreviation and time
    if ' ' in timestamp_str and ('AM' in timestamp_str or 'PM' in timestamp_str):
        parts = timestamp_str.split()
        if len(parts) >= 2:
            day_abbrev = parts[0]
            time_str = ' '.join(parts[1:])

            # Map to day of week (0 = Monday)
            day_map = {
                'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3,
                'Fri': 4, 'Sat': 5, 'Sun': 6
            }

            if day_abbrev in day_map:
                # Parse time
                try:
                    time_part = datetime.strptime(time_str, '%I:%M %p').time()

                    # Estimate date based on current week
                    # This is approximate - would need actual week context
                    today = datetime.now()
                    days_diff = day_map[day_abbrev] - today.weekday()
                    target_date = today + timedelta(days=days_diff)

                    return datetime.combine(target_date.date(), time_part)
                except ValueError:
                    pass

    return None


def parse_teams_messages(teams_file):
    """Parse Teams messages with full details"""
    if not teams_file:
        return []

    try:
        with open(teams_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            messages = []

            for row in reader:
                sent_on = row.get('SentOn', '')

                # Parse timestamp
                dt = parse_teams_datetime(sent_on)

                entry = {
                    'type': 'teams_message',
                    'datetime': dt.isoformat() if dt else None,
                    'timestamp': dt.timestamp() if dt else None,
                    'timestamp_raw': sent_on,
                    'where': row.get('Where', ''),
                    'participants': row.get('Subject', ''),
                    'body': row.get('BodyPreview', ''),
                    'message_id': row.get('Id', '')
                }

                messages.append(entry)

            return messages

    except FileNotFoundError:
        print(f"Warning: Teams file not found: {teams_file}")
        return []


def parse_teams_datetime(timestamp_str):
    """Parse Teams timestamp: '12/5/2025 22:55' or '1/26/2026 15:30'"""
    if not timestamp_str:
        return None

    try:
        # Format: "12/5/2025 22:55" or "1/26/2026 15:30"
        return datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M')
    except ValueError:
        try:
            # Try alternative format with 12-hour time
            return datetime.strptime(timestamp_str, '%m/%d/%Y %I:%M %p')
        except ValueError:
            return None


def build_chronological_timeline(calendar_events, emails, teams_messages):
    """Build a chronological timeline sorted by timestamp"""
    all_entries = []

    # Add all entries to a single list
    all_entries.extend(calendar_events)
    all_entries.extend(emails)
    all_entries.extend(teams_messages)

    # Filter out entries without timestamps
    valid_entries = [e for e in all_entries if e.get('timestamp') is not None]

    # Sort by timestamp
    valid_entries.sort(key=lambda e: e['timestamp'])

    return valid_entries


def calculate_week_range(start_date_str=None):
    """Calculate week range (Saturday to Friday)"""
    if start_date_str:
        # Use provided start date
        start = datetime.strptime(start_date_str, '%Y-%m-%d')
    else:
        # Use default logic: 3 days ago -> Saturday before -> Sat-Fri
        today = datetime.now()
        three_days_ago = today - timedelta(days=3)

        # Find most recent Saturday before that date
        day_of_week = three_days_ago.weekday()  # 0=Mon, 6=Sun
        days_since_saturday = (day_of_week + 2) % 7
        if days_since_saturday == 0:
            days_since_saturday = 7

        start = three_days_ago - timedelta(days=days_since_saturday)

    end = start + timedelta(days=6)
    return start, end


def filter_by_week(entries, start_date, end_date):
    """Filter entries to only include those within the week range"""
    filtered = []

    start_timestamp = start_date.timestamp()
    end_timestamp = end_date.replace(hour=23, minute=59, second=59).timestamp()

    for entry in entries:
        ts = entry.get('timestamp')
        if ts and start_timestamp <= ts <= end_timestamp:
            filtered.append(entry)

    return filtered


def export_to_json(timeline, output_file, week_start, week_end, metadata):
    """Export timeline to JSON file"""
    output = {
        'export_date': datetime.now().isoformat(),
        'week_range': {
            'start': week_start.strftime('%Y-%m-%d'),
            'end': week_end.strftime('%Y-%m-%d'),
            'description': f"{week_start.strftime('%A, %B %d, %Y')} - {week_end.strftime('%A, %B %d, %Y')}"
        },
        'summary': {
            'total_entries': len(timeline),
            'calendar_events': sum(1 for e in timeline if e['type'] == 'calendar_event'),
            'emails_sent': sum(1 for e in timeline if e['type'] == 'email_sent'),
            'teams_messages': sum(1 for e in timeline if e['type'] == 'teams_message')
        },
        'metadata': metadata,
        'timeline': timeline
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output


def main():
    parser = argparse.ArgumentParser(description='Export timeline to JSON')
    parser.add_argument('--output', '-o', default=None, help='Output JSON file')
    parser.add_argument('--week', '-w', default=None, help='Week start date (YYYY-MM-DD)')
    parser.add_argument('--calendar', default='data/2025-01-31/calendar-events-2026-01-31.json', help='Calendar JSON file')
    parser.add_argument('--email', default='data/2025-01-31/extraction-results-2026-01-31.json', help='Email JSON file')
    parser.add_argument('--teams', default='data/2025-01-31/Teams_Sent.csv', help='Teams CSV file')

    args = parser.parse_args()

    # Calculate week range
    week_start, week_end = calculate_week_range(args.week)

    print(f"Exporting timeline for week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
    print()

    # Parse data sources
    print("Loading data...")
    calendar_events = parse_calendar_events(args.calendar)
    emails = parse_emails(args.email)
    teams_messages = parse_teams_messages(args.teams)

    print(f"  Loaded {len(calendar_events)} calendar events")
    print(f"  Loaded {len(emails)} emails")
    print(f"  Loaded {len(teams_messages)} Teams messages")
    print()

    # Build chronological timeline
    print("Building chronological timeline...")
    timeline = build_chronological_timeline(calendar_events, emails, teams_messages)

    # Filter by week
    timeline = filter_by_week(timeline, week_start, week_end)

    print(f"  Timeline has {len(timeline)} entries in target week")
    print()

    # Generate output filename if not specified
    if not args.output:
        args.output = f"timeline-{datetime.now().strftime('%Y-%m-%d')}.json"

    # Export to JSON
    metadata = {
        'sources': {
            'calendar': args.calendar,
            'email': args.email,
            'teams': args.teams
        }
    }

    result = export_to_json(timeline, args.output, week_start, week_end, metadata)

    print(f"✓ Exported timeline to {args.output}")
    print()
    print("Summary:")
    print(f"  Total entries: {result['summary']['total_entries']}")
    print(f"  Calendar events: {result['summary']['calendar_events']}")
    print(f"  Emails sent: {result['summary']['emails_sent']}")
    print(f"  Teams messages: {result['summary']['teams_messages']}")
    print()
    print(f"Week: {result['week_range']['description']}")


if __name__ == '__main__':
    main()
