# Project Timesheet Format Documentation

## Overview

`Project-Timesheet.xlsx` is a multi-sheet Excel workbook that tracks weekly work activities by category.

- **One sheet per week** (named by week start date: `YYYY-MM-DD`)
- **Activities at top** with time blocks
- **Category totals at bottom** with formulas

## Sheet Structure

### Header Section (Rows 1-4)

```
Row 1: (blank)
Row 2: Name: | Ray Morris
Row 3: (blank)
Row 4: Date | Project / Category | Start Time | End Time | (blank) | StartTime | EndTime | Hours
```

**Columns:**
- **A**: Date
- **B**: Project / Category
- **C**: Start Time (first time block)
- **D**: End Time (first time block)
- **E**: (blank spacer)
- **F**: StartTime (second time block - optional)
- **G**: EndTime (second time block - optional)
- **H**: Hours (calculated total)

### Activity Data Section (Rows 5-30)

Each row represents one activity with its time allocation.

**Date Column (A):**
- Row 5: Actual date (e.g., `2025-06-30`)
- Subsequent rows use formulas:
  - Same day: `=A5`
  - Next day: `=A5+1`
  - Two days later: `=A5+2`
  - etc.

**Category Column (B):**
- Text values matching category names exactly
- Examples:
  - `Passwordless / SSO`
  - `App dev / Sonarqube`
  - `Email security`
  - `Cyera`
  - `Alerts`
  - `Admin (weekly team mtg etc)`
  - `Support`

**Time Columns (C, D, F, G):**
- Format: `HH:MM:SS` (Excel time format)
- C-D: First time block
- F-G: Second time block (optional - for activities spanning multiple periods in one day)

**Hours Column (H):**
- Formula: `=( (D5-C5) * 24) + ( (G5-F5) * 24)`
- Calculates total hours from both time blocks
- Multiplies by 24 to convert Excel time (0-1 fraction) to hours

### Category Totals Section (Starting Row 32)

```
Row 31: (blank)
Row 32: Weekly totals:
Row 33: Passwordless / SSO | =ROUND(SUMIF($B$5:$B$30,A33,$H$5:$H$30), 0) | =B33 / SUM(B$33:B40)
Row 34: App dev / Sonarqube | =ROUND(SUMIF($B$5:$B$30,A34,$H$5:$H$30), 0) | =B34 / SUM(B$33:B41)
...
```

**Column A:** Category name (must match exactly with category names used in rows 5-30)

**Column B:** Total hours for category
- Formula: `=ROUND(SUMIF($B$5:$B$30,A33,$H$5:$H$30), 0)`
- Sums all hours (column H) where category (column B) matches this category
- Rounds to whole number

**Column C:** Percentage of total time
- Formula: `=B33 / SUM(B$33:B40)`
- Divides category hours by sum of all category hours
- Shows as percentage when formatted

## Categories List

The following categories appear in the totals section (rows 33+):

1. Passwordless / SSO
2. App dev / Sonarqube
3. Email security
4. Cyera
5. Alerts
6. Admin (weekly team mtg etc)
7. Support / P1
8. Cyberark
9. Prisma
10. DAST / Security Scanning

## Example Week Structure

```
Row 2:  Name: | Ray Morris
Row 4:  Date | Project / Category | Start Time | End Time | | StartTime | EndTime | Hours
Row 5:  2025-06-30 | Passwordless / SSO | 09:00:00 | 11:00:00 | | 12:00:00 | 13:00:00 | =formula
Row 6:  =A5 | Email security | 13:00:00 | 15:00:00 | | | | =formula
Row 7:  =A5 | Support | 15:00:00 | 16:00:00 | | | | =formula
...
Row 10: =A5+1 | Passwordless | 09:00:00 | 15:00:00 | | | | =formula
...
Row 32: Weekly totals:
Row 33: Passwordless / SSO | =SUMIF formula | =percentage formula
Row 34: App dev / Sonarqube | =SUMIF formula | =percentage formula
...
```

## Sheet Naming Convention

Sheets are named with the **week start date** (Saturday) in format `YYYY-MM-DD`.

Examples:
- `2025-06-30` (Saturday, June 30, 2025)
- `2025-07-07` (Saturday, July 7, 2025)
- `2025-11-29` (Saturday, November 29, 2025)

## Data Flow for New Week

### Input Data (from timeline)
```json
{
  "timeline": [
    {
      "type": "calendar_event",
      "datetime": "2026-01-26T10:00:00",
      "title": "Interview",
      "category": "Admin",  // ← Added by LLM
      "duration_hours": 0.5  // ← Calculated from start/end time
    },
    {
      "type": "email_sent",
      "datetime": "2026-01-26T14:30:00",
      "subject": "Sonarqube review",
      "category": "App dev / Sonarqube",  // ← Added by LLM
      "duration_hours": 0.25  // ← Estimated
    }
  ]
}
```

### Output: Excel Sheet

**Step 1:** Group activities by date and category
**Step 2:** Convert to time blocks
**Step 3:** Write to Excel with formulas

## Key Requirements for Script

1. **Date Formulas**: Use `=A5`, `=A5+1` pattern for date increments
2. **Hours Formula**: Must include both time blocks: `=( (D-C) * 24) + ( (G-F) * 24)`
3. **Category Matching**: Exact string match between activity categories and totals section
4. **SUMIF Formula**: Fixed range `$B$5:$B$30` (absolute references)
5. **Percentage Formula**: Relative row references for dynamic totaling
6. **Sheet Name**: Saturday date in `YYYY-MM-DD` format

## Assumptions About Categorized Timeline

The input timeline will have:
1. **Each entry categorized**: LLM has assigned a `category` field matching one of the 10 categories
2. **Time blocks defined**: Either:
   - Calendar events: Use actual start/end times
   - Emails/Teams: Estimate duration (e.g., 0.25 hours per email)
3. **Chronological order**: Entries sorted by datetime

## Edge Cases to Handle

1. **Multiple activities in same time slot**: Use F-G columns for second block
2. **Activities spanning midnight**: Split into two rows (different dates)
3. **Uncategorized activities**: Require manual review or default category
4. **Overlapping times**: Script should detect and flag conflicts
5. **Empty days**: Include row with date but no activity

---

**Created:** 2026-01-31
**Last Updated:** 2026-01-31
