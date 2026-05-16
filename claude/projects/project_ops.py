#!/usr/bin/env python3
"""
Project Operations - Atomic project lifecycle operations

Prevents drift between INDEX.md, completed/INDEX.md, and directory structure
by performing all related changes in a single operation.

Commands:
    complete <project>    Move project to completed (dir + both indexes)
    block <project>       Move project to blocked (dir + index status)
    backburner <project>  Move project to backburner (dir + index status)
    resume <project>      Move project back to active (from blocked/backburner)
    cancel <project>      Move project to completed as cancelled
    audit                 Check for inconsistencies between dirs and indexes
    audit --fix           Fix simple inconsistencies automatically
"""

import re
import sys
import shutil
from pathlib import Path
from datetime import date


PROJECTS_DIR = Path(__file__).parent
INDEX_PATH = PROJECTS_DIR / "INDEX.md"
COMPLETED_INDEX_PATH = PROJECTS_DIR / "completed" / "INDEX.md"
ACTIVE_DIR = PROJECTS_DIR / "active"
COMPLETED_DIR = PROJECTS_DIR / "completed"
BLOCKED_DIR = PROJECTS_DIR / "blocked"
BACKBURNER_DIR = PROJECTS_DIR / "backburner"

# Emoji used in INDEX.md headers
STATUS_EMOJI = {
    'TODO': '📋',
    'IN_PROGRESS': '🚧',
    'BLOCKED': '🚫',
    'BACKBURNER': '⏸️',
    'COMPLETED': '✅',
    'CANCELLED': '❌',
}

# Reverse map (emoji -> status); handle multi-byte emoji
EMOJI_STATUS = {}
for status, emoji in STATUS_EMOJI.items():
    EMOJI_STATUS[emoji] = status


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)


def find_entry_bounds(content, project_name):
    """Find the start and end of a project entry in INDEX.md.

    Returns (start, end) character positions, or (None, None) if not found.
    The range includes the entry header through the trailing '---' separator.
    """
    # Match the project header line with any status emoji
    pattern = re.compile(
        r'^### (?:' + '|'.join(re.escape(e) for e in STATUS_EMOJI.values()) + r') '
        + re.escape(project_name) + r'\s*$',
        re.MULTILINE
    )
    match = pattern.search(content)
    if not match:
        return None, None

    start = match.start()

    # Find the next project header or end-of-section marker after this entry
    next_header = re.compile(
        r'^### (?:' + '|'.join(re.escape(e) for e in STATUS_EMOJI.values()) + r') ',
        re.MULTILINE
    )
    rest = content[match.end():]
    next_match = next_header.search(rest)

    if next_match:
        # End is just before the next header
        end = match.end() + next_match.start()
    else:
        # No next header — find the next '---' or section marker
        section_marker = re.search(r'^\*\*Note:\*\*|^## Completed|^---\s*\n\s*\n(?:## |\*\*)', rest, re.MULTILINE)
        if section_marker:
            end = match.end() + section_marker.start()
        else:
            end = len(content)

    # Trim trailing whitespace/separators
    chunk = content[start:end]
    # Remove trailing '---' and blank lines
    chunk = re.sub(r'\n---\s*\n*$', '\n', chunk)

    return start, start + len(chunk)


def remove_entry_from_index(index_path, project_name):
    """Remove a project entry from an INDEX.md file. Returns the removed text."""
    content = read_file(index_path)
    start, end = find_entry_bounds(content, project_name)
    if start is None:
        return None

    removed = content[start:end]

    # Remove the entry and its trailing separator
    # Look for the --- separator after the entry
    after_entry = content[end:]
    after_entry = re.sub(r'^\s*---\s*\n?', '', after_entry, count=1)

    new_content = content[:start] + after_entry
    # Clean up double blank lines
    new_content = re.sub(r'\n{3,}', '\n\n', new_content)

    write_file(index_path, new_content)
    return removed


