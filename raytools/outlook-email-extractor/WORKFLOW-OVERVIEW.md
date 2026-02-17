# Complete Timeline-to-Timesheet Workflow

## Overview

This workflow extracts your weekly activities from email, calendar, and Teams, categorizes them using an LLM, and generates a formatted Excel timesheet.

## Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Data Extraction                                           │
└─────────────────────────────────────────────────────────────────────┘

1. Email Extraction
   Script: outlook-extractor-final.js
   Output: extraction-results-YYYY-MM-DD.json

2. Calendar Extraction
   Script: parse-calendar-ics.py
   Output: calendar-events-YYYY-MM-DD.json

3. Teams Export
   Manual: Export Teams chat history to CSV
   Output: Teams_Sent.csv

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: Timeline Generation                                       │
└─────────────────────────────────────────────────────────────────────┘

4. Combine Data Sources
   Script: export-timeline-json.py
   Input: emails.json + calendar.json + teams.csv
   Output: timeline-export.json

   Result: Chronological timeline with complete details

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: AI Categorization (LLM)                                   │
└─────────────────────────────────────────────────────────────────────┘

5. Categorize Activities
   Script: categorize-timeline.py (to be implemented)
   Input: timeline-export.json + work-categories.json
   Process: LLM analyzes each activity and assigns category
   Output: categorized-timeline.json

   Structure:
   {
     "timeline": [
       {
         "datetime": "2026-01-26T10:00:00",
         "title": "Darktrace troubleshooting",
         "category": "Alerts",  ← Added by LLM
         "start_time": "10:00:00",
         "end_time": "10:30:00"
       }
     ]
   }

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 4: Timesheet Generation                                      │
└─────────────────────────────────────────────────────────────────────┘

6. Generate Excel Tab
   Script: generate-timesheet-tab.py (to be implemented)
   Input: categorized-timeline.json
   Output: New tab in Project-Timesheet.xlsx

   Result: Formatted Excel sheet with:
   - Activity rows with time blocks
   - Category totals with formulas
   - Percentage calculations
```

## File Flow Diagram

```
outlook-extractor-final.js
    ↓
extraction-results.json ─────┐
                             │
parse-calendar-ics.py        │
    ↓                        ├─→ export-timeline-json.py
calendar-events.json ────────┤       ↓
                             │   timeline-export.json
Teams_Sent.csv ──────────────┘       ↓
                                     │
work-categories.json ────────────────┼─→ categorize-timeline.py
                                     │       ↓
                                     │   categorized-timeline.json
                                     │       ↓
                                     └──→ generate-timesheet-tab.py
                                             ↓
                                         Project-Timesheet.xlsx
                                         (new tab created)
```

## Current Status

### ✅ Completed

1. **Email Extraction**
   - `outlook-extractor-final.js` - Working
   - Extracts To:, subject, body preview

2. **Calendar Extraction**
   - `parse-calendar-ics.py` - Working
   - Fetches from ICS URL
   - Extracts full event details

3. **Timeline Export**
   - `export-timeline-json.py` - Working
   - Combines all data sources
   - Chronological JSON output

4. **Category Definitions**
   - `work-categories.json` - Defined
   - 10 categories with keywords
   - Ready for LLM matching

5. **Format Documentation**
   - `TIMESHEET-FORMAT.md` - Complete
   - Excel structure documented
   - Formula patterns defined

6. **Implementation Plan**
   - `TIMESHEET-SCRIPT-PLAN.md` - Complete
   - Detailed script design
   - Code examples provided

### ⏳ To Be Implemented

1. **LLM Categorization Script** (`categorize-timeline.py`)
   - Read `timeline-export.json`
   - For each activity, use LLM to:
     - Match keywords from `work-categories.json`
     - Assign best-fit category
     - Estimate duration if needed
   - Output `categorized-timeline.json`

2. **Timesheet Generator** (`generate-timesheet-tab.py`)
   - Read `categorized-timeline.json`
   - Group activities by date
   - Create Excel sheet structure
   - Write formulas
   - Save to `Project-Timesheet.xlsx`

## Workflow Commands

### Weekly Routine

```bash
# 1. Extract emails (via Chrome DevTools MCP)
# Run outlook-extractor-final.js

# 2. Extract calendar
python parse-calendar-ics.py --output calendar-events-YYYY-MM-DD.json

# 3. Export Teams (manual)
# Export chat history from Teams

# 4. Combine into timeline
python export-timeline-json.py \
  --calendar calendar-events-YYYY-MM-DD.json \
  --email extraction-results-YYYY-MM-DD.json \
  --teams Teams_Sent.csv \
  --output timeline-export.json

# 5. Categorize with LLM
python categorize-timeline.py \
  --input timeline-export.json \
  --categories work-categories.json \
  --output categorized-timeline.json

# 6. Generate timesheet tab
python generate-timesheet-tab.py \
  --input categorized-timeline.json \
  --workbook Project-Timesheet.xlsx
```

### One-Shot Automation (Future)

```bash
# All-in-one script
python weekly-timesheet.py --week 2026-01-24
```

## LLM Categorization Strategy

The LLM will analyze each timeline entry and:

1. **Extract key terms** from title, description, participants
2. **Match against keywords** in `work-categories.json`
3. **Apply context**:
   - "Interview" + "Application Security Engineer" → Admin
   - "Darktrace" → Alerts
   - "Sonarqube" + "review" → App dev / Sonarqube
   - "Ping" + "troubleshoot" → Passwordless / SSO
4. **Handle ambiguity**:
   - Multiple matches → Choose most specific
   - No matches → Flag for manual review
5. **Estimate duration** for emails/Teams (e.g., 0.25 hours)

### Example LLM Prompt

```
You are categorizing work activities for a security engineer's timesheet.

Categories and keywords:
{work-categories.json content}

Activity to categorize:
{
  "datetime": "2026-01-26T13:00:00",
  "type": "calendar_event",
  "title": "RE: Darktrace x Confie - vSensor Troubleshooting",
  "description": "Troubleshooting meeting for vSensor deployment issues"
}

Assign the best-fit category and explain your reasoning.
Return JSON: {"category": "Alerts", "confidence": "high", "reasoning": "..."}
```

## Quality Checks

Before generating timesheet, validate:

1. **All activities categorized** - No null/empty categories
2. **Valid categories** - Match names in `work-categories.json`
3. **Time coverage** - Hours add up to reasonable weekly total
4. **No overlaps** - No two activities at same time
5. **Duration estimates** - Reasonable (e.g., emails 5-15 min)

## Next Steps

1. Implement `categorize-timeline.py`
   - Design LLM prompts
   - Handle batch processing
   - Add confidence scoring

2. Implement `generate-timesheet-tab.py`
   - Follow TIMESHEET-SCRIPT-PLAN.md
   - Add validation checks
   - Test with sample data

3. Test end-to-end with one week
   - Verify Excel formulas
   - Check category totals
   - Validate percentages

4. Iterate on categorization accuracy
   - Review LLM assignments
   - Refine keywords if needed
   - Add edge case handling

5. Create automation wrapper
   - One command for full pipeline
   - Error handling
   - Progress reporting

---

**Created:** 2026-01-31
**Status:** Documentation phase complete, ready for implementation
