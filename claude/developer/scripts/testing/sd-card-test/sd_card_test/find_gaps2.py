#!/usr/bin/env python3
"""
Correlate gap events across all nodes and message types.
"""
import re
from collections import defaultdict

def parse_line(line):
    m = re.match(r'^\((\d+\.\d+)\)\s+\S+\s+([0-9A-Fa-f]+)#', line)
    if m:
        return float(m.group(1)), m.group(2).upper()
    return None

log_dir = "/home/robs/Projects/inav-claude/claude/developer/scripts/testing/sd-card-test/sd_card_test/overnight_logs"
log_file = f"{log_dir}/candump_20260517_191120.log"

msgs = defaultdict(list)
with open(log_file) as f:
    for line in f:
        p = parse_line(line)
        if p:
            ts, can_id = p
            node = int(can_id, 16) & 0x7F
            msgs[(node, can_id)].append(ts)

# For each (node, can_id), find gaps > 2x expected interval
# Expected intervals: 1s for NodeStatus, 0.040s for GNSSFix, etc.
EXPECTED = {
    "18015501": 1.0,     # FC NodeStatus
    "1801554B": 1.0,     # GNSS NodeStatus
    "1401557F": 1.0,     # SLCAN NodeStatus
    "1803E94B": 0.040,   # GNSSFix (25Hz)
    "1804254B": 0.067,   # (15Hz)
    "1804274B": 0.020,   # (50Hz)
    "184E234B": 0.200,   # (5Hz)
}

print("=== BIG GAP EVENTS (>3x expected interval) ===")
print(f"{'NODE':>5s} {'CAN_ID':>10s} {'EXPECTED':>10s} {'GAP':>10s} {'GAP_START':>16s} {'GAP_END':>16s}")
print(f"{'─'*5} {'─'*10} {'─'*10} {'─'*10} {'─'*16} {'─'*16}")

all_big_gaps = []
for (node, can_id), ts_list in msgs.items():
    if can_id not in EXPECTED:
        continue
    expected = EXPECTED[can_id]
    ts_list.sort()
    for i in range(len(ts_list) - 1):
        gap = ts_list[i+1] - ts_list[i]
        if gap > expected * 3:
            all_big_gaps.append((ts_list[i], ts_list[i+1], gap, node, can_id, expected))

all_big_gaps.sort(key=lambda x: x[0])
for gs, ge, gap, node, cid, exp in all_big_gaps:
    print(f"{node:5d} {cid:>10s} {exp:10.3f}s {gap:10.3f}s {gs:16.3f} {ge:16.3f}")

# Show the last few seconds of the log (the failure)
print(f"\n=== LAST 60 SECONDS OF LOG ===")
ts_n1 = msgs[(1, "18015501")]
ts_n75_gnss = msgs[(75, "1803E94B")]
ts_n127 = msgs[(127, "1401557F")]

all_end = [ts[-1] for ts in [ts_n1, ts_n75_gnss, ts_n127]]
last_ts = max(all_end)
print(f"Last FC NodeStatus:   {ts_n1[-1]:.3f}")
print(f"Last GNSSFix:         {ts_n75_gnss[-1]:.3f}")
print(f"Last SLCAN NodeStatus: {ts_n127[-1]:.3f}")

# Show message intervals in last 30 seconds
print(f"\n  Last 30s FC NodeStatus intervals:")
fc_intervals = [ts_n1[i+1] - ts_n1[i] for i in range(len(ts_n1)-1) if ts_n1[i] > last_ts - 30]
for i, intv in enumerate(fc_intervals):
    marker = " <<< HWFAIL!" if intv > 2.0 else ""
    print(f"    interval={intv:.3f}s{marker}")

# Show when the FC stopped transmitting
ts_end = last_ts
for i in range(len(ts_n1)-2, -1, -1):
    if ts_n1[i+1] - ts_n1[i] > 2.0:
        print(f"\n  FC stopped transmitting at t={ts_n1[i]:.3f} (last msg at {ts_n1[i]:.3f}, next at {ts_n1[i+1]:.3f}, gap={ts_n1[i+1]-ts_n1[i]:.3f}s)")
        print(f"  HWFAIL likely set at ~t={ts_n1[i] + 1.0:.3f} (1s GPS timeout * 5 timeouts)")
        break

# Show GNSS module last gaps
print(f"\n  GNSS module last 5 gaps (>0.1s only):")
gnss_gaps = [(ts_n75_gnss[i], ts_n75_gnss[i+1], ts_n75_gnss[i+1]-ts_n75_gnss[i]) for i in range(len(ts_n75_gnss)-1) if ts_n75_gnss[i+1]-ts_n75_gnss[i] > 0.1]
for g in gnss_gaps[-5:]:
    print(f"    t={g[0]:.3f} gap={g[2]:.3f}s")
