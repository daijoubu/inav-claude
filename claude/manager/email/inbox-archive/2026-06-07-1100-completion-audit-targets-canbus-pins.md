# Task Complete: Audit AP H7/F7 Targets — Add CAN Bus Pins

**Date:** 2026-06-07 11:00
**From:** Developer
**To:** Manager
**Re:** audit-targets-canbus-pins
**Type:** Completion Report

## Status: COMPLETE

PR open: https://github.com/iNavFlight/inav/pull/11631
Branch: feature/audit-targets-canbus-pins → maintenance-10.x
Build matrix: all pass (F4/F7/H7/AT32/SITL), zero warnings.

---

## What Was Done

Audited all 108 H7/F7 INAV targets against the ArduPilot hwdef directory. Added commented-out CAN1 pin blocks to 7 targets where pins were confirmed in AP and verified free in INAV.

**Targets updated:**

| Target | CAN1 RX | CAN1 TX | CAN1 STANDBY | AP Source |
|--------|---------|---------|-------------|-----------|
| AETH743Basic | PD0 | PD1 | PD3 | AET-H743-Basic |
| BROTHERHOBBYH743 | PD0 | PD1 | PD3 | BROTHERHOBBYH743 |
| CORVON743V1 | PB8 | PB9 | — | CORVON743V1 |
| DAKEFPVH743PRO | PD0 | PD1 | PD2 | DAKEFPVH743Pro |
| MICOAIR743 | PB8 | PB9 | — | MicoAir743 |
| TBS_LUCID_H7 | PD0 | PD1 | PD3 | TBS_LUCID_H7 |
| TBS_LUCID_H7_WING | PD0 | PD1 | PD3 | TBS_LUCID_H7_WING |

All definitions are **commented out** — sourced from AP hwdef but not validated on real hardware. Normal builds are unaffected.

---

## Validation Steps Performed

- AP hwdef include chains checked to rule out pin overrides (caught DAKEFPVH743 — AP inherits CAN from Pro hwdef then immediately repurposes PD0/PD1 as UART4)
- Each CAN pin verified free in the INAV target.h (no UART/SPI/I2C conflicts)
- Standby pin polarity confirmed consistent with existing INAV targets (active-high silent, driven LOW on init)
- Open PRs checked: #11403 (AETH743Basic gyro update) touches target.h but our addition is a separate block with no conflict; #11609/#11610 (new TBS variants) don't touch our targets

---

## Excluded Targets and Reasons

| Category | Count | Reason |
|----------|-------|--------|
| Already have CAN active | 3 | KAKUTEH7WING, MATEKH743, MATEKF765 |
| No AP hwdef equivalent | 76 | No reference source per task spec |
| AP hwdef exists but no CAN pins defined | 18 | AP didn't wire CAN — likely not routed to connector |
| DAKEFPVH743 | 1 | CAN pins conflict with UART4 in both AP and INAV |
| TBS_LUCID_H7_WING_MINI | 1 | No dedicated AP hwdef; PCB differences from WING make inference unsafe |

---

## Notes for Reviewers

- DAKEFPVH743PRO uses PD2 as standby (not the usual PD3) — sourced directly from its AP hwdef
- CORVON743V1 and MICOAIR743 have no standby pin in their AP hwdef
- Two open PRs (#11609, #11610) add new TBS_LUCID_H7_V3 and TBS_LUCID_H7_OEM targets with no CAN — worth a follow-up audit once those merge

---
**Developer**
