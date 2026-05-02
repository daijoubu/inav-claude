#!/bin/bash
# Run a single test with logging

PORT="${1:-/dev/ttyACM0}"
TEST_NUM="${2:-1}"
LOG_DIR="${3:-logs/run_$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$LOG_DIR"

echo "=== Running Test $TEST_NUM ===" 
echo "Port: $PORT"
echo "Log: $LOG_DIR/test_${TEST_NUM}.log"

case $TEST_NUM in
    1) EXTRA_ARGS="" ;;
    2) EXTRA_ARGS="--duration-sec 60" ;;
    3) EXTRA_ARGS="--duration-min 5" ;;
    4) EXTRA_ARGS="--duration-sec 60" ;;
    6) EXTRA_ARGS="--cycles 20" ;;
    7) EXTRA_ARGS="--max-logs 2" ;;
    8) EXTRA_ARGS="--attempts 10" ;;
    9) EXTRA_ARGS="--duration-min 180" ;;
    10) EXTRA_ARGS="--duration-min 10" ;;
    11) EXTRA_ARGS="--duration-sec 60" ;;
    *) EXTRA_ARGS="" ;;
esac

python3 -m sd_card_test "$PORT" --tests "$TEST_NUM" --verbose $EXTRA_ARGS 2>&1 | tee "$LOG_DIR/test_${TEST_NUM}.log"
EXIT_CODE=${PIPESTATUS[0]}

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "Test $TEST_NUM: PASSED"
    echo "PASS" > "$LOG_DIR/result.txt"
else
    echo "Test $TEST_NUM: FAILED"
    echo "FAIL" > "$LOG_DIR/result.txt"
fi

exit $EXIT_CODE
