/**
 * Convert Outlook Email Extraction JSON to CSV (Browser)
 *
 * Usage:
 *   1. Run the email extraction script
 *   2. Copy the JSON results
 *   3. Run this script with: convertToCSV(jsonData)
 *   4. CSV file will download automatically
 *
 * Or use the all-in-one function:
 *   downloadEmailsAsCSV(jsonData, 'outlook-emails.csv')
 */

function convertToCSV(jsonData) {
  // Handle both direct data and wrapped format
  const emails = jsonData.emails || jsonData;

  if (!emails || emails.length === 0) {
    console.error('No emails found in JSON data');
    return null;
  }

  // CSV headers
  const headers = [
    'Index',
    'Subject',
    'Timestamp',
    'To (Count)',
    'To (Addresses)',
    'Body Preview',
    'Word Count'
  ];

  // Build CSV rows
  const rows = [headers];

  emails.forEach(email => {
    const toAddresses = (email.toAddresses || []).join('; ');

    rows.push([
      email.index || '',
      escapeCSV(email.subject || ''),
      email.timestamp || '',
      email.toCount || 0,
      escapeCSV(toAddresses),
      escapeCSV(email.bodyPreview || ''),
      email.bodyWordCount || 0
    ]);
  });

  // Convert to CSV string
  const csvContent = rows.map(row => row.join(',')).join('\n');

  console.log(`✓ Converted ${emails.length} emails to CSV`);
  return csvContent;
}

function escapeCSV(field) {
  // Escape fields containing commas, quotes, or newlines
  if (typeof field !== 'string') {
    field = String(field);
  }

  if (field.includes(',') || field.includes('"') || field.includes('\n')) {
    // Escape quotes by doubling them
    field = field.replace(/"/g, '""');
    // Wrap in quotes
    return `"${field}"`;
  }

  return field;
}

function downloadCSV(csvContent, filename = 'outlook-emails.csv') {
  // Create blob
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

  // Create download link
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);

  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  console.log(`✓ Downloaded: ${filename}`);
}

function downloadEmailsAsCSV(jsonData, filename = 'outlook-emails.csv') {
  /**
   * All-in-one function: Convert JSON to CSV and download
   *
   * Usage:
   *   const data = { emails: [...] };  // Your extraction results
   *   downloadEmailsAsCSV(data, 'my-emails.csv');
   */

  const csvContent = convertToCSV(jsonData);

  if (csvContent) {
    downloadCSV(csvContent, filename);
    return true;
  }

  return false;
}

// Example usage (uncomment to test):
/*
const sampleData = {
  totalExtracted: 2,
  emails: [
    {
      index: 1,
      subject: "Test Email 1",
      timestamp: "Fri 4:26 PM",
      toAddresses: ["user1@example.com", "user2@example.com"],
      toCount: 2,
      bodyPreview: "This is a test email body...",
      bodyWordCount: 50
    },
    {
      index: 2,
      subject: "Test Email 2",
      timestamp: "Thu 3:15 PM",
      toAddresses: ["user3@example.com"],
      toCount: 1,
      bodyPreview: "Another test email...",
      bodyWordCount: 30
    }
  ]
};

// Convert and download
downloadEmailsAsCSV(sampleData, 'test-emails.csv');
*/

console.log('CSV Converter loaded!');
console.log('Usage: downloadEmailsAsCSV(yourJsonData, "filename.csv")');