def update_index_counts(index_path):
    """Recount projects by status and update the header counts."""
    content = read_file(index_path)

    if index_path == INDEX_PATH:
        # Count by status emoji in active INDEX
        active = 0
        backburner = 0
        blocked = 0
        for emoji, status in EMOJI_STATUS.items():
            count = len(re.findall(r'^### ' + re.escape(emoji) + r' ', content, re.MULTILINE))
            if status in ('TODO', 'IN_PROGRESS'):
                active += count
            elif status == 'BACKBURNER':
                backburner += count
            elif status == 'BLOCKED':
                blocked += count

        # Update the counts line
        content = re.sub(
            r'\*\*Active:\*\* \d+ \| \*\*Backburner:\*\* \d+ \| \*\*Blocked:\*\* \d+',
            f'**Active:** {active} | **Backburner:** {backburner} | **Blocked:** {blocked}',
            content
        )
        # Update date
        content = re.sub(
            r'\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}',
            f'**Last Updated:** {date.today().isoformat()}',
            content
        )

    elif index_path == COMPLETED_INDEX_PATH:
        completed = len(re.findall(r'^### ✅', content, re.MULTILINE))
        cancelled = len(re.findall(r'^### ❌', content, re.MULTILINE))
        content = re.sub(
            r'\*\*Total Completed:\*\* \d+',
            f'**Total Completed:** {completed}',
            content
        )
        content = re.sub(
            r'\*\*Total Cancelled:\*\* \d+',
            f'**Total Cancelled:** {cancelled}',
            content
        )

    write_file(index_path, content)


def add_entry_to_completed_index(project_name, summary_line, project_type=None,
                                  priority=None, pr_info=None):
    """Add a concise entry to completed/INDEX.md."""
    content = read_file(COMPLETED_INDEX_PATH)

    # Build the entry
    today = date.today().isoformat()
    entry = f"\n### ✅ {project_name}\n\n"
    entry += f"**Status:** COMPLETED ({today})\n"
    if project_type:
        entry += f"**Type:** {project_type}\n"
    if priority:
        entry += f"**Priority:** {priority}\n"
    entry += f"\n{summary_line}\n\n---\n"

    # Insert after the header (after the first '---' line)
    first_sep = content.find('\n---\n')
    if first_sep != -1:
        insert_pos = first_sep + 5  # after '---\n'
        content = content[:insert_pos] + '\n' + entry + content[insert_pos:]
    else:
        content += '\n' + entry

    write_file(COMPLETED_INDEX_PATH, content)


def add_cancelled_to_completed_index(project_name, reason):
    """Add a cancelled entry to completed/INDEX.md."""
    content = read_file(COMPLETED_INDEX_PATH)

    today = date.today().isoformat()
    entry = f"\n### ❌ {project_name} ({today})\n\n"
    entry += f"**Cancelled:** {reason}\n\n---\n"

    first_sep = content.find('\n---\n')
    if first_sep != -1:
        insert_pos = first_sep + 5
        content = content[:insert_pos] + '\n' + entry + content[insert_pos:]
    else:
        content += '\n' + entry

    write_file(COMPLETED_INDEX_PATH, content)


def extract_metadata_from_entry(entry_text):
    """Extract type, priority, and summary from an INDEX entry."""
    project_type = None
    priority = None
    summary = None

    type_match = re.search(r'\*\*Type:\*\* ([^|*\n]+)', entry_text)
    if type_match:
        project_type = type_match.group(1).strip()

    prio_match = re.search(r'\*\*Priority:\*\* ([^|*\n]+)', entry_text)
    if prio_match:
        priority = prio_match.group(1).strip()

    # Summary is the first non-metadata, non-blank line
    for line in entry_text.split('\n'):
        line = line.strip()
        if (line and not line.startswith('#') and not line.startswith('**')
                and not line.startswith('---') and not line.startswith('|')):
            summary = line
            break

    return project_type, priority, summary


