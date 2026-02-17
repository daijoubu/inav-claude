
## Email Parser Improvements

- [x] Filter out Outlook "insights" messages from body preview:
  - Pattern: "X% of recipients have opened this mail. See more insightsFeedback"
  - Examples found:
    - "45% of recipients have opened this mail. See more insightsFeedback"
    - "More than 75% of recipients have opened this mail. See more insightsFeedback"
    - "42% of recipients have opened this mail. See more insightsFeedback"
  - These are Outlook metadata, not actual email content
  - ✓ DONE: Added regex filter in outlook-extractor-final.js to strip these before taking first 50 words


## Categorization Script Updates (DONE)

- [x] Added note: "INC" ticket numbers are NOT necessarily incident response
- [x] Added `--auto-accept-high-confidence` flag to skip prompts for high-confidence matches
- [x] Usage for future runs: `python categorize-timeline.py --auto-accept-high-confidence`

This will only prompt for:
- Low/medium confidence matches
- No keyword matches found
- Ambiguous cases

