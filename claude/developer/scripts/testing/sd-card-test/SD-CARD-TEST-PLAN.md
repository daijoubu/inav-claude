# SD Card Test Plan for MATEKF765SE

**Purpose:** Validate SD card reliability before and after STM32F7 HAL update (V1.2.2 → V1.3.3)
**Target Hardware:** MATEKF765SE (STM32F765, SDIO interface, 4-bit mode, DMA)
**Created:** 2026-02-21

---

## Overview

This test plan provides repeatable procedures to stress-test SD card operations on the MATEKF765SE flight controller. The goal is to:
1. Establish a baseline with current HAL (V1.2.2)
2. Identify any existing reliability issues
3. Verify improvements after HAL update (V1.3.3)

---

## Hardware Configuration

### MATEKF765SE SD Card Interface
- **Interface:** SDIO (not SPI)
- **Mode:** 4-bit (SDCARD_SDIO_4BIT)
- **DMA:** DMA2 Stream 3 Channel 4
- **Device:** SDIODEV_1

### Test Equipment (Available)
- ✅ MATEKF765SE flight controller
- ✅ ST-Link debugger
- ✅ GPS module (connected and functional)
- ✅ SD cards
- ✅ USB cable for MSP communication

### Automation Capability

With this hardware configuration, the following tests are **fully automatable**:

| Test | Automation | Method |
|------|------------|--------|
| 1-4 | ✅ Full | MSP protocol |
| 6 | ✅ Full | MSP protocol |
| 8 | ✅ Full | MSP + real GPS fix detection |
| 10 | ✅ Full | MSP + real GPS DMA activity |
| 11 | ✅ Full | ST-Link + OpenOCD breakpoints |

Run automated tests:
```bash
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2
```

---

## Test Categories

### Test 1: Basic SD Card Detection and Initialization

**Objective:** Verify SD card is detected and initialized correctly

**Procedure:**
1. Remove SD card
2. Power on FC, connect via Configurator
3. Navigate to Blackbox tab
4. Verify "No SD card detected" or similar message
5. Insert SD card (hot insert)
6. Wait 2-3 seconds
7. Refresh Blackbox tab
8. Verify SD card is detected with correct size

**Success Criteria:**
- [ ] Card detected within 3 seconds of insertion
- [ ] Correct capacity displayed
- [ ] No errors in CLI (`status` command)

**Failure Indicators:**
- Card not detected
- Incorrect capacity
- CLI errors or warnings

---

### Test 2: Blackbox Write Speed Measurement

**Objective:** Measure sustained write speed during blackbox logging

**Procedure:**
1. Configure blackbox settings:
   ```
   set blackbox_device = SDCARD
   set blackbox_rate_num = 1
   set blackbox_rate_denom = 1
   save
   ```
2. Start logging (arm the FC or use `blackbox start` if available)
3. Let it log for exactly 60 seconds
4. Stop logging (disarm or `blackbox stop`)
5. Remove SD card, measure file size
6. Calculate write speed: `file_size_bytes / 60 = bytes/sec`

**Success Criteria:**
- [ ] Write speed > 200 KB/s (typical for 1kHz logging)
- [ ] No gaps or stutters in log file
- [ ] File integrity verified (can be parsed by Blackbox Explorer)

**Expected Values:**
| Loop Rate | Expected Log Size (60s) | Min Write Speed |
|-----------|------------------------|-----------------|
| 1 kHz     | ~12-15 MB              | 200 KB/s        |
| 2 kHz     | ~24-30 MB              | 400 KB/s        |
| 4 kHz     | ~48-60 MB              | 800 KB/s        |

---

### Test 3: Continuous Logging Stress Test

**Objective:** Test sustained logging over extended period

**Procedure:**
1. Format SD card (FAT32)
2. Configure maximum logging rate:
   ```
   set blackbox_rate_num = 1
   set blackbox_rate_denom = 1
   save
   ```
3. Start logging and let it run for **30 minutes** continuously
4. Monitor for any error messages via CLI or OSD
5. Stop logging
6. Verify log file integrity

**Success Criteria:**
- [ ] 30 minutes continuous logging without interruption
- [ ] No buffer overflow warnings
- [ ] Log file parseable by Blackbox Explorer
- [ ] No missing data segments

