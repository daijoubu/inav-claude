/**
 * Outlook Email Extractor - Final Version
 *
 * Checks if emails from "Last week" are loaded, prompts user if not,
 * then extracts To: addresses and body text (first 50 words).
 *
 * Usage: Run via Chrome DevTools MCP when viewing Outlook Sent Items
 */

async function extractOutlookEmails() {
  const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  console.log('='.repeat(80));
  console.log('Outlook Email Extractor');
  console.log('='.repeat(80));

  // STEP 1: Check if we have emails from last week
  console.log('\nStep 1: Checking date range...');

  const emailOptions = Array.from(document.querySelectorAll('[role="listbox"] [role="option"]'));
  console.log(`Found ${emailOptions.length} visible emails`);

  // Check aria-labels to see if we have old enough emails
  const labels = emailOptions.map(opt => opt.getAttribute('aria-label') || '');

  // Look for dates from more than 7 days ago or "Last week" text
  const hasOldEmails = labels.some(label => {
    // Check for explicit "Last week" text or old dates
    if (label.toLowerCase().includes('last week')) return true;

    // Check for dates like "Fri 1/23" (older than this week)
    const dateMatch = label.match(/\d{1,2}\/\d{1,2}/);
    if (dateMatch) return true; // If we see dates in MM/DD format, they're likely older

    return false;
  });

  if (!hasOldEmails && emailOptions.length < 15) {
    console.log('\n⚠️  WARNING: May not have loaded "Last week" emails yet!');
    console.log('\n📋 ACTION REQUIRED:');
    console.log('   Please scroll down in Outlook until you see emails from "Last week"');
    console.log('   (look for dates like "Fri 1/23" or a "Last week" section header)');
    console.log('   Then run this script again.');
    console.log(`\n   Currently showing ${emailOptions.length} emails`);

    return {
      status: 'manual_scroll_needed',
      message: 'Please scroll down to load "Last week" emails, then run again',
      emailsFound: emailOptions.length,
      recommendation: 'Scroll down in the Outlook message list until you see emails from last week or earlier dates'
    };
  }

  console.log('✓ Date range looks good - proceeding with extraction');
  console.log(`  Processing ${emailOptions.length} emails`);

  // STEP 2: Extract details from each email
  console.log('\nStep 2: Extracting email details...');

  const results = [];

  for (let i = 0; i < emailOptions.length; i++) {
    const emailOption = emailOptions[i];
    const ariaLabel = emailOption.getAttribute('aria-label') || '';

    // Click to load in reading pane
    emailOption.click();
    await wait(1500);

    // Extract To: addresses
    let toAddresses = [];
    const toDiv = Array.from(document.querySelectorAll('div'))
      .find(div => {
        const text = div.textContent;
        return text && text.trim().startsWith('To:') && text.length < 1000 && text.length > 3;
      });

    if (toDiv) {
      const toText = toDiv.textContent;
      // Try to extract email addresses first
      const emailMatches = toText.match(/[\w.-]+@[\w.-]+\.[\w.-]+/g);
      if (emailMatches) {
        toAddresses = emailMatches;
      } else {
        // Fallback: extract recipient names
        const cleanText = toText
          .replace(/^To:/, '')
          .replace(/​/g, '')
          .replace(/Cc:.*/g, '')
          .replace(/\d{1,2}\/\d{1,2}\/\d{4}.*$/g, '');

        toAddresses = cleanText.split(/[;,]/)
          .map(n => n.trim())
          .filter(n => n && !n.includes('+') && n.length > 2 && n.length < 60)
          .slice(0, 10);
      }
    }

    // Extract body text
    let bodyText = '';
    const bodyElement = document.querySelector('[role="document"]');
    if (bodyElement) {
      let fullText = bodyElement.textContent.trim();

      // Filter out Outlook "insights" metadata
      // Pattern: "X% of recipients have opened this mail. See more insightsFeedback"
      // Also handles "More than X%" variant
      fullText = fullText.replace(
        /(?:More than )?\d+%\s+of\s+recipients\s+have\s+opened\s+this\s+mail\.\s*See\s+more\s+insights\s*Feedback/gi,
        ''
      );

      // Clean up any extra whitespace from removal
      fullText = fullText.replace(/\s+/g, ' ').trim();

      const words = fullText.split(/\s+/).filter(w => w.length > 0);
      bodyText = words.slice(0, 50).join(' ');
    }

    // Parse subject and timestamp from aria-label
    const timeMatch = ariaLabel.match(/(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{1,2}:\d{2}\s+[AP]M|(\d{1,2}\/\d{1,2}\/\d{2,4})/);

    const subject = ariaLabel
      .split(/Fri |Thu |Wed |Tue |Mon |Sat |Sun |\d{1,2}\/\d{1,2}/)[0]
      .replace(/^Collapsed\s+/, '')
      .replace(/Flagged\s+/, '')
      .replace(/Pinned\s+/, '')
      .replace(/Has attachments\s+/, '')
      .replace(/Meeting accepted\s+/, '')
      .trim()
      .substring(0, 100);

    results.push({
      index: i + 1,
      subject: subject,
      timestamp: timeMatch ? timeMatch[0] : 'Unknown',
      toAddresses: toAddresses,
      toCount: toAddresses.length,
      bodyPreview: bodyText.substring(0, 200),
      bodyWordCount: bodyText.split(/\s+/).filter(w => w).length
    });

    // Progress indicator every 5 emails
    if ((i + 1) % 5 === 0) {
      console.log(`  Processed ${i + 1}/${emailOptions.length} emails...`);
    }

    await wait(400);
  }

  console.log(`\n✓ Completed! Extracted ${results.length} emails.`);
  console.log('='.repeat(80));

  return {
    status: 'success',
    totalExtracted: results.length,
    emails: results
  };
}

// Execute the extraction
extractOutlookEmails();
