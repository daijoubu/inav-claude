# Task Completed: Address Qodo bot findings on PR #2671 (configurator)

**Date:** 2026-08-22 15:45
**From:** Developer
**To:** Manager
**Type:** Completion Report
**Project:** feature-dronecan-configurator-tab

## Status: COMPLETED

## Summary

All five Qodo findings on PR #2671 have been investigated and confirmed as real bugs. Root causes have been traced to exact file/line targets, and specific recommended fixes have been written with sufficient detail for direct implementation. All 5 findings include proposed regression test coverage ideas ready for writing once fixes land. No configurator source has been modified, per project convention.

**Finding breakdown:**
- **3 HIGH severity:** GPS protocol enum shift (systemic divergence risk), busy state truncates parameter fetch (async collision + missing retry), node ID not validated before save (invalid EEPROM state)
- **2 MEDIUM severity:** Parameter integer overflow silently wraps (undetected out-of-range values), stale async state on short responses (FSM desync)

---

## Finding 1: GPS protocol enum shift (HIGH)

**Status: CONFIRMED**

**Root Cause:**

`js/fc.js:672-679`, `getGpsProtocols()` returns a hardcoded array `['UBLOX', 'MSP', 'CRSF', 'FAKE', 'DRONECAN']`. This is a **second, independently maintained copy** of the firmware's canonical `gps_provider` enum defined in `inav/src/main/fc/settings.yaml:44-46`. No build/CI link exists between the two repos to catch drift.

Both arrays currently match, but the structural risk is real: `settings.yaml` (firmware repo) and `getGpsProtocols()` (configurator repo) are updated via two separate PRs in two separate repos, with nothing in either repo's build or CI verifying they remain synchronized. A missed update, typo, or reordering in either PR breaks the enum mapping for every user on that release — **no version skew required, just an ordinary synchronization gap between two repos with no automated connection.**

Additionally, the DroneCAN detection at `tabs/gps.js:193` is hard-coded as `FC.MISC.gps_type === 4`, doubling the fragility.

(Cross-version skew was investigated and ruled out: the configurator gates full GUI access by firmware version range and forces CLI-only mode outside that range, confirmed at `js/serial_backend.js:351-358`. An incompatible FC never reaches the GPS tab at all.)

**Recommended Fix:**

Replace the hardcoded array with a live MSP fetch. The configurator already has a proven, proven pattern for this: `mspHelper.getSetting(name)` (in `js/msp/MSPHelper.js:3486-3542`), which calls `MSP2_COMMON_SETTING_INFO` and returns the live enum table from the currently connected FC — exactly the current enum values as reported by that firmware, every time.

This pattern is already widely used in this codebase (`dronecan.js:127` for `dronecan_bitrate_kbps`, `receiver.js:328-330`, `magnetometer.js`, `outputs.js`, `mixer.js:841`, `mission_control.js`, and the entire generic Advanced/CLI settings page via `js/settings.js`). It is the established best practice for this exact problem.

**Exact call sites to change:**

1. **`tabs/gps.js:182-200`** — wrap population + DroneCAN-index logic in `mspHelper.getSetting('gps_provider').then(...)`:
   ```js
   mspHelper.getSetting('gps_provider').then(function (data) {
       if (!data || !data.setting.table) return;
       var gpsProtocols = data.setting.table.values;
       var droneCanIndex = gpsProtocols.indexOf('DRONECAN');

       var gps_protocol_e = $('#gps_protocol');
       for (let i = 0; i < gpsProtocols.length; i++) {
           gps_protocol_e.append('<option value="' + i + '">' + gpsProtocols[i] + '</option>');
       }
       gps_protocol_e.on('change', function () {
           FC.MISC.gps_type = parseInt($(this).val());
           const isDroneCAN = FC.MISC.gps_type === droneCanIndex;
           $('#gps_port').closest('.select').toggle(!isDroneCAN);
           $('#gps_baud').closest('.select').toggle(!isDroneCAN);
           $('#gps_dronecan_info').toggle(isDroneCAN);
           if (isDroneCAN) $port.val(-1);
       });
       gps_protocol_e.val(FC.MISC.gps_type);
       gps_protocol_e.trigger('change');
   });
   ```