**Failure Indicators:**
- Logging stops unexpectedly
- "SD card full" when card has space
- Buffer overflow messages
- Corrupted log file

---

### Test 4: High-Frequency Logging Test

**Objective:** Test SD card at maximum logging throughput

**Procedure:**
1. Set highest practical logging rate:
   ```
   set blackbox_rate_num = 1
   set blackbox_rate_denom = 1
   set gyro_main_lpf_hz = 0
   set blackbox_log_gps = ON
   set blackbox_log_acc = ON
   set blackbox_log_debug = ON
   save
   ```
2. Start logging for 5 minutes
3. Monitor for buffer warnings
4. Stop and verify file

**Success Criteria:**
- [ ] No buffer overflows
- [ ] Consistent write rate
- [ ] File integrity maintained

---

### Test 5: Power Interruption Recovery Test

**Objective:** Verify SD card and filesystem integrity after unexpected power loss

**Procedure:**
1. Start blackbox logging
2. Let it run for 30 seconds
3. **Abruptly remove power** (pull power cable)
4. Wait 5 seconds
5. Restore power
6. Check SD card status in Configurator
7. Verify filesystem integrity (card readable on PC)
8. Check if previous log file is recoverable

**Success Criteria:**
- [ ] SD card still recognized after power loss
- [ ] Filesystem not corrupted (card mounts on PC)
- [ ] FC can create new log files
- [ ] Previous log partially recoverable (truncated but valid)

**Failure Indicators:**
- SD card not detected after power loss
- Filesystem corruption requiring format
- FC locks up on boot

---

### Test 6: Rapid Arm/Disarm Cycle Test

**Objective:** Test repeated start/stop of logging

**Procedure:**
1. Configure blackbox to log only when armed
2. Perform 20 rapid arm/disarm cycles:
   - Arm (logging starts)
   - Wait 5 seconds
   - Disarm (logging stops)
   - Wait 2 seconds
   - Repeat
3. Count number of log files created
4. Verify each log file is valid

**Success Criteria:**
- [ ] 20 separate log files created
- [ ] All files have valid headers
- [ ] No SD card errors during test
- [ ] No missed arm/disarm cycles

---

### Test 7: USB Mass Storage Mode Test

**Objective:** Verify USB MSC access to SD card works correctly

**Procedure:**
1. Connect FC via USB
2. Enter mass storage mode (CLI: `msc` or via Configurator)
3. Access SD card from PC
4. Copy a 100MB test file TO the SD card
5. Copy the file back FROM the SD card
6. Verify file integrity (hash comparison)
7. Exit MSC mode
8. Verify blackbox logging still works

**Success Criteria:**
- [ ] MSC mode accessible
- [ ] File copy in both directions works
- [ ] File integrity maintained
- [ ] Normal operation resumes after MSC exit

---

### Test 8: GPS Fix + Immediate Arm Test (F765 LOCKUP SPECIFIC)

**Objective:** Reproduce the exact F765 arming lockup scenario

**Background:** Issue #11299/#10586 - FC freezes when arming immediately after GPS fix. Root cause is SD card entering error state during GPS DMA activity, then blocking `HAL_SD_Init()` reset loop.

**Procedure:**
1. Power on FC with SD card inserted
2. Wait for GPS to start acquiring (but NO fix yet)
3. Verify blackbox is set to SDCARD
4. **Critical timing:** Watch for GPS fix (3D fix indicator)
5. **Immediately arm within 1-2 seconds of GPS fix**
6. Observe for freeze

**Repeat 10 times** - the issue is intermittent (reported 2-80% failure rate)

**Success Criteria:**
- [ ] 10/10 arm attempts succeed without freeze
- [ ] No servo jitter at GPS fix
- [ ] Blackbox logging starts normally each time

**Failure Indicators:**
- FC freezes at arm (power cycle required)
- Servo jitter when GPS acquires fix
- OSD freezes, telemetry stops
- Blackbox log not created

**Metrics to Record:**
- Number of successful arms: ___/10
- Time from GPS fix to arm attempt: ___ seconds
- Any servo jitter observed: YES/NO

