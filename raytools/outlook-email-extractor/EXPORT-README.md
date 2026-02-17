# Timeline JSON Export

Export complete chronological timeline data as JSON for easy parsing and analysis.

## Overview

`export-timeline-json.py` creates a structured JSON file containing all your email, calendar, and Teams data in chronological order with complete message bodies and event details.

## Usage

### Basic Export

```bash
python export-timeline-json.py
```

Creates `timeline-2026-01-31.json` with data from the default week (3 days ago → Saturday before → Sat-Fri).

### Custom Output File

```bash
python export-timeline-json.py --output my-timeline.json
```

### Specify Week

```bash
python export-timeline-json.py --week "2026-01-24"
```

Exports timeline starting from the specified Saturday.

### Custom Data Sources

```bash
python export-timeline-json.py \
  --calendar path/to/calendar.json \
  --email path/to/emails.json \
  --teams path/to/teams.csv
```

## JSON Structure

```json
{
  "export_date": "2026-01-31T21:01:58.550851",
  "week_range": {
    "start": "2026-01-24",
    "end": "2026-01-30",
    "description": "Saturday, January 24, 2026 - Friday, January 30, 2026"
  },
  "summary": {
    "total_entries": 27,
    "calendar_events": 18,
    "emails_sent": 9,
    "teams_messages": 0
  },
  "metadata": {
    "sources": {
      "calendar": "data/2025-01-31/calendar-events-2026-01-31.json",
      "email": "data/2025-01-31/extraction-results-2026-01-31.json",
      "teams": "data/2025-01-31/Teams_Sent.csv"
    }
  },
  "timeline": [
    {
      "type": "calendar_event",
      "datetime": "2026-01-26T10:00:00",
      "timestamp": 1769443200.0,
      "date": "Monday, January 26, 2026",
      "day_of_week": "Monday",
      "time": "10:00 AM - 10:30 AM",
      "title": "Interview Title",
      "location": "Microsoft Teams Meeting",
      "description": "Full event description...",
      "organizer": "organizer@example.com",
      "status": "CONFIRMED",
      "is_canceled": false,
      "is_recurring": false,
      "all_day": false
    },
    {
      "type": "email_sent",
      "datetime": "2026-01-28T10:51:00",
      "timestamp": 1769619060.0,
      "timestamp_raw": "Wed 10:51 AM",
      "subject": "Email Subject",
      "to_addresses": ["recipient1@example.com", "recipient2@example.com"],
      "to_count": 2,
      "body_preview": "First 50 words of email body...",
      "body_word_count": 50
    },
    {
      "type": "teams_message",
      "datetime": "2026-01-28T14:30:00",
      "timestamp": 1769632200.0,
      "timestamp_raw": "1/28/2026 14:30",
      "where": "Chat (oneOnOne)",
      "participants": "Ray Morris, Ricky Ho",
      "body": "Full message text here...",
      "message_id": "1234567890"
    }
  ]
}
```

## Field Descriptions

### Common Fields (All Entry Types)

- **`type`**: Entry type - `"calendar_event"`, `"email_sent"`, or `"teams_message"`
- **`datetime`**: ISO 8601 datetime string (e.g., `"2026-01-26T10:00:00"`)
- **`timestamp`**: Unix timestamp (seconds since epoch) for easy sorting/filtering

### Calendar Event Fields

- **`date`**: Human-readable date (e.g., `"Monday, January 26, 2026"`)
- **`day_of_week`**: Day name (e.g., `"Monday"`)
- **`time`**: Time range or `"All day"` (e.g., `"10:00 AM - 10:30 AM"`)
- **`title`**: Event title
- **`location`**: Meeting location or URL
- **`description`**: Full event description/notes
- **`organizer`**: Event organizer email
- **`status`**: Event status (e.g., `"CONFIRMED"`, `"CANCELLED"`)
- **`is_canceled`**: Boolean - true if event is canceled
- **`is_recurring`**: Boolean - true if recurring event
- **`all_day`**: Boolean - true if all-day event

### Email Fields

- **`timestamp_raw`**: Original timestamp string from email data
- **`subject`**: Email subject line
- **`to_addresses`**: Array of recipient addresses/names
- **`to_count`**: Number of recipients
- **`body_preview`**: First 50 words of email body
- **`body_word_count`**: Number of words in preview

### Teams Message Fields

- **`timestamp_raw`**: Original timestamp string from Teams data
- **`where`**: Chat type (e.g., `"Chat (oneOnOne)"`, `"Channel"`)
- **`participants`**: Participant names
- **`body`**: Full message text
- **`message_id`**: Unique message identifier

## Parsing in Python

```python
import json
from datetime import datetime

# Load timeline
with open('timeline-export.json', 'r') as f:
    data = json.load(f)

# Access summary
print(f"Total entries: {data['summary']['total_entries']}")
print(f"Week: {data['week_range']['description']}")

# Iterate through timeline
for entry in data['timeline']:
    dt = datetime.fromisoformat(entry['datetime'])

    if entry['type'] == 'calendar_event':
        print(f"{dt}: Meeting - {entry['title']}")

    elif entry['type'] == 'email_sent':
        print(f"{dt}: Email to {entry['to_count']} recipients - {entry['subject']}")

    elif entry['type'] == 'teams_message':
        print(f"{dt}: Teams - {entry['participants']}")
```

## Parsing with Claude

Simply provide the JSON file to Claude:

```
I have a timeline of my week in timeline-export.json.
Can you summarize what I did on Wednesday?
```

Claude can easily parse the structured JSON and answer questions about:
- What you were doing at specific times
- Who you communicated with
- Meeting topics and attendees
- Time spent in meetings vs. sending emails

## Sorting and Filtering

All entries are pre-sorted chronologically by timestamp. To filter:

```python
import json

with open('timeline-export.json', 'r') as f:
    data = json.load(f)

# Get only calendar events
events = [e for e in data['timeline'] if e['type'] == 'calendar_event']

# Get entries on a specific day
wednesday = [e for e in data['timeline']
             if e.get('day_of_week') == 'Wednesday']

# Get entries after a certain time
from datetime import datetime
cutoff = datetime(2026, 1, 28, 14, 0).timestamp()
afternoon = [e for e in data['timeline'] if e['timestamp'] > cutoff]
```

## Advantages Over Display Format

1. **Complete Data**: Includes full descriptions, message bodies, all recipients
2. **Structured**: Easy to parse programmatically
3. **Sortable**: Unix timestamps for easy chronological sorting
4. **Filterable**: Query by type, time, participants, etc.
5. **Portable**: Standard JSON format works everywhere
6. **Claude-Friendly**: Claude can easily analyze and answer questions about the data

## Notes

- Email timestamps may be approximate if only relative times are available (e.g., "Wed 10:51 AM")
- Teams messages are only included if they fall within the target week
- All entries without valid timestamps are excluded from the export
- Chronological order is guaranteed by Unix timestamp sorting

---

**Created:** 2026-01-31