def extract_summary_from_dir(project_dir):
    """Try to extract a one-line summary from a project's summary.md."""
    summary_path = project_dir / "summary.md"
    if not summary_path.exists():
        return None, None, None

    content = read_file(summary_path)
    project_type = None
    priority = None
    summary = None

    type_match = re.search(r'\*\*Type:\*\* (.+)', content)
    if type_match:
        project_type = type_match.group(1).strip()

    prio_match = re.search(r'\*\*Priority:\*\* (.+)', content)
    if prio_match:
        priority = prio_match.group(1).strip()

    # Look for Overview section
    overview_match = re.search(r'## Overview\s*\n+(.+)', content)
    if overview_match:
        summary = overview_match.group(1).strip()
    else:
        # Fall back to first non-header, non-metadata line
        for line in content.split('\n'):
            line = line.strip()
            if (line and not line.startswith('#') and not line.startswith('**')
                    and not line.startswith('---') and not line.startswith('-')):
                summary = line
                break

    return project_type, priority, summary


def find_project_dir(project_name):
    """Find which directory a project lives in. Returns (path, location_type) or (None, None)."""
    for dirname, loc_type in [(ACTIVE_DIR, 'active'), (BLOCKED_DIR, 'blocked'),
                               (BACKBURNER_DIR, 'backburner'), (COMPLETED_DIR, 'completed')]:
        candidate = dirname / project_name
        if candidate.is_dir():
            return candidate, loc_type
    return None, None


def move_project_dir(project_name, from_dir, to_dir):
    """Move a project directory. Returns True on success."""
    src = from_dir / project_name
    dst = to_dir / project_name

    if not src.is_dir():
        print(f"  ERROR: Source directory not found: {src}")
        return False

    if dst.exists():
        print(f"  ERROR: Destination already exists: {dst}")
        print(f"  This is a duplicate — resolve manually.")
        return False

    to_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return True


def update_directory_reference(index_path, project_name, new_location):
    """Update the Directory: reference in an INDEX entry."""
    content = read_file(index_path)
    # Match Directory or Project Directory or Location references
    content = re.sub(
        r'(\*\*(?:Directory|Project Directory|Location):\*\* `)([^`]+)(`)',
        lambda m: m.group(1) + new_location + m.group(3),
        content
    )
    write_file(index_path, content)


def update_entry_status(index_path, project_name, new_emoji, new_status_text):
    """Update the status emoji and text in an INDEX entry header."""
    content = read_file(index_path)

    # Update the header line emoji
    old_pattern = re.compile(
        r'^(### )(?:' + '|'.join(re.escape(e) for e in STATUS_EMOJI.values()) + r')( '
        + re.escape(project_name) + r')\s*$',
        re.MULTILINE
    )
    content = old_pattern.sub(f'\\g<1>{new_emoji}\\g<2>', content)

    # Update Status field
    start, end = find_entry_bounds(content, project_name)
    if start is not None:
        entry = content[start:end]
        entry = re.sub(
            r'(\*\*Status:\*\* )[^|*\n]+',
            f'\\g<1>{new_status_text}',
            entry, count=1
        )
        content = content[:start] + entry + content[end:]

    write_file(index_path, content)


# ============================================================
# Commands
# ============================================================

