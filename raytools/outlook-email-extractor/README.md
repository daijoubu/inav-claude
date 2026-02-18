# Outlook Email & Calendar Extractor

Extract email and calendar data from Outlook Web App, then combine into a unified timeline.

## 📁 Files in This Folder

### Email Extraction

**`outlook-extractor-final.js`** ⭐
   - Extracts sent emails via Chrome DevTools MCP
   - Gets To: addresses and first 50 words of body
   - Stops at "Last week" section
   - Returns JSON output

### Calendar Extraction

**`parse-calendar-ics.py`** ⭐
   - Fetches calendar from Outlook ICS URL
   - Extracts events from "past week" (3 days ago → Saturday before → Sat-Fri)
   - Returns JSON with full event details
   - Requires: `pip install icalendar`

### Timeline Builder

**`build-timeline.py`** ⭐
   - Combines email + calendar + Teams data
   - Creates chronological timeline by day
   - Query specific times: "What was I doing Wednesday at 3:14 PM?"
   - See `TIMELINE-README.md` for details

### CSV Converters

**`convert-to-csv.py`**
   - Convert email JSON to CSV (Python)
   - Interactive or file mode
   - Handles multiple To: addresses

**`convert-to-csv.js`**
   - Convert email JSON to CSV (Browser)
   - Downloads CSV directly

**`convert-calendar-to-csv.py`**
   - Convert calendar JSON to CSV

### Documentation

**`README.md`** (this file) - Complete guide

**`README-SIMPLE.md`** - Quick start guide

**`outlook-extractor-README.md`** - Email extraction details

**`TIMELINE-README.md`** - Timeline usage guide

## 🚀 Quick Start

### Prerequisites

```bash
# Start Chrome with remote debugging
google-chrome --remote-debugging-port=9222

# Open Outlook Sent Items
# https://outlook.office.com/mail/sentitems
```

### Email Extraction

**Step 1: Navigate to Outlook Sent Items**

In Outlook:
1. Scroll down in the message list (left side)
2. Keep scrolling until you see "Last week" section

**Step 2: Run the extraction script**

Run via Claude Code MCP server:

```javascript
// Execute outlook-extractor-final.js via Chrome DevTools MCP
```

The script will:
- Click through each email
- Extract To: addresses and body text (first 50 words)
- Stop at "Last week" section
- Return JSON data

### Calendar Extraction

**Step 1: Run the calendar parser**

```bash
python parse-calendar-ics.py
```

The script will:
- Fetch calendar from ICS URL
- Extract events from target week (3 days ago → Saturday before → Sat-Fri)
- Return JSON with full event details

### Timeline Creation

**Step 1: Get Teams data** (if available)
- Export Teams messages to CSV
- Save as `data/2025-01-31/Teams_Sent.csv`

**Step 2: Build unified timeline**

```bash
python build-timeline.py
```

**Step 3: Query specific times**

```bash
python build-timeline.py --query "Wednesday 3:14 PM"
```

## 📊 What Gets Extracted

For each email:

```json
{
  "index": 1,
  "subject": "Password reset followup",
  "timestamp": "Fri 4:26 PM",
  "toAddresses": ["ricky.ho@confie.com", "abraham.ruelas@confie.com"],
  "toCount": 2,
  "bodyPreview": "Why was the conversation terminated? After the use stated...",
  "bodyWordCount": 50
}
```

## 🎯 Current Results

**Last extraction run:** 2026-01-31

- **Emails extracted:** 17
- **Sections covered:** Pinned, Yesterday, This week, Last week
- **Total available in folder:** 9,982 (only recent shown by Outlook)

## ⚠️ Important Notes

### Why Only Recent Emails?

Outlook Web App uses **lazy loading** with time-based grouping:
- Only loads recent emails by default
- Older emails require scrolling/manual loading
- The script stops at "Last week" as requested

### Time Sections in Outlook

- **Pinned** - Manually pinned emails
- **Yesterday** - Emails from yesterday
- **This week** - Emails from this week
- **Last week** - Emails from last week ← Script stops here
- Older sections require manual scrolling

### Empty Body Previews

Meeting invites and calendar items may show empty body text because:
- They use a different format
- No plain text body available
- Reading pane shows only meeting details

## 🔧 Advanced Usage

### Extract More Than "Last Week"

To extract older emails:

1. Manually scroll past "Last week" in Outlook
2. Load the older time sections (2 weeks ago, etc.)
3. Run the script again
4. It will extract all visible emails

### Save Results to File

After running extraction:

```javascript
// In browser console:
const data = /* paste extraction results */;
const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'outlook-emails-' + new Date().toISOString().split('T')[0] + '.json';
a.click();
```

### Convert to CSV

**Option 1: Python Script (Recommended)**

```bash
# From file
python convert-to-csv.py extraction-results.json emails.csv

# Or paste JSON interactively
python convert-to-csv.py
```

**Option 2: JavaScript (Browser)**

```javascript
// After extraction, in browser console:
const results = /* your extraction results */;

// Load the converter script first (paste convert-to-csv.js)
// Then:
downloadEmailsAsCSV(results, 'outlook-emails.csv');
```

**Option 3: Manual Python**

```python
import json
import csv

with open('outlook-emails.json', 'r') as f:
    data = json.load(f)

with open('outlook-emails.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['index', 'subject', 'timestamp', 'toAddresses', 'bodyPreview'])
    writer.writeheader()

    for email in data['emails']:
        email['toAddresses'] = '; '.join(email['toAddresses'])
        writer.writerow(email)
```

## 📝 Sample Output

```
Email #1:
  Subject: Velox Sonarqube scan results
  Timestamp: 12/18/2025
  To: tony@whitespaces.design, richard.estrella@estrellainsurance.com, christian.montiel@estrellainsurance.com
  Body: "Yes sir, I mis-clicked. I just updated the invitation. -- Ray Morris..."

Email #3:
  Subject: Password reset followup
  Timestamp: Fri 4:26 PM
  To: Ricky Ho, Abraham Ruelas Monge
  Body: "Why was the conversation terminated? After the use stated that they would do all their work..."
```

## 🐛 Troubleshooting

### "Last week" section not found

**Solution:** Scroll down in Outlook's message list until you see "Last week"

### Script extracts 0 emails

**Causes:**
1. Not on Sent Items page
2. No emails in Sent Items
3. Chrome DevTools not connected

**Solution:**
- Navigate to Outlook Sent Items
- Ensure Chrome is running with `--remote-debugging-port=9222`

### Duplicate body previews

**Cause:** Email threads may share the same reading pane content

**Solution:** Normal behavior for conversation threads

### Empty To: addresses

**Cause:** Email format may not have accessible To: field

**Solution:** Check if email is a calendar item or special format

## 📄 License

Created for internal use. Modify as needed.

## 🤝 Contributing

To improve the scripts:
1. Test on different Outlook views
2. Handle edge cases (calendar invites, etc.)
3. Add error handling
4. Optimize extraction speed

---

**Created:** 2026-01-31
**Last Updated:** 2026-01-31
**Location:** `claude/developer/workspace/outlook-email-extractor/`
