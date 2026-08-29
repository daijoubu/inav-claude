# Task Completed: Respond to Maintainer Feedback on PR #11729

**Date:** 2026-08-28 14:30
**From:** Developer
**To:** Manager
**Type:** Completion Report
**Project:** feature-canbus-errors-blackbox
**Re:** Maintain review comment on iNavFlight/inav#11729

## Status: COMPLETED

## Summary

Completed response to maintainer's top-level review comment on PR #11729 (posted 2026-08-28 04:00 UTC). Reply addresses both technical questions (predictor choice and delta/rate field) with clear findings and recommendation to merge as-is. All success criteria met: reply posted, clear recommendation given, no code changes needed.

## Task Completion

All success criteria from task assignment satisfied:

- [x] Reply posted to maintainer's PR comment addressing both predictor question and delta/rate question
- [x] Clear recommendation given: decline the `PREDICT(PREVIOUS)` change, merge as-is
- [x] No code changes needed or warranted (reply-only task)
- [x] Status report sent to manager (this email)

**Reply posted:** https://github.com/iNavFlight/inav/pull/11729#issuecomment-5454889371

## Findings

### 1. Predictor Question: `PREDICT(0)` is Correct

**Recommendation:** Decline the change to `PREDICT(PREVIOUS)`. Current declaration is correct per specification.

**Evidence:** In addition to earlier 2026-08-23 decoder-tracing analysis (both `blackbox-tools` and JS decoder pass `previous=NULL` for S-frames, making `PREDICT(PREVIOUS)` a no-op), found stronger specification-level corroboration in `docs/development/Blackbox Internals.md`:

> "All Slow frames are logged as intraframes. An interframe encoding scheme can't be used for Slow frames..."

This directly contradicts using `PREDICT(PREVIOUS)` (an interframe predictor) on S-frame fields. The mismatch isn't a missed optimization—it's a spec-level violation. `PREDICT(0)` is the only valid declaration for S-frame fields.

### 2. Pre-existing Bug Discovered

**Finding:** Two existing S-frame fields (`rxUpdateRate` and `escTemperature`) are themselves misdeclared as `PREDICT(PREVIOUS)`, in violation of the same specification rule. This is pre-existing, not introduced by PR #11729.

**Recommendation:** Flag for separate follow-up issue (see Open Item below). This PR should not be blocked on fixing unrelated pre-existing issues.

### 3. Delta/Rate Field Question

**Recommendation:** Cumulative-only is correct. Do not add a delta/rate field.

**Reasoning:** DroneCAN bus-off trips when CAN TEC (Transmit Error Counter) reaches 256, incrementing 8 per transmit error. At current transmit rates, 60+ seconds of accumulated errors are required before a bus-off event occurs. This means a bus-off event can never be cleanly traced back to the specific environmental condition that triggered the underlying transmit errors—a delta/rate field wouldn't fix that fundamental timing mismatch.

The cumulative count's actual purpose is coarser: to provide blackbox evidence that CAN hardware was faulty, distinguishing hardware faults from software bugs when sensor data or servo control goes bad in the same flight. Cumulative-only suffices for this use case.

Rejected alternative of logging raw TEC/REC counters: they change faster than the DroneCAN service dispatch cadence, producing near-random snapshots rather than meaningful state in slow frames. Also, some nonzero TEC/REC is normal—better suited for live CLI inspection during bench testing, not logged to blackbox.

## Recommendation

**Merge PR #11729 as-is** — no code changes needed. The PR is clean, small (+17/-1), no RAM/flash impact, and ready for review. Keep in mind RC1 deadline (2026-09-01) noted by maintainer—this PR should not stall.

## Open Item: Follow-up GitHub Issue

**Question for manager:** Should I file the `rxUpdateRate`/`escTemperature` predictor-reclassification issue now as a tracked follow-up project, or hold until PR #11729 merges and maintainer responds?

The issue is legitimate (spec-level mismatch in two existing S-frame fields) but pre-existing and not urgent. Filing now gives it visibility, but the maintainer may have context or plans for when to handle it. Recommend deferring until after this PR lands and getting the maintainer's input on priority.

## Next Steps

1. Awaiting manager direction on filing the predictor-reclassification follow-up issue
2. Ready for user to merge PR #11729 when maintainer approves

---
**Developer**
