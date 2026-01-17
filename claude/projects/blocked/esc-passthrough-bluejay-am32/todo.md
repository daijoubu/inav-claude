# Todo List: ESC Passthrough Bluejay/AM32 Compatibility

## Phase 1: Timeout Handling (Priority: Critical)

- [ ] Add timeout infrastructure to `serial_4way.c`
  - [ ] Add `#define USE_TIMEOUT_4WAYIF` (or make it always-on)
  - [ ] Add timeout constants:
    ```c
    #define CMD_TIMEOUT_US  50000
    #define ARG_TIMEOUT_US  25000
    #define DAT_TIMEOUT_US  10000
    #define CRC_TIMEOUT_US  10000
    ```
  - [ ] Modify `ReadByte()` signature to accept timeout: `static bool ReadByte(uint8_t *data, timeDelta_t timeoutUs)`
  - [ ] Implement timeout logic using `micros()` and `cmpTimeUs()`
  - [ ] Return `true` on timeout, `false` on success
  - [ ] Update `ReadByteCrc()` to use new `ReadByte()` signature
- [ ] Update `esc4wayProcess()` main loop
  - [ ] Add `bool timedOut` variable tracking
  - [ ] Use timeouts for CMD, ARG, DAT, CRC reads
  - [ ] Handle timeout errors appropriately

## Phase 2: Device Detection Updates

- [ ] Update `SILABS_DEVICE_MATCH` macro in `serial_4way.c`
  - [ ] Change from explicit ID list to range-based:
    ```c
    #define SILABS_DEVICE_MATCH ((pDeviceInfo->words[0] > 0xE800) && (pDeviceInfo->words[0] < 0xF900))
    ```

## Phase 3: ESC Reboot Logic

- [ ] Add ESC reboot handling to `cmd_DeviceReset` case
  - [ ] Add `rebootEsc` flag based on `ioMem.D_FLASH_ADDR_L == 1`
  - [ ] After `BL_SendCMDRunRestartBootloader()`, if rebootEsc:
    - [ ] Set ESC pin to output
    - [ ] Pull low for ~300ms
    - [ ] Set high
    - [ ] Set back to input

## Phase 4: Motor IO Access (Investigate First)

- [ ] Test if current PWM-based motor IO works with DSHOT protocols
- [ ] If issues found with DSHOT:
  - [ ] Implement `motorIsMotorEnabled()` function
  - [ ] Implement `motorGetIo()` function
  - [ ] Update `esc4wayInit()` to use new functions

## Phase 5: Version Updates

- [ ] Update `SERIAL_4WAY_PROTOCOL_VER` from 107 to 108
- [ ] Update `SERIAL_4WAY_VER_SUB_2` from 05 to 06

## Phase 6: Build & Test

- [ ] Build SITL with changes
- [ ] Build for hardware target (e.g., MATEKF405)
- [ ] Test with BLHeli32 ESC (regression test)
- [ ] Test with Bluejay ESC
- [ ] Test with AM32 ESC
- [ ] Test with BLHeliSuite32
- [ ] Test with Bluejay Configurator
- [ ] Test with AM32 Configurator

## Completion

- [ ] All tests passing
- [ ] No regressions with BLHeli32
- [ ] Bluejay and AM32 passthrough working
- [ ] Send completion report to manager
