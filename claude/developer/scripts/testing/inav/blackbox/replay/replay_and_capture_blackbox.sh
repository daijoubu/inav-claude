#!/bin/bash
#
# Replay Blackbox Data to SITL and Capture Output
#
# This script performs the complete workflow to:
# 1. Start SITL with fresh configuration
# 2. Configure blackbox FILE logging with DEBUG_POS_EST mode
# 3. Enable BLACKBOX feature flag (required!)
# 4. Configure MSP receiver and ARM mode
# 5. Arm SITL in background (must stay armed during replay)
# 6. Replay sensor data from existing blackbox log
# 7. Capture SITL's output blackbox log
#
# Use Case:
#   Test how SITL's position estimator (navEPH, navEPV) responds to
#   real sensor data from actual flights, especially during high-G
#   maneuvers or GPS fluctuations.
#
# Customize:
#   - Edit line 46: Change CSV input file path
#   - Edit lines 49-51: Change time window (--start-time, --duration)
#   - Edit line 40: Increase timeout if replay is longer than 60s
#
# Output:
#   - SITL blackbox log: inav/build_sitl/YYYY_MM_DD_HHMMSS.TXT
#   - Decoded CSV: inav/build_sitl/YYYY_MM_DD_HHMMSS.01.csv
#
# Critical Requirements:
#   - SITL must be ARMED before and during replay
#   - BLACKBOX feature must be enabled (not just device setting)
#   - Must wait for blackbox flush after replay completes
#
# See: claude/test_tools/inav/gps/README_GPS_BLACKBOX_TESTING.md
#      Section: "Replay Workflow: Capturing SITL Output from Blackbox Replay"
#

set -e

cd ~/inavflight/inav/build_sitl

echo "=== Step 1: Start SITL fresh ==="
pkill -9 SITL.elf 2>/dev/null || true
sleep 2
rm -f eeprom.bin *.TXT *.csv

./bin/SITL.elf > /tmp/sitl_workflow.log 2>&1 &
sleep 10
echo "✓ SITL started"

echo ""
echo "=== Step 2: Configure blackbox FILE logging ==="
cd ~/inavflight
python3 claude/test_tools/inav/gps/configure_sitl_blackbox_file.py --port 5760 --rate-denom 2

echo ""
echo "=== Step 3: Wait for SITL reboot ==="
sleep 15

echo ""
echo "=== Step 4: Enable BLACKBOX feature ==="
python3 claude/test_tools/inav/gps/enable_blackbox_feature.py --port 5760

echo ""
echo "=== Step 5: Configure for arming ==="
python3 claude/test_tools/inav/gps/configure_sitl_for_arming.py --port 5760

echo ""
echo "=== Step 6: Wait for final reboot ==="
sleep 15

echo ""
echo "=== Step 7: Arm SITL (in background) ==="
timeout 60 python3 claude/test_tools/inav/sitl/sitl_arm_test.py 5760 > /tmp/arm_output.log 2>&1 &
ARM_PID=$!
sleep 5

echo ""
echo "=== Step 8: Run blackbox replay ==="
python3 claude/test_tools/inav/gps/replay_blackbox_to_fc.py \
    --csv claude/developer/investigations/gps-fluctuation-issue-11202/blackbox_logs/fast_log_full.01.csv \
    --port tcp:localhost:5761 \
    --start-time 20 \
    --duration 20 \
    --speed 1.0

echo ""
echo "=== Step 9: Stop arming and wait for blackbox flush ==="
kill $ARM_PID 2>/dev/null || true
sleep 5

echo ""
echo "=== Step 10: Find blackbox log ==="
cd ~/inavflight/inav/build_sitl
BBLOG=$(ls -t *.TXT 2>/dev/null | head -1)
if [ -n "$BBLOG" ]; then
    echo "✓ Blackbox log found: $BBLOG"
    ls -lh "$BBLOG"
else
    echo "✗ No blackbox log found!"
    exit 1
fi

echo ""
echo "=== DONE ==="
echo "Blackbox log: inav/build_sitl/$BBLOG"
