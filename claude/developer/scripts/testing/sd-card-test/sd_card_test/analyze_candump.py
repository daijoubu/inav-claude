#!/usr/bin/env python3
"""
Analyze candump logs per-node, per-message-type statistics.

For each node and CAN ID, computes:
  - message count
  - overall mean interval (since first message of that type from this run)
  - max interval between consecutive transmissions
  - mean of 60-second sliding-window mean intervals
  - min of those windowed means
  - max of those windowed means

Outputs: one CSV per node ID found in the log.
"""

import re
import csv
import sys
import os
import math
from collections import defaultdict
from bisect import bisect_left, bisect_right

# Known DroneCAN message type IDs => human names
# These are from the DSDL definitions
KNOWN_MSG_TYPES = {
    341: "NodeStatus",
    1009: "TimeSync",
    1010: "GetNodeInfo",
    2000: "Beacon",
    1001: "GNSSFix",
    1060: "GNSSFix2",
    1065: "GNSSAuxiliary",
    1008: "BatteryInfo",
    1070: "RTCMStream",
    8000: "ESCStatus",
    8001: "ESCStatusExtended",
    16381: "UAVCANDebug",
}

def can_to_nodeid(can_id_hex: str) -> int:
    """Extract DroneCAN node ID (lowest 7 bits of the 29-bit CAN ID)."""
    can_id = int(can_id_hex, 16) & 0x1FFFFFFF
    return can_id & 0x7F

def can_to_msg_type(can_id_hex: str) -> int:
    """Extract the message type ID from the CAN ID.
    
    DroneCAN extended ID format (29 bits):
      Bits 28-26: priority (3 bits, 0=highest)
      Bit 25: reserved (0)
      Bits 24-8: subject ID (17 bits) for broadcast messages
      Bits 7-0: source node ID (but only bits 6-0 are used, bit 7 reserved)
    
    Actually the exact layout depends on service vs message.
    For broadcast messages:
      priority: bits 28-26
      subject ID: bits 24-8 (17 bits)
      source node ID: bits 7-0 (but effectively 7 bits, bit 7 = 0)
    
    For service transfers, the format differs slightly but we only
    see broadcast messages in candump.
    """
    can_id = int(can_id_hex, 16) & 0x1FFFFFFF
    # Remove lower 8 bits (source node ID byte, bit 7 reserved 0)
    msg_type = (can_id >> 8) & 0x1FFFF  # 17 bits
    return msg_type

def parse_candump_line(line: str):
    """Parse a single candump line. Returns (timestamp_s, can_id_hex, data_hex) or None."""
    line = line.strip()
    if not line:
        return None
    # Format: (timestamp) can0 CANID#DATA
    # Or: can0 CANID#DATA
    m = re.match(r'^\((\d+\.\d+)\)\s+\S+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]+)', line)
    if m:
        ts = float(m.group(1))
        can_id = m.group(2).upper()
        data = m.group(3)
        return (ts, can_id, data)
    # Try without timestamp
    m = re.match(r'^\S+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]+)', line)
    if m:
        can_id = m.group(1).upper()
        data = m.group(2)
        return (0.0, can_id, data)
    return None

def compute_intervals(ts_list):
    """Given sorted list of timestamps, return list of intervals."""
    if len(ts_list) < 2:
        return []
    return [ts_list[i+1] - ts_list[i] for i in range(len(ts_list)-1)]

def sliding_window_mean_intervals(ts_list, window_s=60.0):
    """Compute mean interval within each sliding window. Returns list of means."""
    if len(ts_list) < 3:
        return []
    
    intervals = compute_intervals(ts_list)
    
    # For each timestamp position, consider the window [t, t+window_s)
    # and compute the mean interval of messages within that window.
    # Step by 1 second.
    t_min = ts_list[0]
    t_max = ts_list[-1]
    
    window_means = []
    # Window granularity = 1s, but we start from t_min and go to t_max - window_s
    cur = t_min
    while cur + window_s <= t_max:
        # Find messages in [cur, cur + window_s)
        start_idx = bisect_left(ts_list, cur)
        end_idx = bisect_right(ts_list, cur + window_s)
        in_window = ts_list[start_idx:end_idx]
        
        if len(in_window) >= 3:
            win_intervals = [in_window[i+1] - in_window[i] for i in range(len(in_window)-1)]
            if win_intervals:
                window_means.append(sum(win_intervals) / len(win_intervals))
        
        cur += 1.0
    
    return window_means

