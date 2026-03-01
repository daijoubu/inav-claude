# Project: Investigate Bidir DShot Simultaneous Motor RX / DMAR Compatibility

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-02-28
**Estimated Effort:** 4-8 hours

## Overview

Determine whether reading GCR telemetry responses from up to four motors simultaneously (rather than per-channel sequentially) is feasible, and whether such an approach would allow DMAR burst mode to be retained alongside bidirectional DShot.

## Background

The existing feasibility study (see `completed/investigate-bidirectional-dshot/`) concluded that `USE_DSHOT_DMAR` and `USE_DSHOT_TELEMETRY` cannot coexist, because Betaflight's bidirectional DShot uses per-channel DMA (one DMA stream per motor, switching between OC and IC mode per motor). This requires disabling DMAR burst mode.

The open question is: **is per-channel DMA actually necessary, or is it just Betaflight's chosen approach?**

## Research Question

Betaflight switches each motor's DMA stream individually from output-compare (OC) to input-capture (IC) mode after TX completes. Each motor has its own DMA stream and GCR decode happens independently per motor.

**Alternative hypothesis:** If all motors' ESCs respond to the DShot frame within the same narrow time window, could we:

1. Send the DShot frame to all motors simultaneously via DMAR burst (as today)
2. Then switch the entire timer (or all motor channels simultaneously) to IC mode
3. Capture all motors' GCR responses in parallel — one DMA capture per motor channel, but triggered together
4. Decode each motor's GCR independently after all captures complete

If simultaneous RX is feasible, DMAR burst could potentially be used for TX (Step 1), with all motors switching to RX mode together after the burst completes. This would avoid the DMAR/telemetry mutual exclusion in the current plan.

## Key Questions to Answer

1. **Timing:** Do all ESC GCR responses start and end within the same time window? Is the response window deterministic enough to trigger simultaneous IC DMA for all motors?

2. **Timer architecture:** Can multiple channels on the same timer switch from OC to IC mode simultaneously in a single register write? Or must they be switched individually?

3. **DMA resources:** If each motor channel needs its own IC DMA stream for simultaneous capture, how does the DMA resource budget compare to the per-channel sequential approach?

4. **DMAR compatibility:** Does the DMAR burst TX approach finish cleanly in a way that allows a coordinated switch to simultaneous IC RX? What are the handoff mechanics?

5. **STM32H7 specifics:** Does the H7's DMAMUX make simultaneous multi-channel IC DMA more or less feasible than F4/F7?

6. **Betaflight's rationale:** Is there documentation or commit history explaining why Betaflight chose per-channel sequential RX rather than simultaneous? Was simultaneous RX considered and rejected?

## Success Criteria

- [ ] Clear answer on whether simultaneous multi-motor RX is timing-feasible
- [ ] Assessment of timer register mechanics for simultaneous OC→IC switch
- [ ] DMA resource count for simultaneous vs. sequential approach
- [ ] Verdict: Does simultaneous RX allow retaining DMAR burst for TX?
- [ ] If yes: outline the revised implementation approach
- [ ] If no: confirm current plan (per-channel DMA, DMAR mutually exclusive) is correct

## Related

- **Implementation project (on hold):** `active/feature-bidirectional-dshot-h7/`
- **Feasibility report:** `claude/projects/completed/investigate-bidirectional-dshot/`
- **Betaflight reference:** BF bidirectional DShot implementation (dshot_bidir.c)
