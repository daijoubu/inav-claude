#!/usr/bin/env python3
"""
Add sandbox-aware error handling to MSPApi scripts.

This script carefully adds try-except blocks around api.open() calls
in scripts that use mspapi2.MSPApi.

Safety features:
- Dry-run mode by default
- Shows exactly what will be changed
- Skips files that already have error handling
- Creates backups before modifying
- Detailed reporting
"""

import os
import sys
import re
import argparse
from pathlib import Path
import difflib


def find_mspapi_files(root_dir):
    """Find all Python files that use MSPApi."""
    mspapi_files = []
    root_path = Path(root_dir)

    for py_file in root_path.rglob("*.py"):
        # Skip this script itself
        if 'add_mspapi_sandbox_errors.py' in str(py_file):
            continue

        try:
            content = py_file.read_text()
            if 'MSPApi(' in content and 'api.open()' in content:
                mspapi_files.append(py_file)
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}")

    return mspapi_files


def analyze_file(file_path):
    """
    Analyze a file to see if it needs updating.

    Returns:
        (needs_update, reason, line_number, context)
    """
    content = file_path.read_text()
    lines = content.split('\n')

    # Find api.open() calls
    for i, line in enumerate(lines):
        if 'api.open()' in line:
            # Check if it's already wrapped in error handling
            # Look backwards for try: or except
            already_wrapped = False

            # Check 5 lines before
            for j in range(max(0, i-5), i):
                if 'try:' in lines[j] and 'api.open()' in lines[i]:
                    # Check if there's a sandbox-aware message after
                    for k in range(i, min(len(lines), i+10)):
                        if 'sandboxed environment' in lines[k]:
                            already_wrapped = True
                            break

            if already_wrapped:
                return False, "Already has sandbox-aware error handling", i+1, None

            # Check if this api.open() is already in a try block (but without sandbox message)
            in_try_block = False
            for j in range(max(0, i-10), i):
                if re.match(r'^\s*try:\s*$', lines[j]):
                    in_try_block = True
                    break

            if in_try_block:
                return False, "Already in try block (may need manual review)", i+1, None

            # Find the indentation level
            match = re.match(r'^(\s*)', line)
            indent = match.group(1) if match else ''

            # Get context (5 lines before and after)
            start = max(0, i-5)
            end = min(len(lines), i+6)
            context = '\n'.join([f"{j+1:4}: {lines[j]}" for j in range(start, end)])

            return True, "Needs sandbox-aware error handling", i+1, indent

    return False, "No api.open() found", 0, None


def generate_patch(file_path, line_number, indent):
    """Generate the patch for a file."""
    content = file_path.read_text()
    lines = content.split('\n')

    # Find the api.open() line
    api_open_line_idx = None
    for i, line in enumerate(lines):
        if 'api.open()' in line and i+1 == line_number:
            api_open_line_idx = i
            break

    if api_open_line_idx is None:
        return None, None

    # Collect lines from api.open() until we find something that's not part of the connection setup
    # Typically: api.open(), time.sleep(), maybe a print
    end_idx = api_open_line_idx
    for i in range(api_open_line_idx + 1, min(len(lines), api_open_line_idx + 5)):
        line = lines[i].strip()
        if line.startswith('time.sleep(') or line.startswith('print('):
            end_idx = i
        else:
            break

    # Extract the lines to wrap
    old_lines = lines[api_open_line_idx:end_idx+1]
    old_text = '\n'.join(old_lines)

    # Build new lines with try-except
    new_lines = []
    new_lines.append(f"{indent}try:")
    for line in old_lines:
        # Add 4 spaces to indent
        new_lines.append(f"    {line}")
    new_lines.append(f"{indent}except Exception as e:")

    # Determine the port/connection string from context
    # Look for common patterns like port='/dev/ttyACM0' or tcp_endpoint='localhost:5760'
    port_var = 'port'
    for i in range(max(0, api_open_line_idx - 15), api_open_line_idx):
        line_lower = lines[i].lower()
        if 'port=' in line_lower and 'port' in lines[i]:
            # Extract the actual variable name used
            if 'port=port' in line_lower or 'port=args.port' in line_lower:
                port_var = 'port'
            elif 'port=args' in line_lower:
                port_var = 'args.port'
            break
        if 'tcp_endpoint=' in lines[i]:
            if 'tcp_endpoint=host_port' in line_lower:
                port_var = 'host_port'
            else:
                port_var = 'tcp_endpoint'
            break

    new_lines.append(f'{indent}    print(f"ERROR: Cannot connect to {{{port_var}}}: {{e}}")')
    new_lines.append(f'{indent}    print(f"       If running in a sandboxed environment, device files in /dev/ may not be accessible.")')
    new_lines.append(f'{indent}    print(f"       Try running with sandbox disabled or check device permissions.")')

    # Check if the function returns a value - look for 'return' statements
    has_return = False
    for i in range(api_open_line_idx, min(len(lines), api_open_line_idx + 20)):
        if 'return' in lines[i]:
            has_return = True
            break

    if has_return:
        new_lines.append(f"{indent}    return False")
    else:
        new_lines.append(f"{indent}    raise")

    new_text = '\n'.join(new_lines)

    return old_text, new_text


