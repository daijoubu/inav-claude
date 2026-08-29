#!/bin/bash
# OSD Regression Test Suite for optimize/osd-sprintf-patterns branch
# ====================================================================
#
# Runs all three OSD regression tests in sequence:
#   1. Pure-Python unit tests for osdFormatIntUnit / osdFormatTime_MMSS
#   2. SITL MSP_OSD displayport test (confirms OSD frames are produced)
#   3. Baseline comparison report
#
# Usage:
#   ./run_osd_regression_suite.sh [--sitl-binary /path/to/SITL.elf] \
#                                  [--baseline-binary /path/to/baseline/SITL.elf] \
#                                  [--duration 12]
#
# Prerequisites:
#   - python3 in PATH
#   - For SITL test: SITL.elf built from the branch under test
#   - SITL serial port 1 must be configured as FUNCTION_MSP_OSD:
#       CLI: serial 1 33554432 115200 115200 0 115200
#            save
#
# Note: Must be run with dangerouslyDisableSandbox if inside Claude sandbox.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolve the inav source root. Lookup order:
#   1. $INAV_ROOT env var (canonical override)
#   2. Sibling checkout: <inav-claude-parent>/inav
#   3. Sibling numbered worktree: <inav-claude-parent>/inav2
#   4. Legacy: ~/Documents/planes/inavflight/inav{,2}
_resolve_inav_root() {
    if [ -n "${INAV_ROOT:-}" ] && [ -d "$INAV_ROOT" ]; then
        echo "$INAV_ROOT"; return
    fi
    local claude_root h
    claude_root="$(cd "$SCRIPT_DIR/../../../../../.." && pwd)"
    for h in "$claude_root/inav" "$claude_root/inav2"; do
        if [ -d "$h" ]; then echo "$h"; return; fi
    done
    for h in "$HOME/Documents/planes/inavflight/inav" "$HOME/Documents/planes/inavflight/inav2"; do
        if [ -d "$h" ]; then echo "$h"; return; fi
    done
    echo ""
}
INAV_ROOT="$(_resolve_inav_root)"

BRANCH_SITL="${1:-${INAV_ROOT:-}/build_sitl/bin/SITL.elf}"
BASELINE_SITL="${2:-/tmp/inav2_master_sitl_build/bin/SITL.elf}"
DURATION=12

MSP_PORT=5760
OSD_PORT=5761
HOST=localhost

PASS=0
FAIL=0
ERROR=0

print_header() {
    echo ""
    echo "##############################################################"
    echo "  $1"
    echo "##############################################################"
    echo ""
}

print_result() {
    local test_name="$1"
    local result="$2"
    case "$result" in
        PASS)  echo "  [PASS] $test_name" ; PASS=$((PASS+1)) ;;
        FAIL)  echo "  [FAIL] $test_name" ; FAIL=$((FAIL+1)) ;;
        ERROR) echo "  [ERROR] $test_name" ; ERROR=$((ERROR+1)) ;;
    esac
}

kill_sitl() {
    pkill -x SITL.elf 2>/dev/null || true
    sleep 1
}

start_sitl() {
    local binary="$1"
    local build_dir
    build_dir="$(dirname "$binary")/.."
    cd "$build_dir"
    "$binary" > /tmp/sitl_test.log 2>&1 &
    local pid=$!
    echo "  SITL PID: $pid"
    local i=0
    while [ $i -lt 15 ]; do
        if nc -z $HOST $MSP_PORT 2>/dev/null; then
            echo "  ✓ SITL ready on port $MSP_PORT"
            return 0
        fi
        sleep 1
        i=$((i+1))
    done
    echo "  ✗ SITL failed to start (timeout)"
    cat /tmp/sitl_test.log | tail -5
    return 1
}