---

### Test 9: SD Card Error Recovery Test (F765 LOCKUP SPECIFIC)

**Objective:** Test SD card recovery from error state without blocking

**Procedure:**
1. Start blackbox logging
2. **Induce SD card error** by one of these methods:
   - Partially eject SD card during write (careful!)
   - Use a known-problematic SD card
   - Create filesystem corruption
3. Observe FC behavior:
   - Does it freeze?
   - Does it recover gracefully?
   - How long does recovery take?
4. Re-insert/fix SD card
5. Verify normal operation resumes

**Success Criteria:**
- [ ] FC does NOT freeze on SD error
- [ ] Error recovery completes within 500ms
- [ ] No blocking behavior (OSD/servos remain responsive)
- [ ] FC can resume logging after recovery

**Failure Indicators:**
- FC freezes completely
- Recovery takes >1 second (blocking)
- Servos become unresponsive during recovery

---

### Test 10: DMA Contention Stress Test (F765 LOCKUP SPECIFIC)

**Objective:** Test SD card operations under heavy DMA load

**Procedure:**
1. Enable all DMA-intensive features:
   ```
   set gps_provider = UBLOX
   set gps_sbas_mode = AUTO
   set osd_video_system = AUTO
   set blackbox_rate_num = 1
   set blackbox_rate_denom = 1
   save
   ```
2. Connect GPS with high update rate (10Hz if possible)
3. Start blackbox logging
4. Observe for 10 minutes
5. Monitor for:
   - SD write stutters
   - GPS dropouts
   - OSD glitches
   - Any lockups

**Success Criteria:**
- [ ] No lockups during 10-minute test
- [ ] Continuous blackbox logging maintained
- [ ] No DMA-related errors in log

---

### Test 11: Blocking Behavior Measurement (F765 LOCKUP SPECIFIC)

**Objective:** Measure actual blocking time of SD operations

**Requires:** ST-Link debugger + logic analyzer (optional)

**Procedure:**
1. Add timing instrumentation (or use ST-Link breakpoints):
   - Measure time in `HAL_SD_Init()`
   - Measure time in `sdcardSdio_reset()`
   - Measure time in `sdcard_poll()` iterations
2. Trigger SD card error condition
3. Measure how long blocking operations take
4. Record maximum blocking duration

**Success Criteria (After HAL Update):**
- [ ] No single operation blocks >10ms
- [ ] Error recovery doesn't trigger infinite retry
- [ ] `goto doMore` loop limited or removed

**Key Breakpoints:**
- `sdmmc_sdio_hal.c:339` - `HAL_SD_Init(&hsd)`
- `sdcard_sdio.c:102` - `SD_Init()` in reset
- `sdcard_sdio.c:272` - `goto doMore` after reset

---

### Test 12: SD Card Variety Test

**Objective:** Verify compatibility with different SD card types

**Procedure:**
Test with multiple SD cards:
1. Class 4 card (slow)
2. Class 10 card (standard)
3. UHS-I card (fast)
4. Different brands (SanDisk, Samsung, generic)

For each card:
- Run Test 1 (detection)
- Run Test 2 (speed measurement)
- Run Test 8 (GPS+arm) - **Critical for F765 issue**
- Note any differences

**Success Criteria:**
- [ ] All cards detected correctly
- [ ] Speed scales appropriately with card class
- [ ] No initialization failures
- [ ] No GPS+arm lockups on any card type

---

## F765 Lockup-Specific Test Summary

**Tests 8-11 specifically target the root cause identified in the F765/H743 arming lockup investigation:**

| Test | Root Cause Targeted | HAL Fix Expected |
|------|---------------------|------------------|
| 8 - GPS Fix + Arm | GPS fix + arm timing race | V1.3.0 added 2ms power-up delay |
| 9 - Error Recovery | SD error recovery blocking | V1.2.8 improved error management |
| 10 - DMA Contention | DMA starvation issues | V1.3.2 fixed DMA abort handling |
| 11 - Blocking Measurement | Measure actual block times | All fixes combined |

**Reference:** `claude/projects/completed/investigate-f765-arming-lockup/summary.md`

