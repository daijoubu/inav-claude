# Task Assignment: Address Qodo bot findings on PR #2671 (configurator)

**Date:** 2026-08-22 10:00
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-configurator-tab
**Priority:** HIGH
**Estimated Effort:** 2-4 hours (investigation + test coverage; see note on implementation below)

## Task

Qodo's automated code review bot flagged 5 findings on PR #2671 ("feat(dronecan): DroneCAN node configurator tab — GetNodeInfo, GetSet, ExecuteOpcode, RestartNode", branch `feature/dronecan-configurator-tab`, repo inav-configurator) — 3 HIGH, 2 MEDIUM. Investigate all five, confirm whether they're real bugs, and prepare recommended fixes + regression coverage.

## Background

**Finding 1 — GPS protocol enum shift, HIGH (correctness / backward compatibility)**
File: `js/fc.js`, lines 672-679 (related: `tabs/gps.js` 182-200, `js/wizard_ui_bindings.js` 37-40).
CRSF was inserted before FAKE in the GPS protocol array, shifting the numeric indices used as `<option value="i">` values. Existing saved configs using the old enum values (e.g. FAKE=2) will display/save as the wrong protocol when loaded. DroneCAN detection is also hard-coded to `gps_type === 4` instead of derived from an explicit mapping. Suggested direction: append new options only (never insert), build an explicit {id, label} mapping keyed to firmware enum values, gate new protocols by `FC.CONFIG.flightControllerVersion`, and stop hard-coding the DroneCAN index.

**Finding 2 — Busy state truncates parameter fetch, HIGH (reliability)**
File: `tabs/dronecan.js`, lines 373-377 (related: 80-106, 150-195).
Firmware exposes a single async request slot (busy is a normal/expected state). The UI runs overlapping async operations against it — background name fetching plus parameter enumeration — and `showParams()` treats a busy error as terminal, truncating the parameter list and blocking per-node actions instead of retrying. Suggested direction: add a tab-local request queue/mutex so only one `dronecanAsyncPoll()` runs at a time, or pause background name fetching while the node detail/params view is active; treat BUSY/STALE as retryable with backoff rather than a hard stop.

**Finding 3 — Node ID not validated before save, HIGH (correctness)**
File: `tabs/dronecan.js`, lines 451-456 (related: `tabs/dronecan.html` 19-22, `js/msp/MSPHelper.js` 3652-3658).
`saveConfig()` parses nodeId but doesn't enforce bounds or check for NaN; `mspHelper.setSetting()` swallows encoding errors but still calls its callback. An invalid node ID can trigger an EEPROM save + reboot with only partial config applied — the HTML input has min/max but a user can clear the field or otherwise bypass it. Suggested direction: validate nodeId is an integer in [1, 127] and bitrate is one of the supported options before saving, show an error and abort (no reboot) if invalid, and await both setSetting calls, failing the overall save if either fails.

**Finding 4 — Parameter integer overflow silently wraps, MEDIUM (correctness)**
File: `tabs/dronecan.js`, lines 39-57 (related: 269-294).
`encodeParamValueBytes()` truncates any BigInt to 8 bytes without enforcing int64 range, so out-of-range values silently wrap. Float encoding also allows non-finite values (e.g. Infinity) through when no min/max is set — `validateNumericParam()` only checks NaN and optional min/max. Suggested direction: reject INT values outside [-2^63, 2^63-1] before encoding, require `Number.isFinite(value)` for FLOAT, and surface a clear UI error when rejecting.

**Finding 5 — Stale async state on short responses, MEDIUM (reliability)**
File: `js/msp/MSPHelper.js`, lines 1591-1598 (related: `tabs/dronecan.js` 83-90).
The MSP2_INAV_DRONECAN_ASYNC_REQUEST parser only updates `FC.DRONECAN_ASYNC_REQUEST` when byteLength >= 2, so a short/status-only or zero-length response leaves the old status/seq in place. `dronecanAsyncPoll()` reads status/seq immediately to decide whether to poll and what seq to expect, so stale values cause incorrect behavior. Suggested direction: always reset FC.DRONECAN_ASYNC_REQUEST at the start of the parse case; if byteLength >= 1, at least store status; only store seq when present; update dronecanAsyncPoll() to treat a missing seq as error/not-ready.

## What to Do

1. Reproduce/confirm all five findings (bench test or code trace as appropriate).
2. Write up your assessment of root cause and the recommended fix for each.
3. Propose or write regression test coverage for each (per project convention — always add tests for new functionality/bugfixes).
4. Per established project convention for DroneCAN branches: prepare the recommended fixes and test coverage, but the user (daijoubu) will implement the actual production code change — don't write the fix into the configurator source yourself. Your report should be specific enough (file/line/exact change) that the user can apply it directly.
5. Send completion report to manager summarizing all five findings' confirmed root cause and recommended fix, ranked by the HIGH/MEDIUM severity above.

## Success Criteria

- [ ] All five findings confirmed or refuted with evidence
- [ ] Recommended fix written up with specific file/line targets for each
- [ ] Regression test coverage proposed or written for each
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/feature-dronecan-configurator-tab/`

## Note

Companion firmware PR #11683 (`feature-dronecan-param-getset`) also has two HIGH-severity Qodo findings already assigned to you separately (task sent 2026-08-21) — these two PRs are meant to be reviewed/merged together, so keep both in mind together. SonarQube passed clean on this PR (0 new issues, quality gate green) — these five are Qodo findings only.

---
**Manager**
