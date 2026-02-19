#!/bin/bash
# Verify Linux SITL binary glibc version requirement.
# Extracts the SITL binary from a Linux configurator zip and checks
# that the maximum required GLIBC version is <= the threshold.
#
# Usage:
#   ./verify-linux-sitl-glibc.sh <linux-zip-or-binary> [max-glibc-version]
#
# Examples:
#   ./verify-linux-sitl-glibc.sh INAV-Configurator_linux_x64_9.0.2.zip
#   ./verify-linux-sitl-glibc.sh INAV-Configurator_linux_x64_9.0.2.zip 2.35
#   ./verify-linux-sitl-glibc.sh /path/to/inav_SITL

set -euo pipefail

INPUT="${1:?Usage: $0 <linux-zip-or-binary> [max-glibc-version]}"
MAX_GLIBC="${2:-2.35}"

echo "========================================="
echo "Linux SITL glibc Verification"
echo "========================================="
echo ""

BINARY=""
TMPDIR_CREATED=""

if [[ "$INPUT" == *.zip ]]; then
    echo "Extracting SITL binary from: $(basename "$INPUT")"
    TMPDIR_CREATED=$(mktemp -d)
    unzip -q -j "$INPUT" '*/sitl/linux/inav_SITL' -d "$TMPDIR_CREATED" 2>/dev/null || \
    unzip -q -j "$INPUT" '*/sitl/darwin/inav_SITL' -d "$TMPDIR_CREATED" 2>/dev/null || {
        echo "[FAIL] Could not find inav_SITL in zip"
        rm -rf "$TMPDIR_CREATED"
        exit 1
    }
    BINARY="$TMPDIR_CREATED/inav_SITL"
else
    BINARY="$INPUT"
fi

if [ ! -f "$BINARY" ]; then
    echo "[FAIL] Binary not found: $BINARY"
    [ -n "$TMPDIR_CREATED" ] && rm -rf "$TMPDIR_CREATED"
    exit 1
fi

# Verify it's an ELF binary
file_type=$(file -b "$BINARY")
echo "Binary: $file_type"
echo ""

if ! echo "$file_type" | grep -q "ELF"; then
    echo "[FAIL] Not an ELF binary"
    [ -n "$TMPDIR_CREATED" ] && rm -rf "$TMPDIR_CREATED"
    exit 1
fi

# readelf -V is the reliable way to get GLIBC version requirements.
# objdump -T may return empty if the binary has BIND_NOW + full RELRO.
GLIBC_MAX=$(readelf -V "$BINARY" 2>/dev/null \
    | grep -oP 'GLIBC_\K[0-9.]+' \
    | sort -V -u \
    | tail -1)

if [ -z "$GLIBC_MAX" ]; then
    echo "[WARN] No GLIBC version symbols found (possibly statically linked)"
    echo "[PASS] No glibc dependency - compatible with all systems"
    [ -n "$TMPDIR_CREATED" ] && rm -rf "$TMPDIR_CREATED"
    exit 0
fi

echo "GLIBC versions required:"
readelf -V "$BINARY" 2>/dev/null \
    | grep -oP 'GLIBC_\K[0-9.]+' \
    | sort -V -u \
    | while read v; do echo "  - GLIBC_$v"; done

echo ""
echo "Maximum required: GLIBC_$GLIBC_MAX"
echo "Threshold:        GLIBC_$MAX_GLIBC"
echo ""

# Compare versions
if printf '%s\n' "$MAX_GLIBC" "$GLIBC_MAX" | sort -V | tail -1 | grep -q "^${MAX_GLIBC}$"; then
    echo "[PASS] GLIBC_$GLIBC_MAX <= GLIBC_$MAX_GLIBC"
else
    echo "[FAIL] GLIBC_$GLIBC_MAX > GLIBC_$MAX_GLIBC"
    echo ""
    echo "This binary requires a newer glibc than supported."
    echo "Build on Ubuntu 22.04 LTS for glibc <= 2.35 compatibility."
    [ -n "$TMPDIR_CREATED" ] && rm -rf "$TMPDIR_CREATED"
    exit 1
fi

[ -n "$TMPDIR_CREATED" ] && rm -rf "$TMPDIR_CREATED"
