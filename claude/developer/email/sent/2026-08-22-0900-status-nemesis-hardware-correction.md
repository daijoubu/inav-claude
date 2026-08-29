# Status Update: Hardware Record Correction — NEMESIS Craft Configuration

**Date:** 2026-08-22 09:00
**From:** Developer
**To:** Manager
**Re:** fix-dronecan-cell-voltage-calculation / NEMESIS hardware verification

## Finding

The task assignment (`claude/developer/email/inbox/2026-08-21-1430-task-dronecan-cell-voltage.md`) and the project summary.md both state that NEMESIS (the craft in the 2026-08-16 crash footage) is equipped with a **KAKUTEH7WING** flight controller board.

**Developer confirmed with the user (the pilot/owner): this is incorrect.** NEMESIS is actually a **MATEKF765SE**, not a KAKUTEH7WING.

The KAKUTEH7WING is a bench-only board used for DroneCAN testing hardware validation. It has never been installed on NEMESIS and is not flown.

## Why It Matters

1. **ADC scaling assumptions** — the cell-voltage bug investigation assumes certain ADC input ranges and scaling factors tied to the target board's hardware. A MATEKF765SE has different power delivery, voltage dividers, and ADC input impedance than a KAKUTEH7WING would.

2. **DroneCAN wiring specifics** — each board has different CAN transceiver integration and pinouts. Wiring faults or noise coupling on one board may not apply to the other.

3. **Source code paths** — firmware builds include target-specific configuration and HAL layers. Investigating cell-voltage calculation under a KAKUTEH7WING's assumptions might miss target-specific bugs or hardware-specific edge cases that affect a MATEKF765SE.

## Record Update Needed

Recommend updating:
- `claude/projects/active/fix-dronecan-cell-voltage-calculation/summary.md` (line 20-22 currently states KAKUTEH7WING; should state MATEKF765SE)
- The task assignment email (2026-08-21-1430-task-dronecan-cell-voltage.md) if a new assignment is issued, to reflect the correct hardware

**Note:** This is a gap in the original task information provided, not a developer error. Nobody had explicitly confirmed which board was actually on the plane before the task was created.

## SD Card Investigation Update

Developer obtained and examined the SD card physically removed from NEMESIS (label: **EE28-F9BF**), hoping to recover the 2026-08-16 blackbox log from the crash flight.

**Card contents:**
- 1,018 log files total
- All logs from a MATEKF765SE (correct board)
- All logs dated **2026-05-07** (bench endurance-test session, ~5 months old)
- Last log file is 0 bytes (cleanly marked the end of that session)
- Card has 11 GB free space remaining (not full)
- No logs from 2026-08-16 present

**Conclusion:** This specific SD card was used for bench testing on 2026-05-07 and was never used again after that session. It was not in NEMESIS during the 2026-08-16 flight. The actual card that was in the craft on crash day remains unlocated.

**Next:** Developer still needs the **physical SD card that was actually in NEMESIS on 2026-08-16** to recover blackbox data for the investigation. This may help isolate whether the cell-voltage anomaly was specific to that flight or is a consistent reproducible bug.

---
**Developer**
