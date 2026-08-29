# Task Completed: Address Qodo bot findings on PR #11683

**Date:** 2026-08-22 10:30
**From:** Developer
**To:** Manager
**Type:** Completion Report
**Project:** feature-dronecan-param-getset

## Status: COMPLETED

## Summary

Both HIGH-severity Qodo findings on PR #11683 have been investigated and confirmed. Root causes are real bugs with clear recommended fixes. Finding 1 has new regression test coverage written and confirmed working. Finding 2 has a detailed fix specification ready for implementation; unit test infrastructure does not yet exist for that module, with recommendation for incremental improvement.

## Finding 1: Timeout Checked Before RX Drain (Reliability)

**Status: CONFIRMED**

**Root Cause:**
`dronecanUpdate()` in `src/main/drivers/dronecan/dronecan.c` (STATE_DRONECAN_NORMAL case, ~line 147) calls `dronecanAsyncCheckTimeout()` *before* draining the CAN RX FIFO. When a valid response is already queued in the FIFO and the timeout boundary is crossed in the same tick, the timeout check flips the async slot to `DRONECAN_ASYNC_ERROR` before the RX-drain loop runs. `dronecanAsyncHandleServiceResponse()` only processes slots in PENDING state, so the response is discarded as a false timeout even though it arrived within the timeout window.

**Recommended Fix:**
Move `dronecanAsyncCheckTimeout()` to *after* the RX-drain loop and its trailing `processCanardTxQueueSafe()` call in the STATE_DRONECAN_NORMAL case block.

**Test Coverage:**
New regression test written and confirmed: `TEST_F(DroneCANDispatchTest, AsyncSlot_ResponseArrivingAtTimeoutBoundary_IsNotDropped)` in `src/test/unit/dronecan_application_unittest.cc`. Reproduces the exact scenario by calling `dronecanAsyncCheckTimeout()` first, then `onTransferReceived()` with a response arriving exactly at `mock_time_ms == DRONECAN_ASYNC_TIMEOUT_MS`.

**Test Status (via test-engineer 2026-08-22):**
- Compiles cleanly
- Fails exactly as expected: slot state ends up `DRONECAN_ASYNC_ERROR (3)` instead of expected `DRONECAN_ASYNC_READY (2)`
- All 29 other tests in the dronecan_application_unittest binary still pass — no regressions
- Committed locally on branch `feature/dronecan-param-getset` (commit `723bb0630`)

