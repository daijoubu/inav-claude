#!/usr/bin/env bash
# Auto-restarting wrapper for virtual_gnss_node.py
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)/sd_card_test"
LOG="/tmp/virtual_gnss.log"

echo "[$(date)] Starting virtual GNSS node (auto-restart on exit)" | tee "$LOG"

while true; do
    python3 -u "$SCRIPT_DIR/virtual_gnss_node.py" "$@" >> "$LOG" 2>&1
    echo "[$(date)] Process exited (code $?), restarting in 2s..." | tee -a "$LOG"
    sleep 2
done