def cmd_complete(project_name):
    """Complete a project: move dir, remove from INDEX, add to completed/INDEX."""
    print(f"\nCompleting project: {project_name}")

    # 1. Find the project directory
    proj_dir, loc_type = find_project_dir(project_name)
    if proj_dir is None:
        print(f"  WARNING: No directory found for '{project_name}'")
    elif loc_type == 'completed':
        print(f"  Directory already in completed/")
    else:
        # Move to completed
        print(f"  Moving directory: {loc_type}/ -> completed/")
        if not move_project_dir(project_name, proj_dir.parent, COMPLETED_DIR):
            print("  ABORTED: Could not move directory.")
            return False

    # 2. Get metadata from INDEX entry before removing
    content = read_file(INDEX_PATH)
    start, end = find_entry_bounds(content, project_name)
    if start is not None:
        entry_text = content[start:end]
        project_type, priority, summary = extract_metadata_from_entry(entry_text)
    else:
        # Try from summary.md
        completed_path = COMPLETED_DIR / project_name
        if completed_path.is_dir():
            project_type, priority, summary = extract_summary_from_dir(completed_path)
        else:
            project_type, priority, summary = None, None, None

    # 3. Remove from active INDEX
    removed = remove_entry_from_index(INDEX_PATH, project_name)
    if removed:
        print(f"  Removed from INDEX.md")
    else:
        print(f"  Not found in INDEX.md (already removed?)")

    # 4. Check if already in completed INDEX
    completed_content = read_file(COMPLETED_INDEX_PATH)
    if re.search(r'^### ✅ ' + re.escape(project_name), completed_content, re.MULTILINE):
        print(f"  Already in completed/INDEX.md")
    else:
        summary = summary or f"Completed project: {project_name}"
        add_entry_to_completed_index(project_name, summary, project_type, priority)
        print(f"  Added to completed/INDEX.md")

    # 5. Update counts
    update_index_counts(INDEX_PATH)
    update_index_counts(COMPLETED_INDEX_PATH)
    print(f"  Updated counts in both indexes")

    print(f"  DONE")
    return True


def cmd_cancel(project_name, reason=None):
    """Cancel a project: move dir to completed, update indexes."""
    print(f"\nCancelling project: {project_name}")

    reason = reason or "Cancelled"

    # 1. Find and move directory
    proj_dir, loc_type = find_project_dir(project_name)
    if proj_dir and loc_type != 'completed':
        print(f"  Moving directory: {loc_type}/ -> completed/")
        if not move_project_dir(project_name, proj_dir.parent, COMPLETED_DIR):
            print("  ABORTED: Could not move directory.")
            return False

    # 2. Remove from active INDEX
    removed = remove_entry_from_index(INDEX_PATH, project_name)
    if removed:
        print(f"  Removed from INDEX.md")

    # 3. Add to completed INDEX as cancelled
    completed_content = read_file(COMPLETED_INDEX_PATH)
    if re.search(r'^### ❌ ' + re.escape(project_name), completed_content, re.MULTILINE):
        print(f"  Already in completed/INDEX.md")
    else:
        add_cancelled_to_completed_index(project_name, reason)
        print(f"  Added to completed/INDEX.md as cancelled")

    # 4. Update counts
    update_index_counts(INDEX_PATH)
    update_index_counts(COMPLETED_INDEX_PATH)
    print(f"  DONE")
    return True


def cmd_block(project_name, reason=None):
    """Block a project: move dir to blocked/, update INDEX status."""
    print(f"\nBlocking project: {project_name}")

    proj_dir, loc_type = find_project_dir(project_name)
    if proj_dir is None:
        print(f"  ERROR: No directory found for '{project_name}'")
        return False
    if loc_type == 'blocked':
        print(f"  Directory already in blocked/")
    elif loc_type in ('active', 'backburner'):
        print(f"  Moving directory: {loc_type}/ -> blocked/")
        if not move_project_dir(project_name, proj_dir.parent, BLOCKED_DIR):
            return False
    else:
        print(f"  ERROR: Cannot block from {loc_type}/")
        return False

    # Update INDEX entry
    update_entry_status(INDEX_PATH, project_name, STATUS_EMOJI['BLOCKED'], 'BLOCKED')
    update_directory_reference(INDEX_PATH, project_name, f'blocked/{project_name}/')

    if reason:
        # Add blocked since date and reason
        content = read_file(INDEX_PATH)
        start, end = find_entry_bounds(content, project_name)
        if start is not None:
            entry = content[start:end]
            today = date.today().isoformat()
            if '**Blocked Since:**' not in entry:
                # Add after Created line
                entry = re.sub(
                    r'(\*\*Created:\*\* [^\n]+)',
                    f'\\g<1>\n**Blocked Since:** {today}',
                    entry, count=1
                )
            if '**Blocking Issue:**' not in entry:
                entry += f"\n**Blocking Issue:** {reason}\n"
            content = content[:start] + entry + content[end:]
            write_file(INDEX_PATH, content)

    update_index_counts(INDEX_PATH)
    print(f"  DONE")
    return True


