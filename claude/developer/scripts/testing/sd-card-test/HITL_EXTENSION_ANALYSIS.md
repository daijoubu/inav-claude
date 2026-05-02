# HITL Test-Engineer Capability Extension Analysis

**Date:** 2026-02-23
**Project:** update-stm32f7-hal
**Author:** Developer

---

## Overview

This document analyzes the SD card test suite and HITL library to identify reusable modules and integration points for extending the test-engineer agent's Hardware-In-The-Loop testing capabilities.

---

## Existing Module Inventory

### 1. HITL Library (`claude/developer/scripts/testing/hitl/__init__.py`)

**Core Classes:**

| Class | Purpose | Reusability |
|-------|---------|-------------|
| `HITLConnection` | Physical FC connection via serial MSP | High - Already extracted |
| `HITLDebugger` | GDB-based lockup debugging | High - Already extracted |
| `SymbolTable` | ELF symbol lookup for debugging | High - Already extracted |

**Key Features:**
- Context manager for FC connection
- Automatic FAILSAFE clearing
- Arming/disarming with RC channel control
- Lockup detection (3 consecutive MSP timeouts)
- Debug state capture on lockup

### 2. SD Card Test Suite (`sd_card_test.py`)

**Reusable Modules:**

| Module | Lines | Purpose | HITL Suitability |
|--------|-------|---------|------------------|
| `FCConnection` | 249-800+ | MSP communication wrapper | High - Core infrastructure |
| `SDCardStatus` | 134-150 | SD card state dataclass | High - Data structure |
| `GPSStatus` | 152-171 | GPS state dataclass | High - Data structure |
| `ArmingStatus` | 173-190 | Arming flags dataclass | High - Data structure |
| `TestResult` | 192-210 | Test result dataclass | High - Data structure |
| `LogVerificationResult` | 213-242 | Log verification dataclass | High - Data structure |

**Test Functions (Automated):**

| Test | Function | MSP Commands Used | CI/CD Ready |
|------|----------|-------------------|-------------|
| Test 1 | SD Card Detection | `MSP_SDCARD_SUMMARY` (79) | Yes |
| Test 2 | Write Speed | `MSP_SDCARD_SUMMARY`, timing | Yes |
| Test 3 | Continuous Logging | `MSP_SDCARD_SUMMARY`, timing | Yes |
| Test 4 | High-Frequency Logging | Blackbox config, timing | Yes |
| Test 6 | Arm/Disarm Cycles | `MSP_SET_RAW_RC` (200), `MSP2_INAV_STATUS` (0x2000) | Yes |
| Test 8 | GPS Fix + Arm | `MSP_RAW_GPS` (106), arming | Yes (with GPS) |
| Test 10 | DMA Contention | GPS + SD card + timing | Yes (with GPS) |
| Test 11 | Blocking Measurement | ST-Link + GDB | Requires hardware |

### 3. Debug Tools

| Tool | Purpose | Integration |
|------|---------|-------------|
| `debug_lockup.py` | Capture FC state on lockup | Integrates with HITLDebugger |
| `gdb_timing.py` | Timing breakpoints for blocking | Requires ST-Link |
| OpenOCD configs | Target-specific debug configs | Already extracted |

---

## Integration Points for Test-Engineer

### MSP Commands (Automated Query)

| Command | Code | Purpose | Test-Engineer Use |
|---------|------|---------|-------------------|
| `MSP_SDCARD_SUMMARY` | 79 | SD card status | Storage testing |
| `MSP_DATAFLASH_SUMMARY` | 70 | Flash status | Storage testing |
| `MSP2_INAV_STATUS` | 0x2000 | Arming flags, CPU load | State queries |
| `MSP_RAW_GPS` | 106 | GPS fix, satellites | GPS testing |
| `MSP_GPSSTATISTICS` | 166 | GPS performance | GPS testing |
| `MSP_SET_RAW_RC` | 200 | RC channel control | Arming control |
| `MSP2_SET_ARMING_DISABLED` | 0x200B | Enable/disable arming | Safety control |
| `MSP2_BLACKBOX_CONFIG` | 0x201A | Blackbox settings | Logging config |

### CLI Hooks (Serial/Telnet)

```
status           - Full FC status including SD card
get blackbox     - Blackbox configuration
blackbox start   - Start logging manually
blackbox stop    - Stop logging
msc              - Enter USB mass storage mode
sd_format        - Format SD card
tasks            - Show task CPU usage (debugging)
dump profile     - Full configuration dump
```

### Hardware Interfaces

| Interface | Method | Automation Level |
|-----------|--------|------------------|
| USB CDC (Serial) | MSP protocol via pyserial | Full automation |
| ST-Link SWD | OpenOCD + GDB | Automation with hardware |
| USB MSC | Mass storage mode | Partial (requires FC reboot) |

---

## Recommended HITL Extensions

### Extension 1: Automated Regression Test Suite

**Purpose:** CI/CD-compatible tests for firmware validation

**Implementation:**
```python
class HITLRegressionSuite:
    """Reusable regression test suite for CI/CD"""
    
    def __init__(self, port: str, elf_path: str = None):
        self.fc = HITLConnection(port, elf_path)
        
    def run_basic_tests(self) -> dict:
        """Run tests 1-6 (no GPS required)"""
        results = {}
        results['sd_detection'] = self.test_sd_detection()
        results['sd_write_speed'] = self.test_write_speed()
        results['arm_disarm'] = self.test_arm_disarm_cycles()
        return results
```

**Integration Points:**
- Add to `test-engineer` agent capabilities
- Output JSON results for CI consumption
- Support baseline comparison mode