**Critical Success Metric:** Test 8 must achieve 10/10 successful arms after GPS fix.

---

## Baseline Measurements (Before HAL Update)

### Test Environment
- **Firmware Version:** INAV [version]
- **HAL Version:** V1.2.2
- **CMSIS Version:** V1.2.0
- **Date:** ____

### Results Table

| Test | Result | Notes |
|------|--------|-------|
| Test 1: Detection | PASS/FAIL | |
| Test 2: Write Speed | _____ KB/s | |
| Test 3: 30min Continuous | PASS/FAIL | |
| Test 4: High-Frequency | PASS/FAIL | |
| Test 5: Power Interrupt | PASS/FAIL | |
| Test 6: Arm/Disarm Cycles | ___/20 | |
| Test 7: USB MSC | PASS/FAIL | |
| **Test 8: GPS+Arm (F765)** | **___/10** | **CRITICAL** |
| Test 9: Error Recovery (F765) | PASS/FAIL | |
| Test 10: DMA Contention (F765) | PASS/FAIL | |
| Test 11: Blocking Time (F765) | ___ ms max | |
| Test 12: Card Variety | ___/4 cards | |

### Issues Observed
1.
2.
3.

---

## Comparison Measurements (After HAL Update)

### Test Environment
- **Firmware Version:** INAV [version]
- **HAL Version:** V1.3.3
- **CMSIS Version:** V1.3.0
- **Date:** ____

### Results Table

| Test | Before | After | Improvement |
|------|--------|-------|-------------|
| Test 1: Detection | | | |
| Test 2: Write Speed | | | |
| Test 3: 30min Continuous | | | |
| Test 4: High-Frequency | | | |
| Test 5: Power Interrupt | | | |
| Test 6: Arm/Disarm Cycles | | | |
| Test 7: USB MSC | | | |
| **Test 8: GPS+Arm (F765)** | | | **CRITICAL** |
| Test 9: Error Recovery (F765) | | | |
| Test 10: DMA Contention (F765) | | | |
| Test 11: Blocking Time (F765) | | | |
| Test 12: Card Variety | | | |

---

## Debugging with ST-Link

If issues are encountered, the ST-Link debugger can be used for low-level debugging:

### Connection
1. Connect ST-Link to MATEKF765SE SWD pins (SWDIO, SWCLK, GND)
2. Use OpenOCD or STM32CubeIDE for debugging

### Key Debug Points
- `sdcard_init()` - Card initialization
- `SDMMC1_IRQHandler` - SDIO interrupt handler
- `SD_DMAReceiveCplt` / `SD_DMATransmitCplt` - DMA completion
- `HAL_SD_ErrorCallback` - Error handling

### Common Error Codes
| Code | Meaning |
|------|---------|
| `HAL_SD_ERROR_CMD_RSP_TIMEOUT` | Card not responding |
| `HAL_SD_ERROR_DATA_TIMEOUT` | Data transfer timeout |
| `HAL_SD_ERROR_TX_UNDERRUN` | TX buffer underrun |
| `HAL_SD_ERROR_RX_OVERRUN` | RX buffer overrun |
| `HAL_SD_ERROR_DMA` | DMA transfer error |

---

## CLI Commands Reference

```bash
# Check SD card status
status

# Blackbox configuration
get blackbox

# Start/stop blackbox manually (if supported)
blackbox start
blackbox stop

# Enter mass storage mode
msc

# Format SD card (if supported)
sd_format
```

---

## Expected HAL Improvements (V1.2.2 → V1.3.3)

Based on STM32CubeF7 release notes:

1. **SDMMC_DATATIMEOUT** - Updated for different clock scenarios
2. **DMA handling** - Improved reliability
3. **Error recovery** - Better error handling and recovery
4. **Power sequencing** - Improved card initialization

---

## Summary

After completing all tests:

1. **If baseline shows issues:** Document specific failures and error patterns
2. **If HAL update improves results:** Quantify improvements (e.g., "30% faster write speed", "no more timeout errors")
3. **If HAL update causes regressions:** Document and investigate before merging

**Report findings to Manager with:**
- Baseline measurements
- Post-update measurements
- Recommendation (proceed/investigate further)