def analyze_candump(filepath: str, output_dir: str):
    """Analyze a candump file and produce per-node CSVs."""
    print(f"Analyzing {filepath}...")
    
    # Structure: { (node_id, can_id): [timestamps] }
    messages = defaultdict(list)
    line_count = 0
    parse_errors = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line_count += 1
            parsed = parse_candump_line(line)
            if not parsed:
                parse_errors += 1
                continue
            ts, can_id, _ = parsed
            node = can_to_nodeid(can_id)
            msg_type = can_to_msg_type(can_id)
            messages[(node, can_id)].append(ts)
    
    print(f"  Parsed {line_count} lines, {parse_errors} skip, {len(messages)} unique (node, CAN ID) pairs")
    
    # Sort timestamps for each pair
    for key in messages:
        messages[key].sort()
    
    # Group by node
    nodes = defaultdict(dict)  # { node_id: { can_id: [timestamps] } }
    for (node, can_id), ts_list in messages.items():
        nodes[node][can_id] = ts_list
    
    print(f"  Found {len(nodes)} nodes: {sorted(nodes.keys())}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for node in sorted(nodes.keys()):
        rows = []
        for can_id in sorted(nodes[node].keys()):
            ts_list = nodes[node][can_id]
            msg_type = can_to_msg_type(can_id)
            msg_name = KNOWN_MSG_TYPES.get(msg_type, f"0x{msg_type:04X}")
            
            count = len(ts_list)
            intervals = compute_intervals(ts_list)
            
            if intervals:
                max_int = max(intervals)
                overall_mean = (ts_list[-1] - ts_list[0]) / max(1, (count - 1))
            else:
                max_int = 0.0
                overall_mean = 0.0
            
            # 60s sliding window means
            win_means = sliding_window_mean_intervals(ts_list, 60.0)
            if win_means:
                mean60 = sum(win_means) / len(win_means)
                min60 = min(win_means)
                max60 = max(win_means)
            else:
                mean60 = 0.0
                min60 = 0.0
                max60 = 0.0
            
            rows.append({
                'can_id': can_id,
                'msg_type_id': f"0x{msg_type:04X} ({msg_type})",
                'msg_name': msg_name,
                'count': count,
                'duration_s': round(ts_list[-1] - ts_list[0], 3) if count >= 1 else 0,
                'max_interval_s': round(max_int, 3),
                'overall_mean_s': round(overall_mean, 6),
                'mean60_s': round(mean60, 6),
                'min60_s': round(min60, 6),
                'max60_s': round(max60, 6),
            })
        
        if not rows:
            continue
        
        csv_path = os.path.join(output_dir, f"node_{node}.csv")
        fieldnames = ['can_id', 'msg_type_id', 'msg_name', 'count', 'duration_s',
                      'max_interval_s', 'overall_mean_s', 'mean60_s', 'min60_s', 'max60_s']
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"  Wrote {csv_path} ({len(rows)} message types, node {node})")
        
        # Print summary for this node
        print(f"\n  ┌─ Node {node} ─{'-' * 60}┐")
        for r in rows:
            if r['count'] < 2:
                print(f"  │ {r['msg_name']:25s} (0x{r['can_id']:8s})  {r['count']:6d} msgs  (single message)    │")
            else:
                print(f"  │ {r['msg_name']:25s} (0x{r['can_id']:8s})  {r['count']:6d} msgs  max_gap={r['max_interval_s']:8.3f}s  mean={r['mean60_s']:8.6f}s  │")
        print(f"  └{'─' * 74}┘")
    
    print(f"\nDone. Output in {output_dir}/")

if __name__ == '__main__':
    # Process the two most recent candump logs
    log_dir = "/home/robs/Projects/inav-claude/claude/developer/scripts/testing/sd-card-test/sd_card_test/overnight_logs"
    output_dir = os.path.join(log_dir, "analysis")
    
    # Most recent first
    logs = [
        "candump_20260517_191120.log",
        "candump_20260517_190722.log",
        "candump_20260517_181537.log",
    ]
    
    for log in logs:
        path = os.path.join(log_dir, log)
        if os.path.exists(path):
            analyze_candump(path, os.path.join(output_dir, log.replace('.log', '')))
