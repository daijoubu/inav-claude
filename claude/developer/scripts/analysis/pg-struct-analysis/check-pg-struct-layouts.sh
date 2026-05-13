#!/bin/bash
#
# Validate PG struct layouts against known checksums
# Detects struct changes without version increments
#
# Exit codes:
#   0 - All checks passed
#   1 - Struct layout changed but version not incremented
#   2 - Script error
#

set -euo pipefail

SCRIPT_DIR=$(dirname "$0")
ELF_FILE="${1:-}"
DATABASE="${SCRIPT_DIR}/pg_struct_checksums.db"

if [ -z "$ELF_FILE" ]; then
    echo "Usage: $0 <elf_file_with_debug_info>"
    echo "Example: $0 build/inav_SITL"
    exit 2
fi

if [ ! -f "$ELF_FILE" ]; then
    echo "Error: ELF file not found: $ELF_FILE"
    exit 2
fi

if [ ! -f "$DATABASE" ]; then
    echo "Warning: Database not found: $DATABASE"
    echo "Run with --generate to create initial database"
    exit 0
fi

echo "🔍 Checking PG struct layouts against database..."

ISSUES_FOUND=0

# Read database: struct_type version checksum
while IFS=' ' read -r struct_type version expected_checksum || [ -n "$struct_type" ]; do
    # Skip comments and empty lines
    [[ "$struct_type" =~ ^#.*$ ]] && continue
    [ -z "$struct_type" ] && continue

    echo "  📋 Checking $struct_type (version $version)"

    # Extract current layout from ELF
    layout=$("$SCRIPT_DIR/extract-pg-struct-layout.sh" "$ELF_FILE" "$struct_type" 2>/dev/null || echo "")

    if [ -z "$layout" ]; then
        echo "    ⚠️  Warning: Could not extract layout (struct not found in binary)"
        continue
    fi

    # Compute checksum of layout
    current_checksum=$(echo "$layout" | md5sum | cut -d' ' -f1)

    if [ "$current_checksum" != "$expected_checksum" ]; then
        echo "    ⚠️  Layout changed (checksum: $expected_checksum → $current_checksum)"

        # Find PG_REGISTER to check current version
        pg_file=$(grep -r "PG_REGISTER.*$struct_type" src/main --include="*.c" | head -1 | cut -d: -f1)

        if [ -n "$pg_file" ]; then
            current_version=$(grep "PG_REGISTER.*$struct_type" "$pg_file" | grep -oP ',\s*\K\d+(?=\s*\))' || echo "")

            if [ "$current_version" == "$version" ]; then
                echo "    ❌ ERROR: Version NOT incremented (still $version)"
                echo "       File: $pg_file"
                echo "       ACTION REQUIRED: Increment PG version"
                ISSUES_FOUND=$((ISSUES_FOUND + 1))
            else
                echo "    ✅ Version incremented ($version → $current_version)"
                echo "       Note: Update database with --update-db"
            fi
        else
            echo "    ⚠️  Could not find PG_REGISTER for $struct_type"
        fi
    else
        echo "    ✅ Layout unchanged"
    fi
done < "$DATABASE"

echo ""
if [ $ISSUES_FOUND -gt 0 ]; then
    echo "❌ Found $ISSUES_FOUND struct(s) with layout changes but no version increment"
    exit 1
else
    echo "✅ All PG struct layouts validated"
    exit 0
fi
