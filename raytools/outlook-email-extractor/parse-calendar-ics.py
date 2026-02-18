#!/usr/bin/env python3
"""
Parse Calendar Events from Outlook ICS File

Extracts calendar events from the past week defined as:
- Get date 3 days ago
- Find most recent Saturday before that date
- Extract Saturday through Friday (7 days)

This ensures Friday-Monday runs capture the same completed week.

Requires: pip install icalendar
"""

import json
import urllib.request
from datetime import datetime, timedelta
from icalendar import Calendar


ICS_URL = "https://outlook.office365.com/owa/calendar/6ddfa744aee741849b6a77b0e44aa0dc@confie.com/a134d1f53d46492895e93f088d69abd54388966280358402888/calendar.ics"


def calculate_target_week():
    """Calculate the target week: 3 days ago -> find Saturday before -> Sat-Fri week"""
    today = datetime.now()
    three_days_ago = today - timedelta(days=3)

    # Find most recent Saturday before that date
    day_of_week = three_days_ago.weekday()  # 0=Mon, 6=Sun
    # Convert to: 0=Sun, 6=Sat
    days_since_saturday = (day_of_week + 2) % 7
    if days_since_saturday == 0:
        days_since_saturday = 7

    target_saturday = three_days_ago - timedelta(days=days_since_saturday)
    target_friday = target_saturday + timedelta(days=6)

    return target_saturday, target_friday


def parse_ics_events(ics_content):
    """Parse ICS file content using icalendar library"""
    events = []

    # Parse the ICS file
    cal = Calendar.from_ical(ics_content)

    # Extract events
    for component in cal.walk():
        if component.name == "VEVENT":
            event = {
                'title': '',
                'start_time': None,
                'end_time': None,
                'all_day': False,
                'description': '',
                'location': '',
                'organizer': '',
                'status': 'CONFIRMED',
                'is_recurring': False,
                'is_canceled': False
            }

            # Extract SUMMARY (title)
            if 'SUMMARY' in component:
                event['title'] = str(component.get('SUMMARY'))

            # Extract DTSTART (start time)
            if 'DTSTART' in component:
                dtstart = component.get('DTSTART')
                if hasattr(dtstart.dt, 'hour'):
                    # It's a datetime object
                    event['start_time'] = dtstart.dt
                    event['all_day'] = False
                else:
                    # It's a date object (all-day event)
                    event['start_time'] = datetime.combine(dtstart.dt, datetime.min.time())
                    event['all_day'] = True

            # Extract DTEND (end time)
            if 'DTEND' in component:
                dtend = component.get('DTEND')
                if hasattr(dtend.dt, 'hour'):
                    event['end_time'] = dtend.dt
                else:
                    event['end_time'] = datetime.combine(dtend.dt, datetime.min.time())

            # Extract DESCRIPTION
            if 'DESCRIPTION' in component:
                event['description'] = str(component.get('DESCRIPTION'))

            # Extract LOCATION
            if 'LOCATION' in component:
                event['location'] = str(component.get('LOCATION'))

            # Extract ORGANIZER
            if 'ORGANIZER' in component:
                organizer = component.get('ORGANIZER')
                # Extract email from mailto: URI
                if organizer:
                    org_str = str(organizer)
                    if org_str.startswith('mailto:'):
                        event['organizer'] = org_str[7:]  # Remove 'mailto:'
                    else:
                        event['organizer'] = org_str

            # Check if recurring
            event['is_recurring'] = 'RRULE' in component

            # Extract STATUS
            if 'STATUS' in component:
                event['status'] = str(component.get('STATUS'))

            # Check if canceled
            event['is_canceled'] = event['status'] == 'CANCELLED'

            events.append(event)

    return events


def format_event_for_output(event):
    """Format event data for JSON output"""
    result = {
        'title': event['title'],
        'all_day': event['all_day'],
        'is_recurring': event['is_recurring'],
        'is_canceled': event.get('is_canceled', False),
        'status': event['status']
    }

    if event['start_time']:
        result['date'] = event['start_time'].strftime('%A, %B %d, %Y')
        result['day_of_week'] = event['start_time'].strftime('%A')

        if not event['all_day'] and event['end_time']:
            result['time'] = f"{event['start_time'].strftime('%I:%M %p')} - {event['end_time'].strftime('%I:%M %p')}"
        else:
            result['time'] = 'All day'
    else:
        result['date'] = 'Unknown'
        result['day_of_week'] = 'Unknown'
        result['time'] = 'Unknown'

    if event['location']:
        result['location'] = event['location']

    if event['organizer']:
        result['organizer'] = event['organizer']

    if event['description'] and event['description'] not in ['\\n', '\n', '']:
        result['description'] = event['description'][:200]  # First 200 chars

    return result


def main():
    # Calculate target week
    target_sat, target_fri = calculate_target_week()
    print(f"Target week: {target_sat.strftime('%A, %B %d, %Y')} - {target_fri.strftime('%A, %B %d, %Y')}")
    print()

    # Fetch ICS file
    print("Fetching calendar ICS file...")
    with urllib.request.urlopen(ICS_URL) as response:
        ics_content = response.read().decode('utf-8')

    print(f"Downloaded {len(ics_content)} bytes")
    print()

    # Parse events
    print("Parsing calendar events...")
    all_events = parse_ics_events(ics_content)
    print(f"Found {len(all_events)} total events in calendar")
    print()

    # Filter for target week
    target_week_events = []
    for event in all_events:
        if event['start_time']:
            # Normalize to naive datetime for comparison (remove timezone info)
            if hasattr(event['start_time'], 'tzinfo') and event['start_time'].tzinfo is not None:
                # Convert to naive datetime (remove timezone)
                event_date = event['start_time'].replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                event_date = event['start_time'].replace(hour=0, minute=0, second=0, microsecond=0)

            target_sat_date = target_sat.replace(hour=0, minute=0, second=0, microsecond=0)
            target_fri_date = target_fri.replace(hour=0, minute=0, second=0, microsecond=0)

            if target_sat_date <= event_date <= target_fri_date:
                target_week_events.append(event)

    print(f"Found {len(target_week_events)} events in target week")
    print("=" * 80)
    print()

    # Format for output
    formatted_events = []
    for event in sorted(target_week_events, key=lambda e: e['start_time'] or datetime.min):
        formatted = format_event_for_output(event)
        formatted_events.append(formatted)

        # Print preview
        print(f"• {formatted['day_of_week']}: {formatted['title']}")
        print(f"  Time: {formatted['time']}")
        if 'location' in formatted:
            print(f"  Location: {formatted['location']}")
        if formatted['is_recurring']:
            print(f"  [Recurring]")
        if formatted['is_canceled']:
            print(f"  [CANCELED]")
        print()

    # Prepare final output
    output = {
        'status': 'success',
        'extraction_date': datetime.now().strftime('%Y-%m-%d'),
        'target_week': {
            'start': target_sat.strftime('%A, %B %d, %Y'),
            'end': target_fri.strftime('%A, %B %d, %Y')
        },
        'total_events': len(formatted_events),
        'events': formatted_events
    }

    # Save to file
    output_file = f"calendar-events-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("=" * 80)
    print(f"✓ Saved {len(formatted_events)} events to {output_file}")

    return output


if __name__ == '__main__':
    result = main()
    print()
    print("Done!")
