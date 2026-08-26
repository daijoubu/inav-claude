# No Action Required

Issues reviewed and determined to not require action (won't fix, duplicate, already fixed, user error, out of scope).

---

## Issues

### inav #11710 - SITL scheduler sleep pins averageSystemLoadPercent at 100%+, blocking arming

**Reviewed:** 2026-08-10
**Reason:** already-fixed
**URL:** https://github.com/iNavFlight/inav/issues/11710

**Summary:**
Reported against 9.1 SITL: `averageSystemLoadPercent` pinned ≥100%, blocking arming, caused by the SITL scheduler `usleep()` change in #11436. Fixed by #11720 (merged to `release/9.1`), forward-merged via #11727, with build-break follow-up #11738. Confirmed the fix commits (`5e47ffd3`, `ca26d31b`) are present on `master`. Closed the issue with an explanatory comment since it hadn't auto-closed (PR targeted `release/9.1`, not `master`).

---

### inav-configurator #2697 - Target build issue on boards with HSE value 25000000 on INAV 9.1.0

**Reviewed:** 2026-08-10
**Reason:** duplicate
**URL:** https://github.com/iNavFlight/inav-configurator/issues/2697

**Summary:**
Closed by Ray — same reporter is discussing the same HSE-25MHz build issue on inav PR #11756, so tracking there rather than as a separate configurator issue.

**Related:** https://github.com/iNavFlight/inav/pull/11756

---

### inav #11725 - question on javascript programming

**Reviewed:** 2026-08-10
**Reason:** out-of-scope
**URL:** https://github.com/iNavFlight/inav/issues/11725

**Summary:**
"How do I..." support question about using programming/mixer logic for a tail-sitter transition, not a bug or actionable feature request. Better suited to the forum/Discord.

---

### inav #11667 - Hope to develop a new flight controller to add to INAV

**Reviewed:** 2026-08-10
**Reason:** out-of-scope
**URL:** https://github.com/iNavFlight/inav/issues/11667

**Summary:**
A vendor asking how to get a new H743-based FC supported (offering schematics/hardware, asking for dev guidance) — a collaboration request, not a concrete code issue. Replied with a link to [NEW_HARDWARE_POLICY.md](https://github.com/iNavFlight/inav/blob/master/docs/policies/NEW_HARDWARE_POLICY.md) and the Discord invite (https://discord.gg/peg2hhbYwN) so they can coordinate with core developers directly. Left open pending their response.

---

### inav #11647 - inav目前支持stm32 g474芯片吗 (does INAV support STM32 G474?)

**Reviewed:** 2026-08-10
**Reason:** out-of-scope
**URL:** https://github.com/iNavFlight/inav/issues/11647

**Summary:**
Support question (in Chinese) asking whether a BetaFPV G473-based AIO FC is supported. Not a bug/feature request against existing code.

---

### inav-configurator #2662 - "inav"

**Reviewed:** 2026-08-10
**Reason:** user-error
**URL:** https://github.com/iNavFlight/inav-configurator/issues/2662

**Summary:**
Title and body are both just "inav" — no actionable content. Closed by Ray 2026-08-11.

---

### inav-configurator #2667 - HGLRC M100 PRO Magnetometer NOT Working on iNAV 9.02

**Reviewed:** 2026-08-11
**Reason:** already-fixed (config answer, not a bug)
**URL:** https://github.com/iNavFlight/inav-configurator/issues/2667

**Summary:**
Reporter had replaced the module's original QMC5883L mag chip with a QMC5883P. Ray replied: select QMC5883P in the Configuration tab (or set to Auto). Moved out of hardware-dependent.md — no hardware needed, this was a configuration answer.

<!-- Template for adding issues:

### #XXXXX - Issue Title

**Reviewed:** YYYY-MM-DD
**Reason:** already-fixed | duplicate | wont-fix | user-error | out-of-scope
**URL:** https://github.com/iNavFlight/inav/issues/XXXXX

**Summary:**
Brief description of why no action is needed.

**Related:** (if duplicate, link to original)

-->
