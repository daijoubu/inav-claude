#!/bin/bash
#
# Extract PG struct sizes directly from compiled binary
# Uses symbol table - no DWARF debug info needed!
#
# Works by finding the PG reset template symbols which have the struct size
#

set -euo pipefail

ELF_FILE=$1

echo "Extracting PG struct sizes from $ELF_FILE..." >&2

# Detect architecture and use appropriate nm
ARCH=$(file "$ELF_FILE" | grep -o "x86-64\|ARM")
if [[ "$ARCH" == "x86-64" ]]; then
    NM_CMD="nm"
else
    NM_CMD="arm-none-eabi-nm"
fi

# Use nm to get all symbols
# PG reset templates are named: __pg_resetdata_<pgName>
# Their size in the symbol table = sizeof(struct)

$NM_CMD --print-size --size-sort --radix=d "$ELF_FILE" | \
    grep "__pg_resetdata_" | \
    while read addr size type name; do
        # Extract PG name from symbol
        # __pg_resetdata_blackboxConfig -> blackboxConfig
        pg_name=$(echo "$name" | sed 's/__pg_resetdata_//')

        # Find corresponding struct type from source
        # This is a bit hacky but works
        struct_type=$(grep -rh "PG_REGISTER.*$pg_name" src/main --include="*.c" 2>/dev/null | \
            grep -oP 'PG_REGISTER[^(]*\(\K[^,]+' | head -1)

        if [ -n "$struct_type" ]; then
            printf "%-30s %s\n" "$struct_type" "$size"
        fi
    done | sort -u