**Important Note:**
This test is currently **NOT pushed to origin**. The branch has an open PR (#11683). Should this regression test be pushed to the PR now, or held for the user (daijoubu) to push alongside the production fix?

## Finding 2: Truncated MSP Writes Accepted (Correctness)

**Status: CONFIRMED**

**Root Cause:**
`MSP2_INAV_DRONECAN_ASYNC_REQUEST` handler in `src/main/fc/fc_msp.c` (DRONECAN_SERVICE_PARAM_GETSET branch, lines 4642-4694) reads value type and value bytes with individual guard conditions (`if (sbufBytesRemaining(src) >= N)`), but there is **no corresponding rejection** when a guard fails. If a byte-read fails the guard, it is silently skipped (leaving the memset-zeroed default in `req`), and execution falls through to dispatch the request anyway. This means a truncated write payload produces a valid UAVCAN request with zeroed/garbage values or empty/wrong parameter names instead of being rejected.

**Recommended Fix (exact replacement for fc_msp.c lines 4650-4693):**

```c
req.is_write = sbufReadU8(src);
if (req.is_write) {
    if (sbufBytesRemaining(src) < 1) { // value_type
        *ret = MSP_RESULT_ERROR;
        break;
    }
    req.value_type = sbufReadU8(src);
    switch (req.value_type) {
        case DRONECAN_PARAM_TYPE_INT:
            if (sbufBytesRemaining(src) < 8) {
                *ret = MSP_RESULT_ERROR;
                break;
            } else {
                uint64_t tmp;
                sbufReadData(src, &tmp, sizeof(tmp));
                sbufAdvance(src, sizeof(tmp));
                req.value_int = (int64_t)tmp;
            }
            break;
        case DRONECAN_PARAM_TYPE_FLOAT:
            if (sbufBytesRemaining(src) < 4) {
                *ret = MSP_RESULT_ERROR;
                break;
            } else {
                uint32_t raw = sbufReadU32(src);
                memcpy(&req.value_float, &raw, 4);
            }
            break;
        case DRONECAN_PARAM_TYPE_BOOL:
            if (sbufBytesRemaining(src) < 1) {
                *ret = MSP_RESULT_ERROR;
                break;
            }
            req.value_bool = sbufReadU8(src);
            break;
        case DRONECAN_PARAM_TYPE_STRING:
            if (sbufBytesRemaining(src) < 1) {
                *ret = MSP_RESULT_ERROR;
                break;
            }
            req.value_str_len = sbufReadU8(src);
            if (req.value_str_len > sizeof(req.value_str))
                req.value_str_len = sizeof(req.value_str);
            if (sbufBytesRemaining(src) < req.value_str_len) {
                *ret = MSP_RESULT_ERROR;
                break;
            }
            sbufReadData(src, req.value_str, req.value_str_len);
            sbufAdvance(src, req.value_str_len);
            break;
        default: // includes DRONECAN_PARAM_TYPE_EMPTY on a write, which is nonsensical
            *ret = MSP_RESULT_ERROR;
            break;
    }
    if (*ret == MSP_RESULT_ERROR) {
        break; // exits the outer MSP2_INAV_DRONECAN_ASYNC_REQUEST case block —
               // NOT the switch(req.value_type) above, which already exited
               // on its own `break;`. This is the same pattern already used
               // at line 4625-4628 in this function.
    }
}
if (sbufBytesRemaining(src) >= 1) {
    req.req_name_len = sbufReadU8(src);
    if (req.req_name_len > sizeof(req.req_name))
        req.req_name_len = sizeof(req.req_name);
    if (sbufBytesRemaining(src) < req.req_name_len) {
        *ret = MSP_RESULT_ERROR;
        break;
    }
    sbufReadData(src, req.req_name, req.req_name_len);
    sbufAdvance(src, req.req_name_len);
}
accepted = dronecanAsyncRequest(service_id, nodeID, &req);
```

**Critical Nesting Note for Implementation:**
The `break;` statements inside the `switch (req.value_type)` cases only exit that inner switch, **not** the outer `case MSP2_INAV_DRONECAN_ASYNC_REQUEST:` block. The explicit `if (*ret == MSP_RESULT_ERROR) break;` immediately after the switch is required to propagate the error and actually reject the MSP command. The same pattern is already used elsewhere in this function (lines 4625-4628), confirming this is the established practice.

**Test Coverage Status:**
No compiling unit test yet. Root cause: `fc_msp.c` has no existing unit test infrastructure in this repo. The sole MSP-related test file, `serial_msp_unittest.cc.txt`, is disabled via `.txt` extension and does not cover this handler. Testing this inline switch in isolation would require either a full MSP dispatch mock (out of scope) or extracting the payload-parsing logic into a small pure function first.

**Recommended Unit Test Approach:**
Extract the payload-parsing into a pure function (e.g., `static mspResult_e dronecanParseParamGetSetWrite(sbuf_t *src, dronecanParamRequest_t *req)`) as part of the fix itself. This would both correct the bug and make it directly unit-testable.

**Proposed Test Vectors for Extracted Function:**
- `is_write=1, value_type=INT, 0-7 trailing bytes` → `MSP_RESULT_ERROR`
- `is_write=1, value_type=INT, exactly 8 trailing bytes` → `MSP_RESULT_ACK`, value_int decoded correctly
- `is_write=1, value_type=FLOAT, 0-3 trailing bytes` → `MSP_RESULT_ERROR`
- `is_write=1, value_type=BOOL, 0 trailing bytes` → `MSP_RESULT_ERROR`
- `is_write=1, value_type=STRING, length byte present but declared length > remaining bytes` → `MSP_RESULT_ERROR`
- `is_write=1, value_type=EMPTY` → `MSP_RESULT_ERROR` (per original suggestion to reject write with EMPTY type)
- `is_write=1, valid value, but req_name_len byte present with declared length > remaining bytes` → `MSP_RESULT_ERROR`
- `is_write=0` (read request) → unaffected, still ACKs regardless of trailing bytes (matches intended read-request behavior)

## Changes Made

**Developer implemented:**
- Analysis and confirmation of both findings (no production code changes)
- New regression test for Finding 1: `src/test/unit/dronecan_application_unittest.cc`, commit `723bb0630`

**Per project convention (DroneCAN branches):**
Developer did not modify `dronecan.c` or `fc_msp.c`. The user (daijoubu) will apply the recommended production fixes based on the specific file/line targets and code blocks documented above.

## Next Steps

1. For Finding 1 production fix: reorder timeout check in `dronecanUpdate()`
2. For Finding 1 test: decide whether to push the regression test to PR #11683 now or hold for user to push with production fix
3. For Finding 2 production fix: apply the specified payload validation block; consider extracting to pure function for future unit testability
4. For Finding 2 test coverage: either add unit tests for the extracted function, or document test vectors for manual/integration testing

## Reference

Full technical detail, complete fix code blocks, exact line numbers, and comprehensive investigation notes are in:
`claude/developer/workspace/address-qodo-findings-pr11683/notes.md`

---
**Developer**
