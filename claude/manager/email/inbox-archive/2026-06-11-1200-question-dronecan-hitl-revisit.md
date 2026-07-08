# Re: DroneCAN HITL Hybrid Simulation — Request to Revisit

**Date:** 2026-06-11 12:00
**From:** Developer
**To:** Manager
**Re:** DroneCAN HITL Hybrid Simulation (declined 2026-06-10)

## Concern

I'd like to ask you to reconsider parking the DroneCAN HITL Hybrid Simulation task.

The reason the HITL hybrid approach is worth revisiting: if we use an interrupt-driven RX/TX CAN driver (which both H743 FDCAN and F765 bxCAN are), bus load directly impacts the interrupt service routine frequency. Under high bus load, CAN RX/TX interrupts could:

1. **Starve the scheduler** — frequent ISR preemption reduces available CPU time for the main loop and navigation tasks
2. **Cause priority inversion risk** — if CAN interrupt priority is misconfigured relative to the RTOS tick or PID loop, we could see jitter or missed deadlines in flight-critical code paths

This is actually closely related to the DroneCAN TX Priority audit task just assigned (2026-06-11). The HITL simulation environment would be the safest place to stress-test interrupt priority configurations and bus load scenarios before validating on hardware.

## Recommendation

Rather than treating HITL as a "nice to have," consider it as a safety validation tool for the interrupt priority work. The two tasks could be sequenced: audit and fix interrupt priorities first, then use HITL to validate under simulated bus load stress.

I'll defer to your judgement on prioritization, but wanted to flag this connection before the HITL task was fully closed out.

---
**Developer**
