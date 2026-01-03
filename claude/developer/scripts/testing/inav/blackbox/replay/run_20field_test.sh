#!/bin/bash
# Complete automated workflow for 20-field blackbox test
# This script handles all steps without leaving the FC in CLI mode

set -e

FC_CLI="~/inavflight/.claude/skills/flash-firmware-dfu/fc-cli.py"
PORT="${1:-/dev/ttyACM0}"
DURATION="${2:-10}"

echo "========================================================================"
echo "20-Field Blackbox Test - Automated Workflow"
echo "========================================================================"
echo "Port:     $PORT"
echo "Duration: ${DURATION}s"
echo ""

# Step 1: Configure blackbox settings via CLI (most reliable method)
echo "[Step 1/4] Configuring blackbox settings..."
cd ~/inavflight/claude/test_tools/inav/gps
python3 configure_blackbox_via_cli.py --port $PORT --rate-denom 100
echo "  ✓ Configuration complete, FC rebooted"

# Step 2: Wait for FC to reboot into normal MSP mode
echo "[Step 2/4] Waiting for FC to reboot..."
for i in {1..15}; do
  sleep 1
  if [ -e "$PORT" ]; then
    echo "  ✓ FC online after $i seconds"
    sleep 2  # Extra time for full initialization
    break
  fi
done

# Step 3: Erase blackbox flash
echo "[Step 3/4] Erasing blackbox flash..."
cd ~/inavflight/claude/test_tools/inav/gps
if ! python3 erase_blackbox_flash.py $PORT; then
  echo "✗ Flash erase failed!"
  exit 1
fi
# (erase_blackbox_flash.py already prints completion message)

# Step 4: Run test (no verification - trust the config worked)
echo "[Step 4/6] Running ${DURATION}-second hover test..."
python3 gps_hover_test_30s.py $PORT --duration $DURATION

# Step 5: Download blackbox log
echo "[Step 5/6] Downloading blackbox log..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="test_results/blackbox_${TIMESTAMP}.TXT"
python3 download_blackbox_from_fc.py $PORT $LOG_FILE

if [ ! -f "$LOG_FILE" ]; then
  echo "✗ Download failed!"
  exit 1
fi

# Step 6: Decode the log
echo "[Step 6/6] Decoding blackbox log..."
DECODE_OUTPUT="test_results/decode_${TIMESTAMP}.txt"
~/Documents/planes/inavflight/blackbox-tools-9.0.0-rc1/bin/blackbox_decode $LOG_FILE > $DECODE_OUTPUT 2>&1

echo ""
echo "========================================================================"
echo "Test Complete!"
echo "========================================================================"
echo ""
echo "Files created:"
echo "  Log:    $LOG_FILE"
echo "  Decode: $DECODE_OUTPUT"
echo "  CSV:    ${LOG_FILE%.TXT}.01.csv"
echo ""
echo "Check decode output for failures:"
echo "  grep 'frames failed' $DECODE_OUTPUT"
echo ""
