#!/usr/bin/env python3
"""Create a compact INDEX.md with only active projects"""

from pathlib import Path
import re

def main():
    index_path = Path(__file__).parent / "INDEX.md"

    with open(index_path) as f:
        lines = f.readlines()

    active_lines = []
    completed_lines = []

    current_section = []
    is_completed = False
    in_header = True

    for line in lines:
        # Check if this is a project header
        if re.match(r'^### [📋🚧⏸️❌✅]', line):
            # Save previous section
            if current_section:
                if is_completed:
                    completed_lines.extend(current_section)
                else:
                    active_lines.extend(current_section)

            # Start new section
            current_section = [line]
            # Completed (✅) and Cancelled (❌) are both archived
            is_completed = '✅' in line or '❌' in line
            in_header = False

        elif re.match(r'^## ', line):
            # Section header - save what we have
            if current_section:
                if is_completed:
                    completed_lines.extend(current_section)
                else:
                    active_lines.extend(current_section)
                current_section = []

            if in_header:
                active_lines.append(line)
            in_header = False

        elif in_header:
            active_lines.append(line)
        else:
            current_section.append(line)

    # Save last section
    if current_section:
        if is_completed:
            completed_lines.extend(current_section)
        else:
            active_lines.extend(current_section)

    # Write compact INDEX.md with only active projects
    with open(index_path.parent / "INDEX_compact.md", 'w') as f:
        # Write header
        for line in active_lines:
            f.write(line)

        # Add reference to completed projects
        f.write("\n---\n\n")
        f.write("## Completed & Cancelled Projects\n\n")
        f.write("All completed and cancelled projects have been archived for reference.\n\n")
        completed_count = len([l for l in completed_lines if '### ✅' in l])
        cancelled_count = len([l for l in completed_lines if '### ❌' in l])
        f.write(f"**Total Completed:** {completed_count} projects\n")
        f.write(f"**Total Cancelled:** {cancelled_count} projects\n\n")
        f.write("**See:** [COMPLETED_PROJECTS.md](COMPLETED_PROJECTS.md) for full archive\n\n")
        f.write("**Query Tool:**\n")
        f.write("- `python3 project_manager.py list COMPLETE` - View completed projects\n")
        f.write("- `python3 project_manager.py list CANCELLED` - View cancelled projects\n")

    # Append completed and cancelled to COMPLETED_PROJECTS.md
    completed_path = index_path.parent / "COMPLETED_PROJECTS.md"
    completed_count = len([l for l in completed_lines if '### ✅' in l])
    cancelled_count = len([l for l in completed_lines if '### ❌' in l])

    with open(completed_path, 'w') as f:
        f.write("# Completed & Cancelled Projects Archive\n\n")
        f.write("This file contains all completed (✅) and cancelled (❌) projects.\n\n")
        f.write(f"**Total Completed:** {completed_count} projects\n")
        f.write(f"**Total Cancelled:** {cancelled_count} projects\n\n")
        f.write("For active projects, see [INDEX.md](INDEX.md)\n\n")
        f.write("---\n\n")
        f.writelines(completed_lines)

    print(f"Created INDEX_compact.md: {len(active_lines)} lines (active only)")
    print(f"Updated COMPLETED_PROJECTS.md: {len(completed_lines)} lines")

if __name__ == "__main__":
    main()
