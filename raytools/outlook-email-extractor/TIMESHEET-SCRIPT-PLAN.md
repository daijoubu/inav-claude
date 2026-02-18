# Timesheet Generator Script - Implementation Plan

## Goal

Create a script that generates a new weekly timesheet tab from categorized timeline data.

## Input

**Categorized Timeline JSON** (output from LLM categorization):

```json
{
  "week_range": {
    "start": "2026-01-24",
    "end": "2026-01-30"
  },
  "categorized_timeline": [
    {
      "datetime": "2026-01-26T10:00:00",
      "type": "calendar_event",
      "title": "1st Round Interview",
      "category": "Admin",
      "start_time": "10:00:00",
      "end_time": "10:30:00",
      "duration_hours": 0.5
    },
    {
      "datetime": "2026-01-26T13:00:00",
      "type": "calendar_event",
      "title": "Darktrace troubleshooting",
      "category": "Alerts",
      "start_time": "13:00:00",
      "end_time": "13:45:00",
      "duration_hours": 0.75
    }
  ]
}
```

## Output

New Excel sheet in `Project-Timesheet.xlsx` with:
- Sheet name: `2026-01-24` (Saturday start date)
- Activities in rows 5-30
- Category totals in rows 33+
- All formulas properly set

## Script Design

### Script Name: `generate-timesheet-tab.py`

### Command Line Interface

```bash
# Basic usage - reads from categorized-timeline.json
python generate-timesheet-tab.py

# Specify input file
python generate-timesheet-tab.py --input categorized-timeline-2026-01-24.json

# Specify output workbook
python generate-timesheet-tab.py --workbook Project-Timesheet.xlsx

# Preview mode (print to console, don't write Excel)
python generate-timesheet-tab.py --preview
```

### Process Flow

```
1. Load categorized timeline JSON
   ↓
2. Validate categories (match against work-categories.json)
   ↓
3. Group activities by date
   ↓
4. Assign activities to time slots (consolidate overlapping)
   ↓
5. Create Excel sheet structure
   ↓
6. Write header section (rows 1-4)
   ↓
7. Write activity rows (5-30) with formulas
   ↓
8. Write category totals (rows 32+) with SUMIF formulas
   ↓
9. Apply formatting
   ↓
10. Save workbook
```

## Detailed Implementation

### Step 1: Load and Validate

```python
def load_categorized_timeline(input_file):
    """Load JSON and validate structure"""
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Validate required fields
    required = ['week_range', 'categorized_timeline']
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    return data

def validate_categories(timeline, categories_file='work-categories.json'):
    """Ensure all categories are valid"""
    with open(categories_file, 'r') as f:
        valid_categories = [cat['name'] for cat in json.load(f)['categories']]

    invalid = []
    for entry in timeline:
        if entry.get('category') not in valid_categories:
            invalid.append(entry)

    if invalid:
        print(f"Warning: {len(invalid)} entries have invalid categories")
        for entry in invalid:
            print(f"  - {entry['datetime']}: '{entry.get('category')}'")

    return len(invalid) == 0
```

### Step 2: Group by Date

```python
from datetime import datetime
from collections import defaultdict

def group_by_date(timeline):
    """Group activities by date"""
    by_date = defaultdict(list)

    for entry in timeline:
        dt = datetime.fromisoformat(entry['datetime'])
        date_key = dt.date()
        by_date[date_key].append(entry)

    # Sort each day's activities by time
    for date in by_date:
        by_date[date].sort(key=lambda e: datetime.fromisoformat(e['datetime']))

    return by_date
```

### Step 3: Consolidate to Time Slots

```python
def consolidate_to_rows(daily_activities):
    """
    Convert activities to Excel rows.

    Each row can have up to 2 time blocks (C-D and F-G).
    Try to consolidate adjacent/close activities of same category.
    """
    rows = []

    for date, activities in sorted(daily_activities.items()):
        # Try to pair activities into rows with 2 time blocks
        i = 0
        while i < len(activities):
            row = {
                'date': date,
                'category': activities[i]['category'],
                'start_time_1': activities[i]['start_time'],
                'end_time_1': activities[i]['end_time'],
                'start_time_2': None,
                'end_time_2': None
            }

            # Check if next activity is same category and reasonably close
            if i + 1 < len(activities):
                next_act = activities[i + 1]
                if (next_act['category'] == row['category'] and
                    is_close_enough(activities[i], next_act)):
                    row['start_time_2'] = next_act['start_time']
                    row['end_time_2'] = next_act['end_time']
                    i += 2
                else:
                    i += 1
            else:
                i += 1

            rows.append(row)

    return rows

def is_close_enough(act1, act2, max_gap_hours=4):
    """Check if two activities are close enough to combine in one row"""
    dt1_end = datetime.fromisoformat(act1['datetime']).replace(
        hour=int(act1['end_time'].split(':')[0]),
        minute=int(act1['end_time'].split(':')[1])
    )
    dt2_start = datetime.fromisoformat(act2['datetime']).replace(
        hour=int(act2['start_time'].split(':')[0]),
        minute=int(act2['start_time'].split(':')[1])
    )

    gap_hours = (dt2_start - dt1_end).total_seconds() / 3600
    return gap_hours <= max_gap_hours
```

### Step 4: Create Excel Structure

