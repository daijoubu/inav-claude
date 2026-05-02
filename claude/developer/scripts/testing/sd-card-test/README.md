# SD Card Test Plan for MATEKF765SE

## Overview

This directory contains test procedures and automation for validating SD card reliability on the MATEKF765SE, specifically for the STM32F7 HAL update (V1.2.2 → V1.3.3).

## Contents

| File | Description |
|------|-------------|
| `SD-CARD-TEST-PLAN.md` | Complete manual test procedures (12 tests) |
| `sd_card_test.py` | Main automated test script (MSP protocol) |
| `hitl_sdcard_test.py` | HITL-enhanced tests with fault injection |
| `test_11_blocking.py` | Test 11: Blocking measurement (ST-Link + GDB) |
| `gdb_timing.py` | GDB Python script for timing breakpoints |
| `openocd_matekf765.cfg` | OpenOCD configuration for MATEKF765SE |
| `README.md` | This file |

## Quick Start

### Manual Testing

See `SD-CARD-TEST-PLAN.md` for complete test procedures.

### Automated Testing

```bash
# Install dependencies
pip install mspapi2

# Run all automated tests (excludes long-running Test 9)
python sd_card_test.py /dev/ttyACM0

# Run specific tests
python sd_card_test.py /dev/ttyACM0 --test 1,2,8

# Quick validation (shorter test durations)
python sd_card_test.py /dev/ttyACM0 --quick

# Baseline measurement (before HAL update)
python sd_card_test.py /dev/ttyACM0 --baseline --hal-version 1.2.2 --output baseline.json

# Comparison measurement (after HAL update)
python sd_card_test.py /dev/ttyACM0 --hal-version 1.3.3 --output comparison.json
```

### Test Durations and Timeouts

| Test | Default Duration | Quick Mode | Timeout Required |
|------|-----------------|------------|------------------|
| 1 | instant | instant | default |
| 2 | 60s | 60s | 2 min |
| 3 | 5 min | 2 min | 8 min |
| 4 | 60s | 60s | 2 min |
| 6 | ~5 min | ~5 min | 10 min |
| 8 | ~5 min | ~5 min | 10 min |
| 9 | **60 min** | 5 min | **65 min** |
| 10 | 10 min | 5 min | 15 min |
| 11 | 60s | 60s | 2 min |

**Test 9 requires extended timeout:**
```bash
# Test 9 needs 60+ minute timeout
timeout 3900 python sd_card_test.py /dev/ttyACM0 --test 9

# Or use quick mode for validation
python sd_card_test.py /dev/ttyACM0 --test 9 --quick
```

## Test Coverage

**With real hardware (MATEKF765SE + GPS + ST-Link):**

| Test | Automated | Manual | Description |
|------|-----------|--------|-------------|
| 1 | ✅ | ✅ | SD Card Detection |
| 2 | ✅ | ✅ | Write Speed |
| 3 | ✅ | ✅ | Continuous Logging |
| 4 | ✅ | ✅ | High-Frequency Logging |
| 5 | ❌ | ✅ | Power Interruption |
| 6 | ✅ | ✅ | Arm/Disarm Cycles |
| 7 | ❌ | ✅ | USB Mass Storage |
| **8** | **✅** | ✅ | **GPS Fix + Arm (F765 CRITICAL)** |
| 9 | ❌ | ✅ | Error Recovery (F765) |
| **10** | **✅** | ✅ | **DMA Contention (F765)** |
| **11** | **✅** | ✅ | **Blocking Measurement (ST-Link + GDB)** |
| 12 | ❌ | ✅ | SD Card Variety |

**Automation coverage: 9/12 tests (75%)**

### Test 11: Blocking Measurement

Test 11 uses ST-Link + OpenOCD + GDB to measure actual blocking times:

```bash
# Run Test 11 standalone
python test_11_blocking.py build/MATEKF765.elf --duration 60

# Run as part of test suite
python sd_card_test.py /dev/ttyACM0 --test 11 --elf build/MATEKF765.elf
```

