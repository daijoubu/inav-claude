#!/usr/bin/env python3
"""
Build Weekly Timeline from Email and Calendar Data

Combines email and calendar data to create a chronological timeline
that can answer questions like "what was I doing around 3:14 PM on Wednesday?"

Usage:
    python build-timeline.py
    python build-timeline.py --query "Wednesday 3:14 PM"
"""

import json
import sys
import csv
from datetime import datetime, timedelta
from collections import defaultdict


def parse_calendar_events(calendar_file):
    """Parse calendar events into timeline entries"""
    with open(calendar_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    events = []
    for event in data.get('events', []):
        # Parse date and time
        date_str = event.get('date', '')
        time_str = event.get('time', '')

        entry = {
            'type': 'calendar',
            'title': event.get('title', ''),
            'date': date_str,
            'time': time_str,
            'location': event.get('location', ''),
            'day_of_week': event.get('day_of_week', ''),
            'is_canceled': event.get('is_canceled', False),
            'is_recurring': event.get('is_recurring', False),
            'all_day': event.get('all_day', False),
            'raw_event': event
        }

        # Parse start/end times for querying
        if ' - ' in time_str:
            start_str, end_str = time_str.split(' - ', 1)
            entry['start_time'] = start_str.strip()
            entry['end_time'] = end_str.strip()
        elif time_str == 'All day':
            entry['start_time'] = '12:00 AM'
            entry['end_time'] = '11:59 PM'
        else:
            entry['start_time'] = time_str
            entry['end_time'] = time_str

        events.append(entry)

    return events


def parse_emails(email_file):
    """Parse sent emails into timeline entries"""
    with open(email_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    emails = []
    for email in data.get('emails', []):
        timestamp = email.get('timestamp', '')

        entry = {
            'type': 'email',
            'title': f"Email: {email.get('subject', 'No subject')}",
            'timestamp': timestamp,
            'to_addresses': email.get('toAddresses', []),
            'subject': email.get('subject', ''),
            'body_preview': email.get('bodyPreview', ''),
            'raw_email': email
        }

        # Try to parse timestamp
        # Formats: "12/18/2025", "Fri 4:58 PM", "Wed 12:06 PM", "Unknown"
        entry['parsed_date'] = parse_email_timestamp(timestamp)

        emails.append(entry)

    return emails


def parse_teams_messages(teams_file):
    """Parse Teams messages from CSV file into timeline entries"""
    if not teams_file:
        return []

    try:
        with open(teams_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            reader = csv.DictReader(f)
            messages = []

            for row in reader:
                sent_on = row.get('SentOn', '')
                where = row.get('Where', '')
                subject = row.get('Subject', '')
                body_preview = row.get('BodyPreview', '')

                entry = {
                    'type': 'teams',
                    'title': f"Teams: {subject}",
                    'timestamp': sent_on,
                    'where': where,
                    'subject': subject,
                    'body_preview': body_preview,
                    'raw_message': row
                }

                # Parse timestamp: "12/5/2025 22:55" or "1/26/2026 15:30"
                entry['parsed_date'] = parse_teams_timestamp(sent_on)

                messages.append(entry)

            return messages

    except FileNotFoundError:
        print(f"Warning: Teams file not found: {teams_file}")
        return []


def parse_teams_timestamp(timestamp_str):
    """Parse Teams timestamp format: '12/5/2025 22:55' or '1/26/2026 15:30'"""
    if not timestamp_str:
        return None

    try:
        # Format: "12/5/2025 22:55" or "1/26/2026 15:30"
        dt = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M')
        return dt
    except ValueError:
        try:
            # Try alternative format with 12-hour time
            dt = datetime.strptime(timestamp_str, '%m/%d/%Y %I:%M %p')
            return dt
        except ValueError:
            return None


def parse_email_timestamp(timestamp_str):
    """Parse various email timestamp formats"""
    if not timestamp_str or timestamp_str == 'Unknown':
        return None

    # Format: "12/18/2025"
    if '/' in timestamp_str and len(timestamp_str) > 8:
        try:
            return datetime.strptime(timestamp_str, '%m/%d/%Y')
        except ValueError:
            pass

    # Format: "Fri 4:58 PM", "Wed 12:06 PM"
    # These are relative - we'd need to know the week context
    # For now, just extract the time
    parts = timestamp_str.split()
    if len(parts) >= 2 and ('AM' in timestamp_str or 'PM' in timestamp_str):
        return {
            'day_abbrev': parts[0],
            'time': ' '.join(parts[1:])
        }

    return None


def parse_time_query(query):
    """
    Parse time query like "Wednesday 3:14 PM" or "Mon 10:30 AM"

    Returns: (day_of_week, target_time)
    """
    query = query.strip()

    # Map day abbreviations
    day_map = {
        'mon': 'Monday', 'monday': 'Monday',
        'tue': 'Tuesday', 'tues': 'Tuesday', 'tuesday': 'Tuesday',
        'wed': 'Wednesday', 'wednesday': 'Wednesday',
        'thu': 'Thursday', 'thur': 'Thursday', 'thurs': 'Thursday', 'thursday': 'Thursday',
        'fri': 'Friday', 'friday': 'Friday',
        'sat': 'Saturday', 'saturday': 'Saturday',
        'sun': 'Sunday', 'sunday': 'Sunday'
    }

    # Extract day and time
    parts = query.lower().split()
    day_of_week = None
    time_str = None

    for i, part in enumerate(parts):
        if part in day_map:
            day_of_week = day_map[part]
            # Rest is the time
            time_str = ' '.join(parts[i+1:])
            break

    return day_of_week, time_str


def time_to_minutes(time_str):
    """Convert time string like '3:14 PM' to minutes since midnight"""
    try:
        # Parse time
        time_str = time_str.strip().upper()  # Make uppercase for parsing

        # Try different formats
        for fmt in ['%I:%M %p', '%H:%M %p', '%I:%M%p', '%H:%M']:
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.hour * 60 + dt.minute
            except ValueError:
                continue

        return None
    except Exception:
        return None


def is_time_in_range(target_time_str, start_time_str, end_time_str):
    """Check if target time falls within start and end time range"""
    target_min = time_to_minutes(target_time_str)
    start_min = time_to_minutes(start_time_str)
    end_min = time_to_minutes(end_time_str)

    if target_min is None or start_min is None or end_min is None:
        return False

    return start_min <= target_min <= end_min


def build_timeline(calendar_events, emails, teams_messages):
    """Build a chronological timeline organized by day"""
    timeline = defaultdict(list)

    # Add calendar events
    for event in calendar_events:
        day = event['day_of_week']
        if day:
            timeline[day].append(event)

    # Add emails
    for email in emails:
        parsed = email.get('parsed_date')
        if isinstance(parsed, dict) and 'day_abbrev' in parsed:
            # Map day abbreviation to full name
            day_map = {
                'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday',
                'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'
            }
            day = day_map.get(parsed['day_abbrev'])
            if day:
                timeline[day].append(email)

    # Add Teams messages
    for msg in teams_messages:
        parsed = msg.get('parsed_date')
        if isinstance(parsed, datetime):
            day = parsed.strftime('%A')
            timeline[day].append(msg)

    # Sort each day's entries by time
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sorted_timeline = {}

    for day in day_order:
        if day in timeline:
            # Sort by start time
            entries = timeline[day]
            entries.sort(key=lambda e: get_sort_time(e))
            sorted_timeline[day] = entries

    return sorted_timeline


def get_sort_time(entry):
    """Get sorting time for any entry type"""
    if entry['type'] == 'calendar':
        return time_to_minutes(entry.get('start_time', '12:00 PM')) or 0
    elif entry['type'] == 'email':
        parsed = entry.get('parsed_date')
        if isinstance(parsed, dict) and 'time' in parsed:
            return time_to_minutes(parsed['time']) or 0
        return 0
    elif entry['type'] == 'teams':
        parsed = entry.get('parsed_date')
        if isinstance(parsed, datetime):
            return parsed.hour * 60 + parsed.minute
        return 0
    return 0


def query_timeline(timeline, day_of_week, time_str):
    """Find what was happening at a specific time"""
    if day_of_week not in timeline:
        return []

    matching = []
    for entry in timeline[day_of_week]:
        if entry['type'] == 'calendar':
            # Check if time falls within event time range
            if is_time_in_range(time_str, entry.get('start_time', ''), entry.get('end_time', '')):
                matching.append(entry)
        elif entry['type'] == 'email':
            # For emails, check if it's close to the time
            parsed = entry.get('parsed_date')
            if isinstance(parsed, dict) and 'time' in parsed:
                # Check if within 30 minutes
                target_min = time_to_minutes(time_str)
                email_min = time_to_minutes(parsed['time'])
                if target_min and email_min and abs(target_min - email_min) <= 30:
                    matching.append(entry)
        elif entry['type'] == 'teams':
            # For Teams messages, check if it's close to the time (within 30 minutes)
            parsed = entry.get('parsed_date')
            if isinstance(parsed, datetime):
                target_min = time_to_minutes(time_str)
                teams_min = parsed.hour * 60 + parsed.minute
                if target_min and abs(target_min - teams_min) <= 30:
                    matching.append(entry)

    return matching


def print_timeline(timeline):
    """Print the full timeline"""
    print("=" * 100)
    print("WEEKLY TIMELINE")
    print("=" * 100)
    print()

    for day, entries in timeline.items():
        print(f"\n{'=' * 100}")
        print(f"{day.upper()}")
        print('=' * 100)

        for entry in entries:
            if entry['type'] == 'calendar':
                status = ""
                if entry['is_canceled']:
                    status = " [CANCELED]"
                elif entry['is_recurring']:
                    status = " [RECURRING]"

                print(f"\n  {entry['time']}")
                print(f"  📅 {entry['title']}{status}")
                if entry['location']:
                    print(f"     Location: {entry['location']}")

            elif entry['type'] == 'email':
                parsed = entry.get('parsed_date')
                time_info = parsed.get('time', 'Unknown time') if isinstance(parsed, dict) else 'Unknown time'
                print(f"\n  {time_info}")
                print(f"  ✉️  Sent: {entry['subject']}")
                to_list = ', '.join(entry['to_addresses'][:3])
                if len(entry['to_addresses']) > 3:
                    to_list += f" (and {len(entry['to_addresses']) - 3} more)"
                print(f"     To: {to_list}")

            elif entry['type'] == 'teams':
                parsed = entry.get('parsed_date')
                if isinstance(parsed, datetime):
                    time_info = parsed.strftime('%I:%M %p')
                else:
                    time_info = 'Unknown time'
                print(f"\n  {time_info}")
                print(f"  💬 Teams: {entry['subject']}")
                print(f"     {entry['where']}")
                if entry['body_preview']:
                    preview = entry['body_preview'][:80]
                    print(f"     \"{preview}...\"")

        print()


def print_query_results(results, day, time):
    """Print results of a time query"""
    print("=" * 100)
    print(f"WHAT WAS HAPPENING: {day} at {time}")
    print("=" * 100)
    print()

    if not results:
        print(f"No events or emails found for {day} at {time}")
        return

    for entry in results:
        if entry['type'] == 'calendar':
            status = ""
            if entry['is_canceled']:
                status = " [CANCELED]"

            print(f"📅 Calendar Event: {entry['title']}{status}")
            print(f"   Time: {entry['time']}")
            if entry['location']:
                print(f"   Location: {entry['location']}")
            print()

        elif entry['type'] == 'email':
            print(f"✉️  Sent Email: {entry['subject']}")
            parsed = entry.get('parsed_date')
            if isinstance(parsed, dict) and 'time' in parsed:
                print(f"   Time: {parsed['time']}")
            to_list = ', '.join(entry['to_addresses'][:2])
            if len(entry['to_addresses']) > 2:
                to_list += f" (and {len(entry['to_addresses']) - 2} more)"
            print(f"   To: {to_list}")
            if entry['body_preview']:
                preview = entry['body_preview'][:100]
                print(f"   Preview: {preview}...")
            print()

        elif entry['type'] == 'teams':
            print(f"💬 Teams Message: {entry['subject']}")
            parsed = entry.get('parsed_date')
            if isinstance(parsed, datetime):
                print(f"   Time: {parsed.strftime('%I:%M %p')}")
            print(f"   {entry['where']}")
            if entry['body_preview']:
                preview = entry['body_preview'][:100]
                print(f"   \"{preview}...\"")
            print()


def main():
    # File paths
    calendar_file = 'data/2025-01-31/calendar-events-2026-01-31.json'
    email_file = 'data/2025-01-31/extraction-results-2026-01-31.json'
    teams_file = 'data/2025-01-31/Teams_Sent.csv'  # User will update this

    # Parse data
    print("Loading data...")
    calendar_events = parse_calendar_events(calendar_file)
    emails = parse_emails(email_file)
    teams_messages = parse_teams_messages(teams_file)

    print(f"  Loaded {len(calendar_events)} calendar events")
    print(f"  Loaded {len(emails)} emails")
    print(f"  Loaded {len(teams_messages)} Teams messages")
    print()

    # Build timeline
    timeline = build_timeline(calendar_events, emails, teams_messages)

    # Check for query
    if len(sys.argv) > 1 and sys.argv[1] == '--query':
        # Query mode
        query = ' '.join(sys.argv[2:])
        day, time = parse_time_query(query)

        if not day or not time:
            print(f"Error: Could not parse query '{query}'")
            print("Format: 'Wednesday 3:14 PM' or 'Mon 10:30 AM'")
            sys.exit(1)

        results = query_timeline(timeline, day, time)
        print_query_results(results, day, time)

    else:
        # Print full timeline
        print_timeline(timeline)

        print("=" * 100)
        print("QUERY EXAMPLES:")
        print("  python build-timeline.py --query 'Wednesday 3:14 PM'")
        print("  python build-timeline.py --query 'Mon 10:00 AM'")
        print("=" * 100)


if __name__ == '__main__':
    main()