```python
import openpyxl
from openpyxl.utils import get_column_letter
from datetime import datetime, time

def create_timesheet_tab(workbook, week_start_date, activity_rows, categories):
    """Create new sheet with timesheet data"""

    # Sheet name from Saturday date
    sheet_name = week_start_date.strftime('%Y-%m-%d')

    # Create or get sheet
    if sheet_name in workbook.sheetnames:
        ws = workbook[sheet_name]
    else:
        ws = workbook.create_sheet(sheet_name)

    # Row 2: Name
    ws['A2'] = 'Name:'
    ws['B2'] = 'Ray Morris'

    # Row 4: Headers
    headers = ['Date', 'Project / Category', 'Start Time', 'End Time',
               ' ', 'StartTime', 'EndTime', 'Hours']
    for col_idx, header in enumerate(headers, start=1):
        ws.cell(4, col_idx, header)

    # Rows 5-30: Activities
    row_idx = 5
    first_date = week_start_date

    for activity in activity_rows:
        # Column A: Date (with formula)
        if row_idx == 5:
            ws.cell(row_idx, 1, activity['date'])
        else:
            days_diff = (activity['date'] - first_date).days
            if days_diff == 0:
                ws.cell(row_idx, 1, f'=A5')
            else:
                ws.cell(row_idx, 1, f'=A5+{days_diff}')

        # Column B: Category
        ws.cell(row_idx, 2, activity['category'])

        # Column C-D: First time block
        ws.cell(row_idx, 3, parse_time(activity['start_time_1']))
        ws.cell(row_idx, 4, parse_time(activity['end_time_1']))

        # Column F-G: Second time block (if present)
        if activity['start_time_2']:
            ws.cell(row_idx, 6, parse_time(activity['start_time_2']))
            ws.cell(row_idx, 7, parse_time(activity['end_time_2']))

        # Column H: Hours formula
        col_c = get_column_letter(3)
        col_d = get_column_letter(4)
        col_f = get_column_letter(6)
        col_g = get_column_letter(7)
        formula = f'=( ({col_d}{row_idx}-{col_c}{row_idx}) * 24) + ( ({col_g}{row_idx}-{col_f}{row_idx}) * 24)'
        ws.cell(row_idx, 8, formula)

        row_idx += 1

    # Row 32: "Weekly totals:"
    ws.cell(32, 1, 'Weekly totals:')

    # Rows 33+: Category totals
    totals_row = 33
    for category in categories:
        # Column A: Category name
        ws.cell(totals_row, 1, category)

        # Column B: SUMIF formula
        formula = f'=ROUND(SUMIF($B$5:$B$30,A{totals_row},$H$5:$H$30), 0)'
        ws.cell(totals_row, 2, formula)

        # Column C: Percentage formula
        first_total = 33
        last_total = 33 + len(categories) - 1
        formula = f'=B{totals_row} / SUM(B${first_total}:B${last_total})'
        ws.cell(totals_row, 3, formula)

        totals_row += 1

    return ws

def parse_time(time_str):
    """Convert 'HH:MM:SS' string to Excel time value"""
    if not time_str:
        return None
    h, m, s = map(int, time_str.split(':'))
    return time(h, m, s)
```

### Step 5: Main Script

```python
def main():
    parser = argparse.ArgumentParser(description='Generate timesheet tab')
    parser.add_argument('--input', '-i', default='categorized-timeline.json')
    parser.add_argument('--workbook', '-w', default='Project-Timesheet.xlsx')
    parser.add_argument('--categories', '-c', default='work-categories.json')
    parser.add_argument('--preview', action='store_true')

    args = parser.parse_args()

    # Load data
    timeline_data = load_categorized_timeline(args.input)

    # Validate categories
    validate_categories(timeline_data['categorized_timeline'], args.categories)

    # Load category list
    with open(args.categories, 'r') as f:
        categories = [cat['name'] for cat in json.load(f)['categories']]

    # Group by date
    by_date = group_by_date(timeline_data['categorized_timeline'])

    # Consolidate to rows
    activity_rows = consolidate_to_rows(by_date)

    if args.preview:
        # Print preview
        print_preview(activity_rows, categories)
    else:
        # Load workbook
        wb = openpyxl.load_workbook(args.workbook)

        # Create sheet
        week_start = datetime.strptime(
            timeline_data['week_range']['start'],
            '%Y-%m-%d'
        ).date()

        create_timesheet_tab(wb, week_start, activity_rows, categories)

        # Save
        wb.save(args.workbook)

        print(f"✓ Created sheet '{week_start}' in {args.workbook}")
```

## Dependencies

```bash
pip install openpyxl
```

## Testing Strategy

1. **Unit tests**: Test each function independently
2. **Sample data**: Create test JSON with known expected output
3. **Formula validation**: Verify Excel formulas calculate correctly
4. **Category matching**: Ensure SUMIF formulas match categories exactly
5. **Edge cases**:
   - Empty days
   - Multiple time blocks
   - Activities spanning midnight
   - Overlapping times

## Next Steps

1. ✅ Document format (TIMESHEET-FORMAT.md)
2. ✅ Plan implementation (this file)
3. ⏳ Implement `generate-timesheet-tab.py`
4. ⏳ Create test data
5. ⏳ Test with real timeline data
6. ⏳ Integrate with LLM categorization workflow

---

**Created:** 2026-01-31
**Last Updated:** 2026-01-31
