#!/bin/bash
# reboot-to-dfu.sh - Reboot flight controller into DFU mode via serial CLI
#
# Usage: ./reboot-to-dfu.sh [serial_port]
#   serial_port: defaults to /dev/ttyACM0

set -e

SERIAL_PORT="${1:-/dev/ttyACM0}"
TIMEOUT=2

if [ ! -e "$SERIAL_PORT" ]; then
    echo "ERROR: Serial port $SERIAL_PORT not found"
    exit 1
fi

echo "Rebooting flight controller to DFU mode via $SERIAL_PORT"

# Function to send command and wait for response
send_and_wait() {
    local command="$1"
    local expected="$2"
    local timeout="$3"

    # Send command
    echo -ne "$command" > "$SERIAL_PORT"

    # Read response with timeout
    local received=""
    local start_time=$(date +%s)

    while true; do
        # Check timeout
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        if [ $elapsed -ge $timeout ]; then
            echo "ERROR: Timeout waiting for '$expected'"
            echo "Received: $received"
            return 1
        fi

        # Read available data
        if read -t 0.1 -r line < "$SERIAL_PORT" 2>/dev/null; then
            received="$received$line"

            # Check if we got the expected response
            if echo "$received" | grep -q "$expected"; then
                echo "Got expected response: $expected"
                return 0
            fi
        fi
    done
}

# Configure serial port for raw mode (no echo, no processing)
stty -F "$SERIAL_PORT" raw -echo 115200

# Step 1: Send #### to enter CLI mode and wait for "CLI" prompt
echo "Entering CLI mode..."
if ! send_and_wait "####\r\n" "CLI" "$TIMEOUT"; then
    echo "Failed to enter CLI mode"
    exit 1
fi

# Step 2: Send dfu command
echo "Sending DFU reboot command..."
echo -ne "dfu\r\n" > "$SERIAL_PORT"

# Wait for DFU device to appear
echo "Waiting for DFU device to appear (10 seconds)..."
sleep 10

# Verify DFU mode
if dfu-util -l 2>/dev/null | grep -q "0483:df11"; then
    echo "SUCCESS: Flight controller is now in DFU mode"
    dfu-util -l
    exit 0
else
    echo "WARNING: DFU device not detected. Check connection."
    exit 1
fi
