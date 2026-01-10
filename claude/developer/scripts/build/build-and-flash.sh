#!/bin/bash
# Build and flash firmware to flight controller
#
# NOTE: This script is by the inav-builder agent. If calling directly
# (not via the agent), you should probably use the agent (unless you ARE the agent).
# be aware this script doesn't handle cmake reconfiguration when CMakeLists.txt files change.
#
# Usage: build-and-flash.sh [OPTIONS] [TARGET] [EXTRA_FLAGS]
#
# Options:
#   --full-erase    Erase all settings (full chip erase)
#
# Examples:
#   build-and-flash.sh DAKEFPVF722
#   build-and-flash.sh --full-erase DAKEFPVF722
#   build-and-flash.sh DAKEFPVF722 "-DTEST_CIRCULAR_DSHOT"
#   build-and-flash.sh --full-erase DAKEFPVF722 "-DTEST_CIRCULAR_DSHOT"

set -e

# Parse options
FULL_ERASE=false
while [[ "$1" == --* ]]; do
    case "$1" in
        --full-erase)
            FULL_ERASE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INAV_DIR="$SCRIPT_DIR/../../../../inav"
SKILL_DIR="$SCRIPT_DIR/../../../../.claude/skills/flash-firmware-dfu"

TARGET="${1:-JHEMCUF435}"
EXTRA_FLAGS="${2:-}"
SERIAL_PORT="/dev/ttyACM0"

# Build firmware
echo "=== Building $TARGET ${EXTRA_FLAGS:+with $EXTRA_FLAGS} ==="
cd "$INAV_DIR/build"
if [ -n "$EXTRA_FLAGS" ]; then
    make EXTRA_FLAGS="$EXTRA_FLAGS" "$TARGET" -j$(nproc) || exit 1
else
    make "$TARGET" -j$(nproc) || exit 1
fi

# Find the hex file
HEX=$(ls inav_*${TARGET}*.hex 2>/dev/null | head -1)
if [ -z "$HEX" ]; then
    echo "ERROR: No hex file found for $TARGET"
    exit 1
fi
echo "Built: $HEX"

# Convert to bin
echo "=== Converting to binary ==="
BIN="${HEX%.hex}.bin"
arm-none-eabi-objcopy -I ihex -O binary "$HEX" "$BIN"
echo "Converted: $BIN"

# Put FC in DFU mode
echo "=== Entering DFU mode ==="
if [ -e "$SERIAL_PORT" ]; then
    "$SKILL_DIR/reboot-to-dfu.py" "$SERIAL_PORT" || {
        echo "ERROR: Failed to enter DFU mode"
        echo "Try: hold BOOT button while plugging in USB"
        exit 1
    }
else
    echo "No serial port found - FC may already be in DFU mode"
fi

# Wait for DFU device
echo "=== Waiting for DFU device ==="
for i in {1..10}; do
    if lsusb 2>/dev/null | grep -q "0483:df11\|2e3c:df11"; then
        echo "DFU device detected"
        break
    fi
    sleep 1
done

# Detect DFU vendor ID (STM32 vs AT32)
if lsusb 2>/dev/null | grep -q "2e3c:df11"; then
    DFU_ID="2e3c:df11"
    echo "Detected AT32 DFU device"
elif lsusb 2>/dev/null | grep -q "0483:df11"; then
    DFU_ID="0483:df11"
    echo "Detected STM32 DFU device"
else
    echo "ERROR: No DFU device found"
    exit 1
fi

# Flash firmware
echo "=== Flashing firmware ==="
if [ "$FULL_ERASE" = true ]; then
    echo "Performing full chip erase (settings will be erased)"
    dfu-util -d "$DFU_ID" --alt 0 -s 0x08000000:mass-erase:force:leave -D "$BIN"
else
    echo "Preserving settings (no full erase)"
    dfu-util -d "$DFU_ID" --alt 0 -s 0x08000000:leave -D "$BIN"
fi

echo "=== Waiting for FC to reboot ==="
sleep 5

if [ -e "$SERIAL_PORT" ]; then
    echo "✓ Flash complete, FC ready at $SERIAL_PORT"
else
    echo "⚠ FC not detected yet, may need more time"
fi
