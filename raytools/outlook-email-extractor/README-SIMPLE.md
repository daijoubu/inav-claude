# Outlook Email & Calendar Extractor

Extract email and calendar data from Outlook Web App.

## 📁 Files

### Email Extraction
- **`outlook-extractor-final.js`** ⭐ - Email extraction script (tested & working)
- **`convert-to-csv.py`** - Convert email JSON to CSV
- **`convert-to-csv.js`** - Convert email JSON to CSV (Browser)
- **`extraction-results-2026-01-31.json`** - Sample output (12 emails)

### Calendar Extraction
- **`parse-calendar-ics.py`** ⭐ - Calendar ICS parser (tested & working)
- **`convert-calendar-to-csv.py`** - Convert calendar JSON to CSV
- **`calendar-events-2026-01-31.json`** - Sample output (18 events)
- **`calendar-events.csv`** - Sample CSV output

### Timeline Builder
- **`build-timeline.py`** - Combine email + calendar + Teams data
- **`TIMELINE-README.md`** - Timeline usage guide

### Documentation
- **`README.md`** - Full documentation
- **`outlook-extractor-README.md`** - Email extraction details

---

## 🚀 Quick Start

### Email Extraction

**Step 1: Extract Emails**

```bash
# Start Chrome with debugging
google-chrome --remote-debugging-port=9222

# Navigate to: https://outlook.office.com/mail/sentitems
# Scroll until you see "Last week" emails
```

Run `outlook-extractor-final.js` via Chrome DevTools MCP.

**Returns:** JSON with To: addresses, subject, timestamp, first 50 words of body

**Step 2: Convert to CSV**

```bash
python convert-to-csv.py extraction-results-2026-01-31.json emails.csv
```

---

### Calendar Extraction

**Step 1: Extract Calendar Events**

```bash
python parse-calendar-ics.py
```

**Returns:** JSON with events from the "past week" (3 days ago → Saturday before → Sat-Fri)

**Step 2: Convert to CSV**

```bash
python convert-calendar-to-csv.py calendar-events-2026-01-31.json calendar.csv
```

---

## ✅ What Was Tested

### Email Extraction
- ✅ Extracted 12 emails successfully
- ✅ To: addresses captured (email format when available)
- ✅ First 50 words of body text
- ✅ Subject lines and timestamps
- ✅ Stops at "Last week" as requested

### Calendar Extraction
- ✅ Extracted 18 events from target week (Jan 24-30, 2026)
- ✅ Date calculation: 3 days ago → Saturday before → Sat-Fri
- ✅ Full event details: title, time, location, description
- ✅ Recurring and canceled event flags
- ✅ All-day event detection

---

## 📊 Sample Output

### Email Extraction
```json
{
  "status": "success",
  "totalExtracted": 12,
  "emails": [
    {
      "index": 1,
      "subject": "Velox Sonarqube scan results",
      "timestamp": "12/18/2025",
      "toAddresses": ["tony@whitespaces.design", "richard.estrella@estrellainsurance.com"],
      "toCount": 2,
      "bodyPreview": "Yes sir, I mis-clicked...",
      "bodyWordCount": 32
    }
  ]
}
```

### Calendar Extraction
```json
{
  "status": "success",
  "extraction_date": "2026-01-31",
  "target_week": {
    "start": "Saturday, January 24, 2026",
    "end": "Friday, January 30, 2026"
  },
  "total_events": 18,
  "events": [
    {
      "title": "1st Round Virtual Interview: Application Security Engineer-Jay Molinaro",
      "date": "Monday, January 26, 2026",
      "time": "10:00 AM - 10:30 AM",
      "location": "Microsoft Teams Meeting",
      "is_recurring": false,
      "is_canceled": false
    }
  ]
}
```

---

See **README.md** for full documentation.
