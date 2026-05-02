#!/bin/bash
# Run all SD card tests individually, logging output to files
# Test 9 runs for 180 minutes

set -e

PORT="${1:-/dev/ttyACM0}"
LOG_DIR="logs/run_$(date +%Y%m%d-%H%M%S)"
mkdir -p "$LOG_DIR"

echo "=== SD Card Test Suite ===" | tee "$LOG_DIR/summary.log"
echo "Port: $PORT" | tee -a "$LOG_DIR/summary.log"
echo "Log directory: $LOG_DIR" | tee -a "$LOG_DIR/summary.log"
echo "" | tee -a "$LOG_DIR/summary.log"

run_test() {
    local test_num=$1
    local log_file="$LOG_DIR/test_${test_num}.log"
    shift
    local extra_args="$@"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Test $test_num..." | tee -a "$LOG_DIR/summary.log"
    
    if python3 -m sd_card_test "$PORT" --tests "$test_num" --verbose $extra_args > "$log_file" 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test $test_num PASSED" | tee -a "$LOG_DIR/summary.log"
        echo "PASS" >> "$LOG_DIR/results.txt"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test $test_num FAILED" | tee -a "$LOG_DIR/summary.log"
        echo "FAIL" >> "$LOG_DIR/results.txt"
    fi
    echo "" | tee -a "$LOG_DIR/summary.log"
    
    # Brief pause between tests to let FC settle
    sleep 2
}

# Test 1: SD Card Detection (~3s)
run_test 1

# Test 2: Write Speed Measurement (60s)
run_test 2 --duration-sec 60

# Test 3: Continuous Logging (5 min default)
run_test 3 --duration-min 5

# Test 4: High-Frequency Logging (60s)
run_test 4 --duration-sec 60

# Test 6: Arm/Disarm Cycles (20 cycles)
run_test 6 --cycles 20

# Test 7: MSC Log Verification (~30s)
run_test 7 --max-logs 2

# Test 8: GPS Fix + Immediate Arm (10 attempts)
run_test 8 --attempts 10

# Test 9: Extended Endurance (180 minutes)
run_test 9 --duration-min 180

# Test 10: DMA Contention Stress (10 min)
run_test 10 --duration-min 10

# Test 11: Blocking Measurement (60s, requires ST-Link and ELF)
run_test 11 --duration-sec 60

echo "=== All tests complete ===" | tee -a "$LOG_DIR/summary.log"
echo "Logs saved to: $LOG_DIR" | tee -a "$LOG_DIR/summary.log"
echo "" | tee -a "$LOG_DIR/summary.log"
echo "Results:" | tee -a "$LOG_DIR/summary.log"
cat "$LOG_DIR/results.txt" | tee -a "$LOG_DIR/summary.log"