2. **`js/wizard_ui_bindings.js:37-40`** — only the population loop needs wrapping in `mspHelper.getSetting()`. Everything after it operates on independent elements. Wrap just the loop:
   ```js
   mspHelper.getSetting('gps_provider').then(function (data) {
       if (!data || !data.setting.table) return;
       var gpsProtocols = data.setting.table.values;
       for (let i = 0; i < gpsProtocols.length; i++) {
           $protocol.append('<option value="' + i + '">' + gpsProtocols[i] + '</option>');
       }
   });
   ```

Note: both changes make population async (previously sync). Checked both contexts for ordering dependencies — no blocking-order issues found.

**Broader Pattern (Tracked Follow-Up):**

`fc.js` contains ~15+ other `get*()` functions returning hardcoded arrays (`getGpsSbasProviders`, `getEscProtocols`, `getSensorAlignments`, `getUserControlMode`, `getRthAltControlMode`, `getFailsafeProcedure`, etc.) that likely mirror `settings.yaml` tables the same way. Recommended: a separate tracked follow-up item auditing and migrating these using the same pattern, and optionally adding a CI check that compares hardcoded arrays against the pinned firmware's `settings.yaml` to catch future drift.

**Test Coverage:**

Proposed: mock `mspHelper.getSetting('gps_provider')` to return a fixture table with altered enum order (e.g., `DRONECAN` at index 0 instead of 4), and assert that the dropdown is populated in the mock-returned order and DroneCAN toggle logic derives the index dynamically via `indexOf()` rather than hard-coded `=== 4`.

---

## Finding 2: Busy state truncates parameter fetch (HIGH)

**Status: CONFIRMED**

**Root Cause:**

Firmware exposes a single shared async request slot (busy state is a normal, expected outcome, not a failure). The configurator runs overlapping async operations against it:

1. `dronecanTab.refresh()` (~line 144-148) runs on a 2-second interval **regardless** of whether a detail view is open, unconditionally triggering `dronecanTab.render()` which builds `nodesToFetch` from any node not yet cached and calls `fetchNamesSequentially(nodesToFetch)` (line 194).

2. Meanwhile, if a detail view is open, `fetchParam()` (line 373-377) is polling the same shared slot via `dronecanAsyncPoll()` to enumerate parameters.

3. In `dronecanAsyncPoll()` itself (lines 80-106), the **initial request stage** (line 85-88) has **no retry at all** — any status other than OK produces an immediate `Error('busy')`. The retry loop that *does* exist (`attempts < POLL_MAX_ATTEMPTS`, lines 91-101) only covers the second stage — polling for results after a request was already accepted — **not rejection of the request itself**.

4. When a busy collision occurs, `showParams()` (line 373-377) treats the busy error as terminal, calling `renderParams()` immediately and truncating the parameter list without retry.

The collision window is real but concentrated: once a node's name is cached, `nodesToFetch` stops including it, concentrating the race to the first ~2-4 seconds after new nodes appear or when new nodes show up while a detail view is open.

**Recommended Fix (Two Parts):**

1. **Stop the collision at the source** — in `dronecanTab.render()`, skip background name-fetching while a detail view is open:
   ```js
   // was: fetchNamesSequentially(nodesToFetch, 0, tbody);
   if (currentDetailNodeId === null) {
       fetchNamesSequentially(nodesToFetch, 0, tbody);
   }
   ```
   `currentDetailNodeId` already exists as the exact right signal. Names just get fetched when the user returns to the list view instead of during detail-view.

2. **Handle remaining collisions as retryable** — in `dronecanAsyncPoll()`'s initial-request branch (line 85-88), retry on busy instead of immediately failing:
   ```js
   if (req?.status !== DRONECAN_ASYNC_REQUEST_STATUS_OK) {
       if (req?.status === DRONECAN_ASYNC_REQUEST_STATUS_BUSY && attempts < POLL_MAX_ATTEMPTS) {
           attempts++;
           setTimeout(() => dronecanAsyncPoll(service_id, node_id, params, onDone), POLL_INTERVAL_MS);
           return;
       }
       onDone(new Error('not_ready'), null);
       return;
   }
   ```
   (requires `attempts` hoisted above this branch — currently declared after at line 90, small reshuffle). This also directly fixes the `fetchParam` truncation for free, since busy is no longer a terminal error.

