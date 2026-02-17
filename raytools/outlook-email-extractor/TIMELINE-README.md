# Weekly Timeline Tool

Combines email, calendar, and Teams data to create a unified timeline of your week.

## 📊 Data Sources

The timeline tool integrates three data sources:

1. **Calendar Events** (`calendar-events-2026-01-31.json`)
   - Meeting times and locations
   - Recurring events
   - Canceled events

2. **Sent Emails** (`extraction-results-2026-01-31.json`)
   - Email subject lines
   - Recipients
   - Timestamps
   - Body previews

3. **Teams Messages** (`Teams_Sent.csv`)
   - Chat messages
   - Participants
   - Timestamps
   - Message previews

## 🚀 Usage

### View Full Timeline

```bash
python build-timeline.py
```

Shows your entire week organized by day with:
- 📅 Calendar events (with times and locations)
- ✉️ Sent emails (with recipients)
- 💬 Teams messages (with previews)

### Query Specific Times

```bash
python build-timeline.py --query "Wednesday 3:14 PM"
python build-timeline.py --query "Mon 10:00 AM"
python build-timeline.py --query "Friday 2:30 PM"
```

Answers questions like "What was I doing around 3:14 PM on Wednesday?"

Shows:
- Calendar events happening at that time
- Emails sent within 30 minutes of that time
- Teams messages sent within 30 minutes of that time

## 📁 Expected File Structure

```
data/2025-01-31/
├── calendar-events-2026-01-31.json  # From parse-calendar-ics.py
├── extraction-results-2026-01-31.json  # From outlook-extractor-final.js
└── Teams_Sent.csv  # Export from Teams (late Jan 2026 timeframe)
```

## 📋 Teams CSV Format

Expected columns:
- `SentOn` - Timestamp (e.g., "1/26/2026 15:30")
- `Where` - Chat type (e.g., "Chat (oneOnOne)")
- `Subject` - Participants (e.g., "Ray Morris, Ricky Ho")
- `BodyPreview` - Message text preview
- `Id` - Message ID

## ⏰ Time Matching Logic

- **Calendar events**: Exact time range matching
  - Shows events where query time falls between start and end time

- **Emails & Teams**: Proximity matching (±30 minutes)
  - Shows messages sent within 30 minutes of the query time

## 🎯 Example Output

### Full Timeline View
```
====================================================================================================
WEDNESDAY
====================================================================================================

  10:51 AM
  ✉️  Sent: Urgent Troubleshooting Session for Ping/Vertafore
     To: Cody DerryberryWed

  11:30 AM - 12:00 PM
  📅 Sonarqube code repositories
     Location: Microsoft Teams Meeting

  11:45 AM
  💬 Teams: Ray Morris, Ricky Ho
     Chat (oneOnOne)
     "Can you join the Sonarqube call? We need your input..."

  02:00 PM - 03:00 PM
  📅 Confie | Rapid7 - DAST
```

### Query View
```
====================================================================================================
WHAT WAS HAPPENING: Wednesday at 2:30 pm
====================================================================================================

📅 Calendar Event: Confie | Rapid7 - DAST
   Time: 02:00 PM - 03:00 PM
```

## 📝 Notes

- Timeline is organized by day of week (Monday through Sunday)
- Events are sorted chronologically within each day
- Canceled calendar events are marked with [CANCELED]
- Recurring events are marked with [RECURRING]
- All-day events show as "All day"

## 🔄 Updating Data

When you fetch new Teams data for the correct time period:
1. Save it as `data/2025-01-31/Teams_Sent.csv`
2. Run `python build-timeline.py` again
3. The timeline will automatically include Teams messages

---

**Created:** 2026-01-31
**Last Updated:** 2026-01-31
