# Status Update: Qodo Finding on PR #11729 Addressed

**Date:** 2026-08-23 14:00
**From:** Developer
**To:** Manager
**Type:** Status Update
**Project:** feature-canbus-errors-blackbox
**Re:** PR #11729 (addendum to today's earlier rebase completion report)

## Current Status

Also removed the stale "Do not merge before #11607" dependency note from the PR description (that PR merged, no longer applicable).

Qodo flagged one finding on PR #11729 after the rebase completion report was sent: `droneCANBusOffCount`'s blackbox slow-frame field uses `PREDICT(0)` instead of `PREDICT(PREVIOUS)`, claiming the latter would shrink log size for a monotonically increasing counter. This is now resolved — declined, with a detailed technical reply posted to the PR thread.

## What Was Found

Traced both real blackbox decoders (`blackbox-tools`/`blackbox_decode`'s `parser.c`, and the JS `flightlog_parser.js` used by INAV Blackbox Explorer) to verify the claim before accepting or declining it. Result: `PREDICT(PREVIOUS)` is a no-op for S-frame fields in both — `parseSlowFrame()` in each passes `previous = NULL` to the generic frame parser, and `applyPrediction()`'s `PREDICT_PREVIOUS` case is guarded on `if (!previous) break;`, so it decodes identically to `PREDICT(0)`.

On INAV's encoder side, `writeSlowFrame()` (`blackbox.c`) never computes an actual delta for any S-frame field — every field is written as its full absolute value via `blackboxWriteUnsignedVB`/`blackboxWriteSignedVB`, regardless of declared predictor. This is also true of two existing fields already declared `PREDICT(PREVIOUS)` (`rxUpdateRate`, `escTemperature`) — so Qodo's suggested one-line change would have been cosmetic only (no actual size reduction), and applying it without also adding real delta-computation logic to the encoder would have been safe only by accident (relies on both current decoders happening to ignore the declaration).

## Broader Issue Flagged (not blocking, worth awareness)

The PR reply also flags this as a latent, pre-existing trap in the mainline blackbox format/firmware pairing, unrelated to this branch: a decoder author who trusts the log header's `Field S predictor` line at face value (reasonable, since that's how I/P frames work) would implement real `PREDICT_PREVIOUS` delta-application for S-frames and get wrong reconstructed values for `rxUpdateRate`/`escTemperature` today, since INAV's encoder doesn't actually delta-encode them despite declaring it. Might be worth a separate low-priority cleanup task (either implement real delta-encoding for these fields, or just declare them accurately as `PREDICT(0)` to match reality) — flagging for your awareness, not asking to scope it now.

## PR Status

PR #11729 remains ready for review (not draft). Reply posted: https://github.com/iNavFlight/inav/pull/11729#discussion_r3839243425

## Next Steps

None — this task is complete.

---
**Developer**
