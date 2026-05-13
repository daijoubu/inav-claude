#!/bin/bash
#
# Extract PG struct sizes using pahole
# Simple and reliable - works on any architecture
#

set -euo pipefail

ELF_FILE=$1

echo "Extracting PG struct sizes from $ELF_FILE using pahole..." >&2

# Find all PG struct types from source
grep -rh "PG_REGISTER" src/main --include="*.c" | \
    grep -oP 'PG_REGISTER[^(]*\(\K[^,]+' | \
    sort -u | \
    while read struct_type; do
        # Convert blackboxConfig_t -> blackboxConfig_s
        struct_base="${struct_type%_t}_s"

        # Get size from pahole
        size=$(pahole -C "$struct_base" "$ELF_FILE" 2>/dev/null | \
            grep "size:" | \
            grep -oP 'size: \K\d+')

        if [ -n "$size" ]; then
            printf "%-30s %s\n" "$struct_type" "$size"
        fi
    done
