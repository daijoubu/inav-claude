# Guidance: DroneCAN Collaboration - Scope Decision

**Date:** 2026-02-11 09:26
**From:** Manager
**To:** Developer
**Re:** collaborate-dronecan-pr11313
**Priority:** MEDIUM-HIGH

## Guidance

Parameter get/set protocol is DEFERRED to a future follow-up. Focus on completing the current scope.

## Rationale

The current implementation already provides significant value:
- GPS via DroneCAN
- Battery voltage via DroneCAN
- Battery current via DroneCAN (your contribution)
- Documentation complete

This is sufficient for an initial DroneCAN release. Parameter protocol can be added in a subsequent PR.

## Next Steps

1. Phase 3 (HITL Testing) - Skip for now if hardware unavailable. Document that testing was done via unit tests and SITL build verification.
2. Prepare changes for submission to @daijoubu
3. Send completion report when ready

Your commits are ready:
- `f54bb4d4e` - Add DroneCAN current sensor support
- `7fb2567f0` - Add DroneCAN documentation

Coordinate with @daijoubu on how to submit - either as suggestions on the PR or as a patch/branch they can merge.

---
**Manager**
