#!/usr/bin/env python3
"""
Interactive Timeline Categorization Tool

Processes timeline data and categorizes each activity with user confirmation.
Uses LLM analysis to suggest categories, user approves/corrects.

Usage:
    python categorize-timeline.py
    python categorize-timeline.py --input timeline-export.json
    python categorize-timeline.py --resume  # Resume from saved progress
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
import os


def load_timeline(input_file):
    """Load timeline JSON"""
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_categories(categories_file='work-categories.json'):
    """Load valid work categories"""
    with open(categories_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data['categories']


def load_progress(progress_file='categorization-progress.json'):
    """Load saved progress if exists"""
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_progress(categorized_entries, progress_file='categorization-progress.json'):
    """Save progress so we can resume later"""
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(categorized_entries, f, indent=2, ensure_ascii=False)


def calculate_duration(entry):
    """Calculate or estimate duration for an activity"""
    if entry['type'] == 'calendar_event':
        # Calendar events have actual times
        time_str = entry.get('time', '')
        if ' - ' in time_str:
            try:
                start_str, end_str = time_str.split(' - ')
                start = datetime.strptime(start_str.strip(), '%I:%M %p')
                end = datetime.strptime(end_str.strip(), '%I:%M %p')
                duration = (end - start).total_seconds() / 3600
                return duration
            except ValueError:
                pass

        # All-day events
        if entry.get('all_day'):
            return 0  # Don't count in timesheet

    elif entry['type'] == 'email_sent':
        # Estimate email time based on body length
        word_count = entry.get('body_word_count', 0)
        if word_count > 100:
            return 0.5  # 30 minutes for long email
        elif word_count > 20:
            return 0.25  # 15 minutes for normal email (default)
        else:
            return 0.1  # 6 minutes for very brief email

    elif entry['type'] == 'teams_message':
        # Estimate Teams message time
        body_length = len(entry.get('body', ''))
        if body_length > 100:
            return 0.15  # 9 minutes for longer message
        else:
            return 0.05  # 3 minutes for quick message

    return 0.25  # Default estimate


def display_activity(entry, index, total):
    """Display activity details for review"""
    print("\n" + "=" * 80)
    print(f"Activity {index}/{total}")
    print("=" * 80)

    # Type and time
    entry_type = entry['type'].replace('_', ' ').title()
    dt = entry.get('datetime', 'Unknown')
    print(f"\n📅 {entry_type} - {dt}")

    if entry['type'] == 'calendar_event':
        print(f"\n   Title: {entry.get('title', 'N/A')}")
        print(f"   Time: {entry.get('time', 'N/A')}")
        if entry.get('location'):
            print(f"   Location: {entry['location'][:60]}...")
        if entry.get('description'):
            desc = entry['description'][:200].replace('\n', ' ')
            print(f"   Description: {desc}...")
        if entry.get('is_canceled'):
            print(f"   ⚠️  CANCELED")

    elif entry['type'] == 'email_sent':
        print(f"\n   Subject: {entry.get('subject', 'N/A')}")
        print(f"   To: {', '.join(entry.get('to_addresses', [])[:3])}")
        if entry.get('body_preview'):
            print(f"   Preview: {entry['body_preview'][:150]}...")

    elif entry['type'] == 'teams_message':
        print(f"\n   Participants: {entry.get('participants', 'N/A')}")
        print(f"   Where: {entry.get('where', 'N/A')}")
        if entry.get('body'):
            print(f"   Message: {entry['body'][:150]}...")


def suggest_category(entry, categories):
    """
    Analyze activity and suggest a category.

    This is where the LLM (Claude) provides intelligent categorization.
    Returns: (suggested_category, confidence, reasoning)

    Note: High-confidence matches can be auto-assigned without user confirmation.
    """

    # Collect all text to analyze
    text_to_analyze = []

    if entry['type'] == 'calendar_event':
        text_to_analyze.append(entry.get('title', ''))
        text_to_analyze.append(entry.get('description', ''))
        text_to_analyze.append(entry.get('location', ''))
    elif entry['type'] == 'email_sent':
        text_to_analyze.append(entry.get('subject', ''))
        text_to_analyze.append(entry.get('body_preview', ''))
    elif entry['type'] == 'teams_message':
        text_to_analyze.append(entry.get('participants', ''))
        text_to_analyze.append(entry.get('body', ''))

    combined_text = ' '.join(text_to_analyze).lower()

    # IMPORTANT: "INC" followed by numbers is just a ticket number format,
    # NOT necessarily incident response. Don't use it for categorization.

    # Keyword matching logic
    matches = []

    for category in categories:
        category_name = category['name']
        keywords = category['keywords']

        # Count keyword matches
        match_count = 0
        matched_keywords = []

        for keyword in keywords:
            if keyword.lower() in combined_text:
                match_count += 1
                matched_keywords.append(keyword)

        if match_count > 0:
            matches.append({
                'category': category_name,
                'match_count': match_count,
                'keywords': matched_keywords
            })

    # Sort by match count
    matches.sort(key=lambda x: x['match_count'], reverse=True)

    if matches:
        best_match = matches[0]
        confidence = "high" if best_match['match_count'] >= 2 else "medium"
        reasoning = f"Matched keywords: {', '.join(best_match['keywords'])}"

        return best_match['category'], confidence, reasoning

    # No keyword matches - make educated guess based on type
    if entry['type'] == 'calendar_event':
        title = entry.get('title', '').lower()
        if 'interview' in title:
            return 'Admin', 'medium', 'Contains "interview" - likely recruiting'
        if 'meeting' in title or 'status' in title:
            return 'Admin', 'low', 'Generic meeting - defaulting to Admin'

    return None, 'none', 'No keyword matches found'


def get_user_confirmation(suggested_category, confidence, reasoning, categories):
    """Prompt user to confirm or change category"""

    print("\n" + "-" * 80)

    if suggested_category:
        print(f"💡 Suggested Category: {suggested_category}")
        print(f"   Confidence: {confidence}")
        print(f"   Reasoning: {reasoning}")
    else:
        print(f"💡 No clear category match")
        print(f"   {reasoning}")

    print("\n" + "-" * 80)
    print("\nOptions:")
    if suggested_category:
        print(f"  [Enter] - Accept suggestion: {suggested_category}")
    print("  [1-9]   - Choose category by number:")

    for idx, cat in enumerate(categories, 1):
        marker = " ← suggested" if cat['name'] == suggested_category else ""
        print(f"            {idx}. {cat['name']}{marker}")

    print(f"  [s]     - Skip this activity")
    print(f"  [q]     - Quit and save progress")

    while True:
        choice = input("\nYour choice: ").strip().lower()

        # Accept suggestion
        if choice == '' and suggested_category:
            return suggested_category

        # Skip
        if choice == 's':
            return None

        # Quit
        if choice == 'q':
            return 'QUIT'

        # Numeric choice
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(categories):
                return categories[idx - 1]['name']
            else:
                print(f"Invalid choice. Please enter 1-{len(categories)}")
                continue

        print("Invalid choice. Please try again.")


def main():
    parser = argparse.ArgumentParser(description='Interactive timeline categorization')
    parser.add_argument('--input', '-i', default='timeline-export.json',
                        help='Input timeline JSON file')
    parser.add_argument('--output', '-o', default='categorized-timeline.json',
                        help='Output categorized timeline JSON file')
    parser.add_argument('--categories', '-c', default='work-categories.json',
                        help='Categories definition file')
    parser.add_argument('--resume', action='store_true',
                        help='Resume from saved progress')
    parser.add_argument('--auto-accept-high-confidence', action='store_true',
                        help='Automatically accept high-confidence categorizations without prompting')

    args = parser.parse_args()

    print("=" * 80)
    print("INTERACTIVE TIMELINE CATEGORIZATION")
    print("=" * 80)
    print()

    # Load data
    print(f"Loading timeline from {args.input}...")
    timeline_data = load_timeline(args.input)

    print(f"Loading categories from {args.categories}...")
    categories = load_categories(args.categories)

    print(f"Found {len(categories)} categories")
    print()

    # Check for saved progress
    categorized_entries = []
    start_index = 0

    if args.resume:
        progress = load_progress()
        if progress:
            categorized_entries = progress
            start_index = len(categorized_entries)
            print(f"Resuming from activity {start_index + 1}")
            print(f"Already categorized: {start_index} activities")
            print()

    timeline = timeline_data['timeline']
    total = len(timeline)

    print(f"Total activities to categorize: {total}")
    if start_index > 0:
        print(f"Remaining: {total - start_index}")
    print()

    # Process each activity
    try:
        for idx in range(start_index, total):
            entry = timeline[idx]

            # Display activity
            display_activity(entry, idx + 1, total)

            # Suggest category
            suggested, confidence, reasoning = suggest_category(entry, categories)

            # Auto-accept high-confidence matches if flag is set
            if args.auto_accept_high_confidence and confidence == 'high' and suggested:
                chosen_category = suggested
                print(f"\n✓ Auto-accepted: {suggested} (high confidence)")
            else:
                # Get user confirmation
                chosen_category = get_user_confirmation(suggested, confidence, reasoning, categories)

            # Handle special responses
            if chosen_category == 'QUIT':
                print("\n💾 Saving progress...")
                save_progress(categorized_entries)
                print(f"✓ Saved {len(categorized_entries)} categorized activities")
                print(f"Run with --resume to continue from activity {len(categorized_entries) + 1}")
                sys.exit(0)

            if chosen_category is None:
                print("⏭️  Skipped")
                continue

            # Calculate duration
            duration = calculate_duration(entry)

            # Create categorized entry
            categorized = entry.copy()
            categorized['category'] = chosen_category
            categorized['duration_hours'] = round(duration, 2)
            categorized['categorization_confidence'] = confidence
            categorized['suggested_category'] = suggested
            categorized['user_confirmed'] = (chosen_category == suggested)

            # Extract time info for timesheet
            if entry['type'] == 'calendar_event':
                time_str = entry.get('time', '')
                if ' - ' in time_str:
                    start_str, end_str = time_str.split(' - ')
                    categorized['start_time'] = start_str.strip()
                    categorized['end_time'] = end_str.strip()
                else:
                    # Estimate time slot
                    dt = datetime.fromisoformat(entry['datetime'])
                    categorized['start_time'] = dt.strftime('%I:%M %p')
                    end_dt = dt + timedelta(hours=duration)
                    categorized['end_time'] = end_dt.strftime('%I:%M %p')
            else:
                # For emails/teams, estimate a time slot
                dt = datetime.fromisoformat(entry['datetime'])
                categorized['start_time'] = dt.strftime('%I:%M %p')
                end_dt = dt + timedelta(hours=duration)
                categorized['end_time'] = end_dt.strftime('%I:%M %p')

            categorized_entries.append(categorized)

            # Auto-save progress periodically
            if len(categorized_entries) % 5 == 0:
                save_progress(categorized_entries)

            print(f"✓ Categorized as: {chosen_category}")

        # All done!
        print("\n" + "=" * 80)
        print("CATEGORIZATION COMPLETE")
        print("=" * 80)
        print()

        # Prepare final output
        output = {
            'export_date': datetime.now().isoformat(),
            'week_range': timeline_data.get('week_range', {}),
            'total_activities': len(categorized_entries),
            'summary': timeline_data.get('summary', {}),
            'metadata': timeline_data.get('metadata', {}),
            'categorized_timeline': categorized_entries
        }

        # Save final result
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved categorized timeline to {args.output}")
        print(f"  Total activities categorized: {len(categorized_entries)}")
        print()

        # Show category breakdown
        category_hours = {}
        total_hours = 0

        for entry in categorized_entries:
            cat = entry['category']
            hours = entry.get('duration_hours', 0)
            category_hours[cat] = category_hours.get(cat, 0) + hours
            total_hours += hours

        # Print tab-separated summary suitable for spreadsheet
        for cat in sorted(category_hours.keys(), key=lambda x: category_hours[x], reverse=True):
            hours = category_hours[cat]
            percentage = (hours / total_hours * 100) if total_hours > 0 else 0
            print(f"{cat}\t{percentage:.1f}\t{hours:.2f}")

        # Clean up progress file
        if os.path.exists('categorization-progress.json'):
            os.remove('categorization-progress.json')
            print("\n✓ Removed progress file")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("💾 Saving progress...")
        save_progress(categorized_entries)
        print(f"✓ Saved {len(categorized_entries)} categorized activities")
        print(f"Run with --resume to continue from activity {len(categorized_entries) + 1}")
        sys.exit(1)


if __name__ == '__main__':
    main()