**Monitored functions:**
- `HAL_SD_Init()` - Main blocking HAL call
- `HAL_SD_InitCard()` - Card initialization
- `SD_Init()` - SDIO driver init
- `sdcardSdio_reset()` - Reset with potential blocking loop
- `sdcardSdio_poll()` - Contains `goto doMore` loop
- `blackboxStart()` - Triggered at arming

**Pass criteria:** Maximum single call duration < 10ms

## F765 Lockup Tests

Tests 8-11 specifically target the root cause identified in `investigate-f765-arming-lockup`:

- **Test 8**: Critical - GPS fix + immediate arm timing race
- **Test 9**: SD card error recovery without blocking
- **Test 10**: DMA contention during GPS activity
- **Test 11**: Measure actual blocking times with ST-Link

## HITL-Enhanced Testing

Hardware-In-The-Loop (HITL) tests provide deeper coverage through:

1. **State Introspection** - Read SD card driver state from FC memory
2. **Fault Injection** - Simulate DMA errors, timeouts, CRC errors
3. **Recovery Validation** - Verify driver handles faults without blocking

### HITL Test Coverage

| Code Path | Basic Tests | HITL Tests |
|-----------|-------------|------------|
| Normal read/write | ✓ | ✓ |
| DMA error recovery | ✗ | ✓ |
| Timeout recovery | ✗ | ✓ |
| CRC error handling | ✗ | ✓ |
| Consecutive failure threshold | ✗ | ✓ |
| Forced reset recovery | ✗ | ✓ |

### Running HITL Tests

```bash
# Prerequisites: ST-Link connected, OpenOCD available
python hitl_sdcard_test.py /dev/ttyACM0 --elf build/MATEKF765.elf

# Run specific test category
python hitl_sdcard_test.py /dev/ttyACM0 --elf build/MATEKF765.elf --test introspect
python hitl_sdcard_test.py /dev/ttyACM0 --elf build/MATEKF765.elf --test fault-injection

# Save results
python hitl_sdcard_test.py /dev/ttyACM0 --elf build/MATEKF765.elf --output hitl_results.json
```

### HITL API

```python
from claude.developer.scripts.testing.hitl import HITLSDCard

with HITLSDCard('/dev/ttyACM0', elf_path='build/MATEKF765.elf') as hitl:
    # State introspection
    state = hitl.get_sdcard_state()
    print(f"SD state: {state.state_name}")
    
    # DMA state
    dma = hitl.get_dma_state()
    print(f"DMA busy: {dma.busy}")
    
    # Fault injection
    result = hitl.inject_dma_error()
    print(f"Injected: {result.fault_type}")
    
    # Verify recovery
    state = hitl.get_sdcard_state()
    print(f"Recovered: {state.state_name == 'READY'}")
```

### Fault Injection Types

| Fault Type | Function | Effect |
|------------|----------|--------|
| DMA Error | `inject_dma_error()` | Sets DMA transfer error flag |
| SD Timeout | `inject_sd_timeout()` | Forces timeout condition |
| CRC Error | `inject_crc_error()` | Sets SDMMC CRC fail flag |
| Forced Reset | `force_sdcard_reset()` | Forces SD state to RESET |
| Consecutive Failures | `inject_consecutive_failures(n)` | Triggers threshold behavior |

## Requirements

### Hardware
- MATEKF765SE flight controller
- SD card (Class 10 recommended)
- USB cable
- GPS module (for Test 8)
- ST-Link debugger (for Test 11)

### Software
- Python 3.9+
- mspapi2 library

## Output

The script generates:
1. Console output with pass/fail for each test
2. JSON results file (optional, use `--output`)

Example output:
```
======================================================================
SD CARD TEST REPORT - BASELINE
======================================================================
Timestamp: 2026-02-21 16:30:00
HAL Version: 1.2.2

RESULTS SUMMARY
----------------------------------------------------------------------
  Test 1: SD Card Detection              [PASS] (0.5s)
  Test 2: Write Speed Measurement        [PASS] (60.2s)
           write_speed_kbps: 245.3
  Test 8: GPS Fix + Immediate Arm        [PASS] (125.0s)
           successful_arms: 10
           lockups_detected: 0

----------------------------------------------------------------------
TOTAL: 3/3 tests passed
======================================================================
```
