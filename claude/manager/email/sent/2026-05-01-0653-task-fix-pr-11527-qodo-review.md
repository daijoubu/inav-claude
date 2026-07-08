# Task Assignment: Fix PR #11527 Qodo Review Issues

**Date:** 2026-05-01 06:53
**From:** Manager
**To:** Developer
**Project:** feature-dronecan-msp-messages
**Priority:** HIGH
**Estimated Effort:** 1-2 hours

## Task

PR #11527 ("DroneCAN: Add node table, CLI status, and MSP2 node query commands") received Qodo bot feedback identifying two action-required issues. Before fixing them, run the local code review tool to check whether these would have been caught locally — that result is useful feedback for our workflow.

## Step 1: Run Local Code Review First

Run `/inav-code-review` (or the local code review agent) against the changes in PR #11527 and note whether it catches either of the two issues below. Report the result in your completion email.

## Step 2: Fix the Two Issues

### Issue 1 — Payload Buffer Overflow in MSP2_INAV_DRONECAN_NODES

**Location:** `src/main/fc/fc_msp.c` ~line 1774–1788

**Problem:** The `MSP2_INAV_DRONECAN_NODES` reply serializes all nodes without checking remaining buffer space. Worst-case payload is `1 + nodeCount * 30 = 961 bytes`, which exceeds the default MSP out buffer (`MSP_PORT_OUTBUF_SIZE` = 512 bytes). `sbufWriteU8/U16/U32/sbufWriteData` do not bounds-check.

**Fix:** Cap `nodeCount` before serializing so the response never exceeds the buffer. Check `sbufBytesRemaining(dst)` or cap to `(bufSize - 1) / 30` nodes. Document the cap.

### Issue 2 — Wrong ret Value in MSP2_INAV_DRONECAN_NODE_INFO

**Location:** `src/main/fc/fc_msp.c` ~lines 4273–4310 and 4826–4853

**Problem:** `mspFCProcessInOutCommand()` returns `bool` (handled/unhandled) and communicates ACK vs ERROR via the `mspResult_e *ret` out-parameter. The new `MSP2_INAV_DRONECAN_NODE_INFO` case incorrectly uses `return MSP_RESULT_ERROR` / `return MSP_RESULT_ACK` directly and never sets `*ret`. This means "node not found" is silently reported as ACK (success) to clients.

**Fix:**
- Replace `return MSP_RESULT_ERROR;` with `*ret = MSP_RESULT_ERROR; break;`
- Replace `return MSP_RESULT_ACK;` with `break;` (ACK is the default)
- Ensure the "node not found" path sets `*ret = MSP_RESULT_ERROR`
- The function's own return value should be `true` (command was handled)

## Success Criteria

- [ ] Local code review run; result noted (caught / not caught)
- [ ] `MSP2_INAV_DRONECAN_NODES` caps serialized nodes to fit within MSP out buffer
- [ ] `MSP2_INAV_DRONECAN_NODE_INFO` sets `*ret` correctly; error cases return MSP_RESULT_ERROR
- [ ] Builds cleanly for MATEKF765SE
- [ ] Fixes pushed to the existing PR branch (`feature/msp-dronecan-support-v2` or whichever is current)
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/feature-dronecan-msp-messages/`

---
**Manager**