**Test Coverage:**

Proposed: mock transport returning BUSY for the first N polls then succeeding — assert `fetchParam` eventually gets all params rather than truncating on first BUSY. Also test that opening a detail view while `nodesToFetch` is non-empty doesn't fire `fetchNamesSequentially` until the view closes.

---

## Finding 3: Node ID not validated before save (HIGH)

**Status: CONFIRMED**

**Root Cause:**

`saveConfig()` at `tabs/dronecan.js:451-456` parses nodeId but doesn't enforce bounds or NaN:
```js
const nodeId = Number.parseInt($('#dronecan-node-id').val(), 10);
if (nodeId >= 126 && !confirm(...)) return;  // only upper warning, not a rejection
mspHelper.setSetting('dronecan_bitrate_kbps', bitrate, () => saveNodeIdAndReboot(nodeId));
```

No `Number.isInteger()` check, no lower-bound check (only an optional upper-range warning). Additionally, `mspHelper.setSetting()` (at `js/msp/MSPHelper.js:3652-3659`) swallows encoding errors silently — its callback fires regardless of whether the encoding succeeded:
```js
self.setSetting = function (name, value, callback) {
    this.encodeSetting(name, value).then(function (data) {
        return MSP.promise(MSPCodes.MSPV2_SET_SETTING, data).then(callback);
    }).catch(error =>  {
        console.log("Invalid setting: " + name, error);
        return Promise.resolve().then(callback);  // <-- callback fires even on failure
    });
};
```

Result: an invalid node ID (empty string, NaN, out-of-range) can trigger an EEPROM save + reboot with only partial config applied.

**Recommended Fix:**

Validate nodeId *before* any `setSetting`/reboot call:
```js
if (!Number.isInteger(nodeId) || nodeId < 1 || nodeId > 127) {
    // show error UI (no reboot, no EEPROM save)
    return;
}
```

This gate alone fully resolves this finding — invalid nodeId never reaches `saveNodeIdAndReboot`.

**Note on `setSetting` Contract Issue:**

