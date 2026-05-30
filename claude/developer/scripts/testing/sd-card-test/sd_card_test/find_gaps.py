#!/usr/bin/env python3
"""
Find and correlate gap events (>250ms) across all message types for node 75.
Shows when gaps happen relative to each other.
"""
import re
import sys
from collections import defaultdict
from bisect import bisect_left

def parse_line(line):
    m = re.match(r'^\((\d+\.\d+)\)\s+\S+\s+([0-9A-Fa-f]+)#', line)
    if m:
        return float(m.group(1)), m.group(2).upper()
    return None

def msg_type_from_can(can_id_hex):
    can_id = int(can_id_hex, 16) & 0x1FFFFFFF
    return (can_id >> 8) & 0x1FFFF

log_dir = "/home/robs/Projects/inav-claude/claude/developer/scripts/testing/sd-card-test/sd_card_test/overnight_logs"
log_file = f"{log_dir}/candump_20260517_191120.log"

# Collect timestamps by (node, can_id)
msgs = defaultdict(list)
with open(log_file) as f:
    for line in f:
        p = parse_line(line)
        if p:
            ts, can_id = p
            node = int(can_id, 16) & 0x7F
            msgs[(node, can_id)].append(ts)

# Focus on node 75
node75 = {k: v for k, v in msgs.items() if k[0] == 75}

# Find gaps > 250ms for each message type
GAP_THRESHOLD = 0.25

# Identify gap events: a set of (message_can_id, gap_start, gap_end, gap_duration)
all_gaps = []
for (node, can_id), ts_list in node75.items():
    ts_list.sort()
    for i in range(len(ts_list) - 1):
        gap = ts_list[i+1] - ts_list[i]
        if gap > GAP_THRESHOLD:
            msg_type = msg_type_from_can(can_id)
            all_gaps.append((ts_list[i], ts_list[i+1], gap, can_id, msg_type))

all_gaps.sort(key=lambda x: x[0])  # sort by gap start time

# Print gap events
print(f"{'GAP_START':>16s} {'GAP_END':>16s} {'DURATION':>10s} {'CAN_ID':>10s} {'MSG_TYPE':>10s}")
print(f"{'─'*16} {'─'*16} {'─'*10} {'─'*10} {'─'*10}")
for gs, ge, dur, cid, mt in all_gaps[:30]:
    print(f"{gs:16.3f} {ge:16.3f} {dur:10.3f} {cid:>10s} 0x{mt:04X}")

print(f"\n... (showing first 30 of {len(all_gaps)} gap events)")

# Now check: are gaps synchronized? Find gaps > 2.5s (big dropouts)
big_gaps = [g for g in all_gaps if g[2] > 2.5]
print(f"\n=== BIG GAPS (>2.5s): {len(big_gaps)} events ===")
for gs, ge, dur, cid, mt in big_gaps:
    print(f"  t={gs:.3f} gap={dur:.3f}s  {cid}  0x{mt:04X}")

# Check correlation: are different message types dropping at the same time?
# For each big gap in the highest-rate message (0x427), check if other types also gap nearby
print(f"\n=== CORRELATION: Do other message types gap during 0x0427 gaps? ===")
ref_cid = "1804274B"
ref_gaps = [g for g in big_gaps if g[3] == ref_cid]
ref_gaps.sort()

other_types = sorted(set(g[3] for g in node75.keys()) - {ref_cid})
print(f"  Reference message: {ref_cid} (rate: ~50Hz, {len(ref_gaps)} big gaps)")
print(f"  Other types: {other_types}")
print()

import math

for i, (ref_gs, ref_ge, ref_dur, _, _) in enumerate(ref_gaps[:10]):
    # Check if other types have a gap that overlaps or is within 1s of this reference gap
    correlated = []
    for oth_cid in other_types:
        oth_list = node75[(75, oth_cid)]
        # Find the nearest gap in this type
        oth_gaps = [g for g in all_gaps if g[3] == oth_cid]
        for og in oth_gaps:
            if abs(og[0] - ref_gs) < 3.0 or abs(og[1] - ref_ge) < 3.0:
                correlated.append((oth_cid, og[2]))
                break
    print(f"  Gap {i+1}: t={ref_gs:.1f}s duration={ref_dur:.3f}s")
    for oth_cid, oth_dur in correlated:
        short = oth_cid.replace("180", "").replace("18", "")
        print(f"    correlated: {oth_cid} gap={oth_dur:.3f}s")