def cmd_backburner(project_name):
    """Move a project to backburner."""
    print(f"\nMoving to backburner: {project_name}")

    proj_dir, loc_type = find_project_dir(project_name)
    if proj_dir is None:
        print(f"  ERROR: No directory found for '{project_name}'")
        return False
    if loc_type == 'backburner':
        print(f"  Directory already in backburner/")
    elif loc_type in ('active', 'blocked'):
        print(f"  Moving directory: {loc_type}/ -> backburner/")
        if not move_project_dir(project_name, proj_dir.parent, BACKBURNER_DIR):
            return False
    else:
        print(f"  ERROR: Cannot backburner from {loc_type}/")
        return False

    update_entry_status(INDEX_PATH, project_name, STATUS_EMOJI['BACKBURNER'], 'BACKBURNER')
    update_directory_reference(INDEX_PATH, project_name, f'backburner/{project_name}/')
    update_index_counts(INDEX_PATH)
    print(f"  DONE")
    return True


def cmd_resume(project_name):
    """Resume a project from blocked or backburner back to active."""
    print(f"\nResuming project: {project_name}")

    proj_dir, loc_type = find_project_dir(project_name)
    if proj_dir is None:
        print(f"  ERROR: No directory found for '{project_name}'")
        return False
    if loc_type == 'active':
        print(f"  Directory already in active/")
    elif loc_type in ('blocked', 'backburner'):
        print(f"  Moving directory: {loc_type}/ -> active/")
        if not move_project_dir(project_name, proj_dir.parent, ACTIVE_DIR):
            return False
    else:
        print(f"  ERROR: Cannot resume from {loc_type}/")
        return False

    update_entry_status(INDEX_PATH, project_name, STATUS_EMOJI['IN_PROGRESS'], 'IN PROGRESS')
    update_directory_reference(INDEX_PATH, project_name, f'active/{project_name}/')
    update_index_counts(INDEX_PATH)
    print(f"  DONE")
    return True


