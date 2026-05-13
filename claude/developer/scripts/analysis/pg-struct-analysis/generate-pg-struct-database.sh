#!/bin/bash
#
# Generate initial PG struct layout database
# Extracts all PG structs from an ELF file and creates checksum database
#
# Usage: generate-pg-struct-database.sh <elf_file> [output_db]
#

set -euo pipefail

SCRIPT_DIR=$(dirname "$0")
ELF_FILE="${1:-}"
OUTPUT_DB="${2:-${SCRIPT_DIR}/pg_struct_checksums.db}"

if [ -z "$ELF_FILE" ]; then
    echo "Usage: $0 <elf_file_with_debug_info> [output_db]"
    echo "Example: $0 build/inav_SITL"
    exit 1
fi

if [ ! -f "$ELF_FILE" ]; then
    echo "Error: ELF file not found: $ELF_FILE"
    exit 1
fi

echo "🔨 Generating PG struct database from $ELF_FILE"
echo "📝 Output: $OUTPUT_DB"
echo ""

# Create header
cat > "$OUTPUT_DB" << 'EOF'
# PG Struct Layout Database
# Format: struct_type version checksum
# Checksum is MD5 of struct layout (field offsets and types)
# Generated automatically - do not edit manually
#
EOF

# Find all PG_REGISTER entries and extract struct info
grep -rh "PG_REGISTER" src/main --include="*.c" | while read -r line; do
    # Extract struct type and version
    if [[ $line =~ PG_REGISTER[^(]*\(([^,]+),.*,([^)]+)\) ]]; then
        struct_type=$(echo "${BASH_REMATCH[1]}" | xargs)
        version=$(echo "${BASH_REMATCH[2]}" | xargs)

        # Skip if not a simple integer version
        [[ ! "$version" =~ ^[0-9]+$ ]] && continue

        echo "  Processing $struct_type (version $version)..."

        # Extract layout from ELF
        layout=$("$SCRIPT_DIR/extract-pg-struct-layout.sh" "$ELF_FILE" "$struct_type" 2>/dev/null || echo "")

        if [ -z "$layout" ]; then
            echo "    ⚠️  Warning: Could not extract layout (not in binary?)"
            continue
        fi

        # Compute checksum
        checksum=$(echo "$layout" | md5sum | cut -d' ' -f1)

        # Add to database
        printf "%-30s %2s %s\n" "$struct_type" "$version" "$checksum" >> "$OUTPUT_DB"
        echo "    ✅ Added: checksum $checksum"
    fi
done

echo ""
echo "✅ Database generated: $OUTPUT_DB"
echo ""
echo "Entry count: $(grep -v '^#' "$OUTPUT_DB" | grep -v '^$' | wc -l)"
