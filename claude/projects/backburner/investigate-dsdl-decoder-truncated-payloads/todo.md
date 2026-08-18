# Todo List: DSDL-Generated Decoders Silently Accept Truncated/Malformed DroneCAN Payloads

## Phase 1: Determine Intent

- [ ] Check whether a length/validity check happens upstream of decode
      (`canardHandleRxFrame()` / `on_reception()` in
      `src/main/drivers/dronecan/libcanard/canard.c`)
- [ ] Check DSDL/libcanard upstream project history and docs for any
      stated design intent on this
- [ ] Decide: known/accepted limitation, or genuine gap — document reasoning

## Phase 2: Fix (only if genuine gap)

- [ ] Identify where in the generator/post-processing pipeline
      `lib/main/Dronecan/dsdlc_generated/` is produced
- [ ] Design return-value propagation fix (generator-level or
      post-processing, not hand-patched generated files)
- [ ] Verify fix covers `_uavcan_Timestamp_decode()` and all scalar-field
      call sites, not just GNSSFix2
- [ ] Re-generate/re-apply and confirm generated files build clean

## Phase 3: Tests

- [ ] Fix `GNSSFix2_ZeroPayload` in `dronecan_messages_unittest.cc` to
      assert the real (correct) contract
- [ ] Fix `GNSSFix2_TruncatedBuffer` in `dronecan_messages_unittest.cc`
      to assert the real (correct) contract
- [ ] Spot-check NodeStatus/BatteryInfo decode tests reflect the same fix

## Completion

- [ ] All tests passing
- [ ] PR opened (if code change needed) against correct base branch
- [ ] Completion report sent to manager