configure_osd_port() {
    echo "  Configuring MSP_OSD on serial port 1 (port $OSD_PORT)..."
    python3 - <<PYEOF
import socket, time
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('$HOST', $MSP_PORT))
s.settimeout(0.5)
s.sendall(b'#')
time.sleep(0.3)
try: s.recv(4096)
except: pass
s.sendall(b'serial 1 33554432 115200 115200 0 115200\n')
time.sleep(0.3)
try: s.recv(4096)
except: pass
s.sendall(b'feature OSD\n')
time.sleep(0.3)
try: s.recv(4096)
except: pass
s.sendall(b'save\n')
time.sleep(2.0)
try: s.recv(4096)
except: pass
s.close()
PYEOF
    echo "  ✓ Config saved, waiting for SITL reboot..."
    sleep 5
    if nc -z $HOST $MSP_PORT 2>/dev/null; then
        echo "  ✓ SITL rebooted"
        return 0
    else
        echo "  ✗ SITL did not reboot correctly"
        return 1
    fi
}

# ==========================================================================
print_header "Test 1: Pure-Python OSD Format Helper Unit Tests"
echo "  (No SITL required – validates the Python reference model)"
echo ""

if python3 "$SCRIPT_DIR/test_osd_format_helpers.py"; then
    print_result "OSD format helper unit tests" PASS
else
    print_result "OSD format helper unit tests" FAIL
fi

# ==========================================================================
print_header "Test 2: Branch SITL - OSD MSP_OSD Port"

if [ ! -x "$BRANCH_SITL" ]; then
    echo "  ✗ Branch SITL not found at: $BRANCH_SITL"
    echo "    Build with: claude/developer/scripts/build/build_sitl.sh"
    print_result "Branch SITL OSD test" ERROR
else
    kill_sitl
    if start_sitl "$BRANCH_SITL"; then
        configure_osd_port || true
        echo ""
        if python3 "$SCRIPT_DIR/test_osd_msp_osd_port.py" \
                --host $HOST --msp-port $MSP_PORT --osd-port $OSD_PORT \
                --duration $DURATION; then
            print_result "Branch SITL OSD output (port $OSD_PORT)" PASS
        else
            EC=$?
            if [ $EC -eq 1 ]; then
                print_result "Branch SITL OSD output (port $OSD_PORT)" FAIL
            else
                print_result "Branch SITL OSD output (port $OSD_PORT)" ERROR
            fi
        fi
    else
        print_result "Branch SITL startup" ERROR
    fi
    kill_sitl
fi

# ==========================================================================
print_header "Test 3: Baseline (Master) SITL - OSD MSP_OSD Port"

if [ ! -x "$BASELINE_SITL" ]; then
    echo "  ✗ Baseline SITL not found at: $BASELINE_SITL"
    echo "    Build baseline with the instructions in the test documentation."
    print_result "Baseline SITL OSD test" ERROR
else
    kill_sitl
    if start_sitl "$BASELINE_SITL"; then
        configure_osd_port || true
        echo ""
        if python3 "$SCRIPT_DIR/test_osd_msp_osd_port.py" \
                --host $HOST --msp-port $MSP_PORT --osd-port $OSD_PORT \
                --duration $DURATION; then
            print_result "Baseline SITL OSD output (port $OSD_PORT)" PASS
        else
            EC=$?
            if [ $EC -eq 1 ]; then
                print_result "Baseline SITL OSD output (port $OSD_PORT)" FAIL
            else
                print_result "Baseline SITL OSD output (port $OSD_PORT)" ERROR
            fi
        fi
    else
        print_result "Baseline SITL startup" ERROR
    fi
    kill_sitl
fi

# ==========================================================================
print_header "Test Suite Summary"

TOTAL=$((PASS + FAIL + ERROR))
echo "  Total:  $TOTAL"
echo "  Pass:   $PASS"
echo "  Fail:   $FAIL"
echo "  Error:  $ERROR"
echo ""

if [ $FAIL -gt 0 ]; then
    echo "  OVERALL: FAIL"
    echo ""
    echo "  One or more tests failed.  If the BRANCH test fails but the"
    echo "  BASELINE passes, the regression is confirmed on this branch."
    exit 1
elif [ $ERROR -gt 0 ]; then
    echo "  OVERALL: ERROR (some tests could not run)"
    exit 2
else
    echo "  OVERALL: PASS"
    exit 0
fi