def show_diff(file_path, old_text, new_text):
    """Show a unified diff of the changes."""
    old_lines = old_text.split('\n')
    new_lines = new_text.split('\n')

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f'{file_path} (original)',
        tofile=f'{file_path} (modified)',
        lineterm=''
    )

    return '\n'.join(diff)


def apply_patch(file_path, old_text, new_text, create_backup=True):
    """Apply the patch to a file."""
    content = file_path.read_text()

    if old_text not in content:
        return False, "Old text not found in file (file may have changed)"

    # Create backup
    if create_backup:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        backup_path.write_text(content)

    # Apply replacement
    new_content = content.replace(old_text, new_text)
    file_path.write_text(new_content)

    return True, "Applied successfully"


def main():
    parser = argparse.ArgumentParser(description='Add sandbox-aware error handling to MSPApi scripts')
    parser.add_argument('--root', default='claude/developer/scripts',
                       help='Root directory to search (default: claude/developer/scripts)')
    parser.add_argument('--apply', action='store_true',
                       help='Actually apply the changes (default is dry-run)')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backup files (.bak)')
    parser.add_argument('--file', help='Process only this specific file')

    args = parser.parse_args()

    print("="*80)
    print("MSPApi Sandbox Error Handler")
    print("="*80)
    print()

    if not args.apply:
        print("🔍 DRY RUN MODE - No files will be modified")
        print("   Use --apply to actually make changes")
        print()

    # Find files to process
    if args.file:
        files = [Path(args.file)]
    else:
        files = find_mspapi_files(args.root)

    print(f"Found {len(files)} Python files using MSPApi")
    print()

    # Analyze each file
    results = {
        'needs_update': [],
        'already_updated': [],
        'in_try_block': [],
        'no_api_open': [],
        'errors': []
    }

    for file_path in sorted(files):
        needs_update, reason, line_num, indent = analyze_file(file_path)

        if needs_update:
            results['needs_update'].append((file_path, line_num, indent))
        elif 'Already has sandbox' in reason:
            results['already_updated'].append(file_path)
        elif 'try block' in reason:
            results['in_try_block'].append(file_path)
        elif 'No api.open()' in reason:
            results['no_api_open'].append(file_path)

    # Report summary
    print("Summary:")
    print(f"  ✅ Already updated:      {len(results['already_updated'])}")
    print(f"  ⚠️  In try block:         {len(results['in_try_block'])} (may need manual review)")
    print(f"  ❌ No api.open() found:  {len(results['no_api_open'])}")
    print(f"  🔧 Needs update:         {len(results['needs_update'])}")
    print()

    if results['already_updated']:
        print("Already updated files:")
        for f in results['already_updated']:
            print(f"  ✓ {f}")
        print()

    if results['in_try_block']:
        print("Files with api.open() in try block (MANUAL REVIEW NEEDED):")
        for f in results['in_try_block']:
            print(f"  ⚠ {f}")
        print()

    # Process files that need updates
    if not results['needs_update']:
        print("No files need updating!")
        return 0

    print(f"Files to update ({len(results['needs_update'])}):")
    print()

    for file_path, line_num, indent in results['needs_update']:
        print("─"*80)
        print(f"📄 {file_path}")
        print(f"   Line {line_num}")
        print()

        old_text, new_text = generate_patch(file_path, line_num, indent)

        if old_text is None:
            print(f"   ❌ ERROR: Could not generate patch")
            results['errors'].append(file_path)
            continue

        diff = show_diff(file_path, old_text, new_text)
        print(diff)
        print()

        if args.apply:
            success, message = apply_patch(file_path, old_text, new_text, not args.no_backup)
            if success:
                print(f"   ✅ {message}")
                if not args.no_backup:
                    print(f"   💾 Backup: {file_path}.bak")
            else:
                print(f"   ❌ {message}")
                results['errors'].append(file_path)
        print()

    print("="*80)
    if args.apply:
        print(f"✅ Updated {len(results['needs_update']) - len(results['errors'])} files")
        if results['errors']:
            print(f"❌ Errors: {len(results['errors'])} files")
    else:
        print("Dry run complete. Use --apply to make changes.")
    print("="*80)

    return 1 if results['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
