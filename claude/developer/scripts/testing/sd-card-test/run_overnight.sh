#!/bin/bash
# Overnight DroneCAN test: GNSS sim + candump + arm/disarm cycles
BASEDIR="/home/robs/Projects/inav-claude/claude/developer/scripts/testing/sd-card-test"
export PYTHONPATH="$BASEDIR:$PYTHONPATH"
cd "$BASEDIR"

# GNSS simulator
nohup python3 -u sd_card_test/virtual_gnss_node.py --can can0 --node-id 74 \
  > /tmp/gnss_sim.log 2>&1 &
echo "GNSS_PID=$!"

# Error frame logging
nohup candump can0 -e -l \
  > /dev/null 2>&1 &
echo "CANDUMP_ERR_PID=$!"

# Overnight monitor
nohup python3 -u sd_card_test/overnight_monitor.py /dev/ttyACM0 --can can0 \
  --deadline 06:30 > /tmp/overdrone_night.log 2>&1 &
echo "OVERDRONE_PID=$!"