### Extension 2: Lockup Detection & Debug Capture

**Purpose:** Automated debug capture when FC hangs

**Implementation:**
```python
class LockupMonitor:
    """Monitor for FC lockups and capture debug state"""
    
    def __init__(self, fc: HITLConnection, debugger: HITLDebugger):
        self.fc = fc
        self.debugger = debugger
        
    def run_with_monitoring(self, test_func, timeout: float = 60.0):
        """Run test with automatic lockup detection"""
        self.fc._consecutive_timeouts = 0
        self.fc._max_timeouts = 3
        
        # Run test with watchdog
        result = test_func()
        
        return result
```

**Already Implemented:** `HITLConnection._check_lockup()` and `debug_lockup.py`

### Extension 3: Sensor Simulation Support

**Purpose:** Mock sensor data for testing without hardware

**Current State:** Not implemented

**Recommended Approach:**
- Use SITL for sensor simulation (existing capability)
- HITL tests should focus on real hardware validation
- Keep HITL and SITL separate concerns

### Extension 4: Parameterized Test Runner

**Purpose:** Run tests with varying parameters

**Implementation:**
```python
class ParameterizedTestRunner:
    """Run tests with parameter variations"""
    
    def run_sd_card_variety(self, cards: list[dict]):
        """Test multiple SD card types"""
        results = []
        for card in cards:
            print(f"Testing: {card['name']} (Class {card['class']})")
            # Manual card swap required
            input("Insert card and press Enter...")
            result = self.fc.test_sd_card()
            results.append({'card': card, 'result': result})
        return results
```

### Extension 5: Baseline Comparison Tool

**Purpose:** Compare HAL versions automatically

**Implementation:**
```python
class BaselineComparator:
    """Compare test results between HAL versions"""
    
    def __init__(self, baseline_file: str):
        with open(baseline_file) as f:
            self.baseline = json.load(f)
    
    def compare(self, current_results: dict) -> dict:
        """Compare current results to baseline"""
        comparison = {}
        for test_name, current in current_results.items():
            baseline = self.baseline.get(test_name, {})
            comparison[test_name] = {
                'baseline': baseline,
                'current': current,
                'change_pct': self._calc_change(baseline, current)
            }
        return comparison
```

---

## Files to Extract to HITL Library

### Already Extracted
- `claude/developer/scripts/testing/hitl/__init__.py` (HITLConnection, HITLDebugger, SymbolTable)

### Recommended Additions

| Source File | Extract To | Content |
|-------------|------------|---------|
| `sd_card_test.py` | `hitl/msp_commands.py` | MSPCode enum, data parsing |
| `sd_card_test.py` | `hitl/dataclasses.py` | SDCardStatus, GPSStatus, ArmingStatus |
| `debug_lockup.py` | Already in HITLDebugger | ✓ |
| `gdb_timing.py` | `hitl/gdb_timing.py` | Timing breakpoints |

---

## Test-Engineer Agent Integration

### New Agent Capabilities

```
The test-engineer agent can now:

1. Connect to physical FC via HITLConnection
2. Run automated SD card tests (Tests 1-6, 8, 10)
3. Detect FC lockups and capture debug state
4. Compare baseline vs. current HAL performance
5. Generate JSON test reports for CI/CD

Example usage:
  from claude.developer.scripts.testing.hitl import HITLConnection, HITLDebugger
  
  with HITLConnection('/dev/ttyACM0', elf_path='build/MATEKF765.elf') as fc:
      fc.wait_for_arming_ready()
      with fc.armed():
          # Run tests while armed
          result = run_stress_test(fc)
```

### Agent Workflow for HITL Testing

```
1. Check hardware availability
   - FC connected (CDC device exists)
   - GPS connected (optional, for GPS tests)
   - ST-Link connected (optional, for debug capture)

2. Connect via HITLConnection
   - Establish MSP communication
   - Query FC status
   - Clear FAILSAFE if needed

3. Run test suite
   - Execute automated tests
   - Monitor for lockups
   - Capture debug state on failure

4. Generate report
   - JSON results file
   - Comparison with baseline (if available)
   - Debug captures (if lockup occurred)

5. Cleanup
   - Disarm FC
   - Disconnect cleanly
```

---

## Summary

### Reusable Modules Identified: 12
- HITLConnection (already extracted)
- HITLDebugger (already extracted)
- SymbolTable (already extracted)
- FCConnection (candidate for extraction)
- MSPCode enum (candidate)
- Status dataclasses (candidate)
- Test result classes (candidate)
- Debug capture scripts (integrated)

### Integration Points Documented: 8 MSP commands + CLI hooks
- MSP_SDCARD_SUMMARY, MSP_RAW_GPS, MSP2_INAV_STATUS, etc.
- CLI: status, blackbox, msc commands

### Recommended Extensions: 5
1. HITLRegressionSuite - CI/CD automation
2. LockupMonitor - Already implemented
3. SensorSimulation - Use SITL instead
4. ParameterizedTestRunner - Card variety testing
5. BaselineComparator - HAL version comparison

### CI/CD Ready Tests: 7/12 (58%)
- Tests 1-4, 6, 8, 10 can run without manual intervention (with GPS)
- Tests 5, 7, 9, 11, 12 require manual steps or special hardware

---

## Next Steps

1. Extract remaining modules to `hitl/` library
2. Add `HITLRegressionSuite` class to library
3. Add `BaselineComparator` class to library
4. Update test-engineer agent documentation
5. Create example scripts for common test scenarios
