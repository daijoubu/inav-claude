#!/bin/bash
#
# Extract PG struct layout from DWARF debug info
# Uses readelf (standard binutils tool, no extra dependencies)
#
# Usage: extract-pg-struct-layout.sh <elf_file> <struct_name>
# Example: extract-pg-struct-layout.sh build/inav_SITL blackboxConfig_t
#

set -euo pipefail

ELF_FILE=$1
STRUCT_NAME=$2

# Convert blackboxConfig_t -> blackboxConfig_s (actual struct name)
STRUCT_BASE="${STRUCT_NAME%_t}_s"

echo "Extracting layout for $STRUCT_BASE from $ELF_FILE..." >&2

# Extract DWARF debug info for this struct
# Look for DW_TAG_structure_type with our name
DWARF_INFO=$(readelf --debug-dump=info "$ELF_FILE")

# Find the DIE (Debug Information Entry) for our struct
# This is a simplified parser - real DWARF is complex
echo "$DWARF_INFO" | awk -v struct="$STRUCT_BASE" '
BEGIN {
    in_struct = 0
    struct_level = 0
}

# Found our structure definition
/<[0-9a-f]+>.*DW_TAG_structure_type/ {
    struct_level = $1
    getline
    while (getline > 0) {
        if ($0 ~ /DW_AT_name.*: '"$STRUCT_BASE"'/) {
            in_struct = 1
            print "# Structure: '"$STRUCT_BASE"'"
            break
        }
        # If we hit another DIE at same level, this wasnt our struct
        if ($1 == struct_level && $0 ~ /DW_TAG/) {
            break
        }
    }
}

# Extract members while in our struct
in_struct && /<[0-9a-f]+>.*DW_TAG_member/ {
    member_name = ""
    member_offset = ""
    member_size = ""
    member_type = ""

    # Read member attributes
    while (getline > 0) {
        if ($0 ~ /DW_AT_name/) {
            match($0, /: (.+)/, arr)
            member_name = arr[1]
        }
        if ($0 ~ /DW_AT_data_member_location/) {
            match($0, /: ([0-9]+)/, arr)
            member_offset = arr[1]
        }
        if ($0 ~ /DW_AT_type/) {
            match($0, /: <0x([0-9a-f]+)>/, arr)
            member_type = arr[1]
        }

        # End of this member, check if we got all info
        if ($0 ~ /<[0-9a-f]+>.*DW_TAG/ || $0 ~ /^$/) {
            if (member_name != "" && member_offset != "") {
                printf "%s %s %s\n", member_offset, member_name, member_type
            }
            break
        }
    }
}

# Stop when we exit the structure
in_struct && /<[0-9a-f]+>.*DW_TAG/ && !($0 ~ /DW_TAG_member/) {
    exit
}
'
