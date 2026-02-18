# Outlook Email Extractor

Extracts email details from Outlook Web App using Chrome DevTools Protocol.

## Current Script

**`outlook-extractor-final.js`** - Working email extraction script

- Extracts emails from Outlook Sent Items
- **Clicks through each email** to load full details
- Extracts To: addresses and first 50 words of body
- Stops at "Last week" section
- Returns JSON output

## Key Findings

### About the 13 Email Limit

**Q: Was 13 a limit you set in the script?**

**A: No.** The 13 emails is the number currently loaded in the browser DOM without scrolling. Outlook uses **lazy loading** - it only renders emails that are visible or near the viewport. To get more emails, you would need to:

1. Scroll down to load more emails into the DOM
2. Then run the extraction script again
3. Or modify the script to scroll automatically

## Usage

### Prerequisites

```bash
# Start Chrome with remote debugging
google-chrome --remote-debugging-port=9222

# Open Outlook and navigate to Sent Items
# https://outlook.office.com/mail/sentitems
```

### Quick Test (First 5 Emails)

Use Claude Code's MCP server to run:

```javascript
async () => {
  const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));
  const emailOptions = Array.from(document.querySelectorAll('[role="listbox"] [role="option"]'));
  const results = [];

  for (let i = 0; i < Math.min(5, emailOptions.length); i++) {
    const emailOption = emailOptions[i];
    emailOption.click();
    await wait(2000);

    // Extract To: addresses
    let toAddresses = [];
    const toDiv = Array.from(document.querySelectorAll('div'))
      .find(div => div.textContent?.trim().startsWith('To:') && div.textContent.length < 1000);

    if (toDiv) {
      const emailMatches = toDiv.textContent.match(/[\\w.-]+@[\\w.-]+\\.[\\w.-]+/g);
      toAddresses = emailMatches || [];
    }

    // Extract body
    const bodyElement = document.querySelector('[role="document"]');
    const bodyText = bodyElement ?
      bodyElement.textContent.trim().split(/\\s+/).slice(0, 50).join(' ') : '';

    results.push({
      index: i + 1,
      toAddresses: toAddresses,
      bodyPreview: bodyText.substring(0, 150)
    });
  }

  return { count: results.length, emails: results };
}
```

## What Gets Extracted

For each email:

```json
{
  "index": 1,
  "subject": "Velox Sonarqube scan results remediation",
  "timestamp": "12/18/2025",
  "toAddresses": [
    "tony@whitespaces.design",
    "richard.estrella@estrellainsurance.com"
  ],
  "toCount": 2,
  "bodyPreview": "Yes sir, I mis-clicked. I just updated the invitation...",
  "bodyWordCount": 50
}
```

## Important Notes

### Visible Emails Only

The script can only extract emails that are:
1. **Currently in the DOM** (loaded by Outlook's lazy loader)
2. Typically ~10-15 emails without scrolling
3. More emails appear as you scroll down

### To Get All Sent Items

Option 1: **Scroll then extract**
- Manually scroll to bottom of Sent Items
- This loads more emails into the DOM
- Then run extraction

Option 2: **Auto-scroll script**
```javascript
// Scroll to load all emails first
async function scrollToLoadAll() {
  const list = document.querySelector('[role="listbox"]').parentElement;
  let lastCount = 0;

  while (true) {
    const currentCount = document.querySelectorAll('[role="option"]').length;
    if (currentCount === lastCount) break; // No new emails loaded

    lastCount = currentCount;
    list.scrollTo(0, list.scrollHeight);
    await new Promise(r => setTimeout(r, 2000)); // Wait for load
  }

  return currentCount;
}

await scrollToLoadAll(); // Run this first
// Then run extraction script
```

### Meeting Invites

Meeting acceptance emails may not have body text - they show "No preview available" in the list view.

## Files

1. `outlook-extractor-final.js` - Email extraction script (working version)
2. `convert-to-csv.py` - Convert JSON to CSV (Python)
3. `convert-to-csv.js` - Convert JSON to CSV (Browser)
4. `outlook-extractor-README.md` - This file

## Next Steps

To extract **all** sent items (not just visible 13):

1. Add auto-scroll functionality to load all emails
2. Run extraction in batches
3. Save results to CSV or JSON file

Example batch processing:
```python
# Process in chunks of 20 emails
import json

all_results = []
chunk_size = 20

for start in range(0, total_emails, chunk_size):
    # Extract chunk
    result = extract_emails(start, start + chunk_size)
    all_results.extend(result['emails'])

# Save to file
with open('sent_items.json', 'w') as f:
    json.dump(all_results, f, indent=2)
```