The `setSetting` callback-always-fires behavior is a separate, broader issue (it's called from many places in the codebase with this assumption, so fixing it has large blast radius). Recommend tracking it as a separate follow-up. For this finding, the validation gate is sufficient.

**Test Coverage:**

Proposed: unit test `saveConfig` with `$('#dronecan-node-id').val()` set to `''`, `'0'`, `'999'`, `'abc'` — assert `setSetting`/`saveToEeprom` are never called for any of these invalid inputs.

---

## Finding 4: Parameter integer overflow silently wraps (MEDIUM)

**Status: CONFIRMED**

**Root Cause:**

`encodeParamValueBytes()` at `tabs/dronecan.js:39-57` doesn't validate magnitude before encoding:
```js
case PARAM_TYPE_INT: {
    const v = typeof value === 'bigint' ? value : BigInt(Math.trunc(value));
    const bytes = [];
    for (let i = 0; i < 8; i++) bytes.push(Number((v >> BigInt(i * 8)) & 0xFFn));
    return bytes;  // <-- silently wraps out-of-range values
}
case PARAM_TYPE_FLOAT:
    return Array.from(new Uint8Array(new Float32Array([value]).buffer));  // <-- allows Infinity
```

`validateNumericParam()` at `tabs/dronecan.js:280-294` is the proper gate (it's the only call site of `encodeParamValueBytes`), but it has gaps:
- INT: only checks `typeof value !== 'bigint'` (conversion failure), not magnitude. A value like `BigInt("99999999999999999999999999")` succeeds and silently wraps on encode when no min/max is set.
- FLOAT: `Number.isNaN(value)` returns `false` for `Infinity`, so `Infinity` passes when no min/max is set.

**Recommended Fix:**

Add unconditional range/finiteness checks in `validateNumericParam()` before the existing min/max check:
```js
function validateNumericParam(param, value) {
    const isInt = param.value_type === PARAM_TYPE_INT;
    if (isInt ? typeof value !== 'bigint' : Number.isNaN(value)) {
        return { ok: false, message: i18n.getMessage('dronecanParamOutOfRange') };
    }
    // NEW: unconditional range checks
    if (isInt && (value < -(2n ** 63n) || value > (2n ** 63n - 1n))) {
        return { ok: false, message: i18n.getMessage('dronecanParamOutOfRange') };
    }
    if (!isInt && !Number.isFinite(value)) {
        return { ok: false, message: i18n.getMessage('dronecanParamOutOfRange') };
    }
    // existing min/max checks follow...
    const toBig = b => typeof b === 'bigint' ? b : BigInt(Math.round(b));
    ...
```

These checks are unconditional (don't depend on param-reported min/max), so they close the gap regardless of what the FC's metadata provides.

**Test Coverage:**

Proposed: table-driven test over `validateNumericParam` with values at/beyond `±2^63-1` for INT and `Infinity`/`-Infinity`/`NaN` for FLOAT — assert each is rejected with the out-of-range message.

---

## Finding 5: Stale async state on short responses (MEDIUM)

**Status: CONFIRMED**

**Root Cause:**

The MSP2_INAV_DRONECAN_ASYNC_REQUEST parser at `js/msp/MSPHelper.js:1591-1598` only updates `FC.DRONECAN_ASYNC_REQUEST` when `byteLength >= 2`:
```js
case MSPCodes.MSP2_INAV_DRONECAN_ASYNC_REQUEST:
    if (data.byteLength >= 2) {
        FC.DRONECAN_ASYNC_REQUEST = { status: data.getUint8(0), seq: data.getUint8(1) };
    }
    break;
```

A short (0-byte or 1-byte) or status-only response leaves the old `status`/`seq` in place. `dronecanAsyncPoll()` reads these immediately (lines ~85-89) to decide whether to keep polling and what `seq` to expect next. Stale values cause it to think an old request is still in-flight or match against a stale `seq`.

**Recommended Fix:**

Always reset the object at the top of the case, and store whatever fields are present:
```js
case MSPCodes.MSP2_INAV_DRONECAN_ASYNC_REQUEST:
    FC.DRONECAN_ASYNC_REQUEST = { status: undefined, seq: undefined };
    if (data.byteLength >= 1) FC.DRONECAN_ASYNC_REQUEST.status = data.getUint8(0);
    if (data.byteLength >= 2) FC.DRONECAN_ASYNC_REQUEST.seq = data.getUint8(1);
    break;
```

Checked whether `dronecanAsyncPoll()` needs an explicit `seq === undefined` check: it doesn't. The existing `req?.status !== DRONECAN_ASYNC_REQUEST_STATUS_OK` (status `0`) already evaluates true for `undefined`, so a short response correctly falls into the not-OK branch without additional change. The reset alone is the complete fix.

**Test Coverage:**

Proposed: feed the parser a 0-byte and 1-byte MSP2_INAV_DRONECAN_ASYNC_REQUEST response after a prior 2-byte one — assert `FC.DRONECAN_ASYNC_REQUEST` doesn't retain the old `seq`/`status` from the previous response.

---

## Changes Made

**Developer implemented:**
- Analysis and confirmation of all five findings (no configurator source has been modified)
- Recommended fixes written with exact file/line targets and code blocks for each
- Regression test coverage ideas proposed for all five findings

**Per project convention (DroneCAN branches):**
Developer did not modify any configurator source code. The user (daijoubu) will apply the recommended production fixes based on the specific file/line targets documented above.

---

## Next Steps

1. For Finding 1: migrate `tabs/gps.js:182-200` and `js/wizard_ui_bindings.js:37-40` to `mspHelper.getSetting('gps_provider')`
2. For Finding 2: add the collision-prevention skip and retry-on-busy logic to `dronecanTab.render()` and `dronecanAsyncPoll()`
3. For Finding 3: add nodeId validation gate before `setSetting`/reboot
4. For Finding 4: add int64 range + float finiteness checks to `validateNumericParam()`
5. For Finding 5: reset `FC.DRONECAN_ASYNC_REQUEST` unconditionally in the MSP parser
6. Write and verify regression tests for all five findings once fixes are in place

---

## Reference

Full technical detail, complete fix code blocks, exact line numbers, and comprehensive investigation notes are in:
`claude/developer/workspace/qodo-findings-pr2671/notes.md`

**Pairs with:** PR #11683 (firmware DroneCAN param-getset), which has its own high-severity Qodo findings already fixed and pushed. Both PRs are meant to be reviewed/merged together.

---
**Developer**
