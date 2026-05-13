#!/bin/bash
#
# Compare PG struct sizes across multiple ELF files
# Shows platform-specific size differences
#

set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: $0 <elf1> <elf2> [elf3...]"
    echo "Example: $0 build/bin/MATEKF722.elf build/bin/MATEKH743.elf"
    exit 1
fi

ELF_FILES=("$@")

echo "Comparing PG struct sizes across platforms..."
echo ""

# Extract all PG struct types
STRUCT_TYPES=$(grep -rh "PG_REGISTER" src/main --include="*.c" | \
    grep -oP 'PG_REGISTER[^(]*\(\K[^,]+' | \
    sort -u | \
    xargs)

# Header
printf "%-30s" "Struct"
for elf in "${ELF_FILES[@]}"; do
    basename=$(basename "$elf" .elf)
    printf " %15s" "$basename"
done
printf "\n"

printf "%-30s" "=============================="
for elf in "${ELF_FILES[@]}"; do
    printf " %15s" "==============="
done
printf "\n"

# For each struct, get size from each ELF
for struct_type in $STRUCT_TYPES; do
    printf "%-30s" "$struct_type"

    sizes=()
    for elf in "${ELF_FILES[@]}"; do
        # Use readelf to get struct size from DWARF
        struct_base="${struct_type%_t}_s"

        # Extract DW_TAG_structure_type and DW_AT_byte_size
        size=$(readelf --debug-dump=info "$elf" 2>/dev/null | \
            awk -v struct="$struct_base" '
            /<[0-9a-f]+>.*DW_TAG_structure_type/ {
                in_tag = 1
                struct_found = 0
            }
            in_tag && /DW_AT_name.*: '"$struct_base"'/ {
                struct_found = 1
            }
            in_tag && struct_found && /DW_AT_byte_size.*: ([0-9]+)/ {
                match($0, /: ([0-9]+)/, arr)
                print arr[1]
                exit
            }
            /<[0-9a-f]+>.*DW_TAG/ && in_tag && !struct_found {
                in_tag = 0
            }
            ' || echo "")

        if [ -z "$size" ]; then
            printf " %15s" "N/A"
        else
            printf " %15s" "${size}B"
            sizes+=("$size")
        fi
    done

    # Check if all sizes are the same
    if [ ${#sizes[@]} -gt 1 ]; then
        first="${sizes[0]}"
        all_same=1
        for s in "${sizes[@]}"; do
            if [ "$s" != "$first" ]; then
                all_same=0
                break
            fi
        done

        if [ $all_same -eq 0 ]; then
            printf " ⚠️ MISMATCH"
        fi
    fi

    printf "\n"
done

echo ""
echo "Legend:"
echo "  N/A = Struct not found in this platform's binary"
echo "  ⚠️ MISMATCH = Struct has different sizes across platforms"