def cmd_audit(fix=False):
    """Check for inconsistencies between directories and indexes."""
    print("\n=== Project Audit ===\n")
    issues = []

    # Parse active INDEX
    index_content = read_file(INDEX_PATH)
    index_projects = {}
    for match in re.finditer(
        r'^### (' + '|'.join(re.escape(e) for e in STATUS_EMOJI.values()) + r') (.+?)\s*$',
        index_content, re.MULTILINE
    ):
        emoji = match.group(1)
        name = match.group(2)
        status = EMOJI_STATUS.get(emoji, 'UNKNOWN')
        index_projects[name] = status

    # Parse completed INDEX
    completed_content = read_file(COMPLETED_INDEX_PATH)
    completed_indexed = set()
    for match in re.finditer(r'^### [✅❌] (.+?)(?:\s*\(.*\))?\s*$', completed_content, re.MULTILINE):
        completed_indexed.add(match.group(1))

    # Scan directories
    dir_locations = {}  # project_name -> set of locations
    for dirname, loc_type in [(ACTIVE_DIR, 'active'), (BLOCKED_DIR, 'blocked'),
                               (BACKBURNER_DIR, 'backburner'), (COMPLETED_DIR, 'completed')]:
        if dirname.is_dir():
            for d in dirname.iterdir():
                if d.is_dir() and d.name != '__pycache__':
                    dir_locations.setdefault(d.name, set()).add(loc_type)

    # Check 1: Projects in multiple directories (duplicates)
    duplicates = {name: locs for name, locs in dir_locations.items() if len(locs) > 1}
    if duplicates:
        print(f"DUPLICATES: {len(duplicates)} projects exist in multiple directories")
        for name, locs in sorted(duplicates.items()):
            print(f"  {name}: {', '.join(sorted(locs))}")
            if fix and 'completed' in locs:
                for loc in locs - {'completed'}:
                    loc_dir = {'active': ACTIVE_DIR, 'blocked': BLOCKED_DIR,
                               'backburner': BACKBURNER_DIR}[loc]
                    stale_dir = loc_dir / name
                    print(f"    FIX: Removing stale {loc}/{name}/ (completed copy exists)")
                    shutil.rmtree(str(stale_dir))
        issues.append(('DUPLICATES', len(duplicates)))
    else:
        print("DUPLICATES: None found")

    # Check 2: Active INDEX entries pointing to completed projects
    completed_in_index = []
    for name, status in index_projects.items():
        if name in dir_locations and 'completed' in dir_locations[name]:
            if 'active' not in dir_locations.get(name, set()) and \
               'blocked' not in dir_locations.get(name, set()) and \
               'backburner' not in dir_locations.get(name, set()):
                completed_in_index.append(name)
    if completed_in_index:
        print(f"\nCOMPLETED IN ACTIVE INDEX: {len(completed_in_index)} entries should be removed")
        for name in sorted(completed_in_index):
            print(f"  {name}")
            if fix:
                removed = remove_entry_from_index(INDEX_PATH, name)
                if removed:
                    print(f"    FIX: Removed from INDEX.md")
        issues.append(('COMPLETED_IN_INDEX', len(completed_in_index)))
    else:
        print("\nCOMPLETED IN ACTIVE INDEX: None found")

    # Check 3: INDEX entries with no directory anywhere
    orphan_entries = []
    for name in index_projects:
        if name not in dir_locations:
            orphan_entries.append(name)
    if orphan_entries:
        print(f"\nORPHAN INDEX ENTRIES: {len(orphan_entries)} entries have no directory")
        for name in sorted(orphan_entries):
            status = index_projects[name]
            print(f"  {name} (status: {status})")
            if fix:
                expected_dir = ACTIVE_DIR / name
                if status == 'BLOCKED':
                    expected_dir = BLOCKED_DIR / name
                elif status == 'BACKBURNER':
                    expected_dir = BACKBURNER_DIR / name
                expected_dir.mkdir(parents=True, exist_ok=True)
                print(f"    FIX: Created {expected_dir.relative_to(PROJECTS_DIR)}/")
        issues.append(('ORPHAN_ENTRIES', len(orphan_entries)))
    else:
        print("\nORPHAN INDEX ENTRIES: None found")

    # Check 4: Status/location mismatches
    status_dir_map = {
        'TODO': 'active', 'IN_PROGRESS': 'active',
        'BLOCKED': 'blocked', 'BACKBURNER': 'backburner'
    }
    mismatches = []
    for name, status in index_projects.items():
        expected_loc = status_dir_map.get(status)
        if expected_loc and name in dir_locations:
            actual_locs = dir_locations[name]
            if expected_loc not in actual_locs and len(actual_locs) == 1:
                actual = next(iter(actual_locs))
                if actual != 'completed':  # completed is handled separately
                    mismatches.append((name, status, expected_loc, actual))
    if mismatches:
        print(f"\nSTATUS/LOCATION MISMATCHES: {len(mismatches)} projects in wrong directory")
        for name, status, expected, actual in mismatches:
            print(f"  {name}: status={status} -> expected {expected}/, found in {actual}/")
            if fix:
                from_dir = {'active': ACTIVE_DIR, 'blocked': BLOCKED_DIR,
                            'backburner': BACKBURNER_DIR}[actual]
                to_dir = {'active': ACTIVE_DIR, 'blocked': BLOCKED_DIR,
                          'backburner': BACKBURNER_DIR}[expected]
                if move_project_dir(name, from_dir, to_dir):
                    update_directory_reference(INDEX_PATH, name, f'{expected}/{name}/')
                    print(f"    FIX: Moved {actual}/{name}/ -> {expected}/{name}/")
        issues.append(('MISMATCHES', len(mismatches)))
    else:
        print("\nSTATUS/LOCATION MISMATCHES: None found")

    # Check 5: Completed directories missing from completed/INDEX.md
    missing_completed = []
    for name in sorted(dir_locations):
        if 'completed' in dir_locations[name] and name not in completed_indexed:
            missing_completed.append(name)
    if missing_completed:
        print(f"\nMISSING FROM COMPLETED INDEX: {len(missing_completed)} directories not indexed")
        for name in missing_completed:
            print(f"  {name}")
            if fix:
                proj_dir = COMPLETED_DIR / name
                project_type, priority, summary = extract_summary_from_dir(proj_dir)
                summary = summary or f"Completed project: {name}"
                add_entry_to_completed_index(name, summary, project_type, priority)
                print(f"    FIX: Added to completed/INDEX.md")
        issues.append(('MISSING_COMPLETED', len(missing_completed)))
    else:
        print("\nMISSING FROM COMPLETED INDEX: None found")

    # Check 6: Verify INDEX.md counts match reality
    print(f"\nCOUNT VERIFICATION:")
    active_count = sum(1 for s in index_projects.values() if s in ('TODO', 'IN_PROGRESS'))
    backburner_count = sum(1 for s in index_projects.values() if s == 'BACKBURNER')
    blocked_count = sum(1 for s in index_projects.values() if s == 'BLOCKED')

    count_match = re.search(
        r'\*\*Active:\*\* (\d+) \| \*\*Backburner:\*\* (\d+) \| \*\*Blocked:\*\* (\d+)',
        index_content
    )
    if count_match:
        stated_active = int(count_match.group(1))
        stated_backburner = int(count_match.group(2))
        stated_blocked = int(count_match.group(3))

        if (stated_active, stated_backburner, stated_blocked) == (active_count, backburner_count, blocked_count):
            print(f"  INDEX.md counts correct: Active={active_count}, Backburner={backburner_count}, Blocked={blocked_count}")
        else:
            print(f"  INDEX.md counts WRONG:")
            print(f"    Stated:  Active={stated_active}, Backburner={stated_backburner}, Blocked={stated_blocked}")
            print(f"    Actual:  Active={active_count}, Backburner={backburner_count}, Blocked={blocked_count}")
            if fix:
                update_index_counts(INDEX_PATH)
                print(f"    FIX: Updated counts")
            issues.append(('WRONG_COUNTS', 1))
    else:
        print(f"  Could not find counts in INDEX.md header")

    # Summary
    print(f"\n{'='*50}")
    if issues:
        total = sum(count for _, count in issues)
        print(f"TOTAL ISSUES: {total}")
        if fix:
            print(f"Applied automatic fixes where possible.")
        else:
            print(f"Run with --fix to auto-fix simple issues.")
    else:
        print("ALL CLEAN - no inconsistencies found")

    return len(issues) == 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'complete':
        if len(sys.argv) < 3:
            print("Usage: project_ops.py complete <project-name>")
            sys.exit(1)
        cmd_complete(sys.argv[2])

    elif command == 'cancel':
        if len(sys.argv) < 3:
            print("Usage: project_ops.py cancel <project-name> [reason]")
            sys.exit(1)
        reason = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else None
        cmd_cancel(sys.argv[2], reason)

    elif command == 'block':
        if len(sys.argv) < 3:
            print("Usage: project_ops.py block <project-name> [reason]")
            sys.exit(1)
        reason = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else None
        cmd_block(sys.argv[2], reason)

    elif command == 'backburner':
        if len(sys.argv) < 3:
            print("Usage: project_ops.py backburner <project-name>")
            sys.exit(1)
        cmd_backburner(sys.argv[2])

    elif command == 'resume':
        if len(sys.argv) < 3:
            print("Usage: project_ops.py resume <project-name>")
            sys.exit(1)
        cmd_resume(sys.argv[2])

    elif command == 'audit':
        fix = '--fix' in sys.argv
        cmd_audit(fix=fix)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
