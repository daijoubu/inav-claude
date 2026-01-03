# GPS Navigation Testing Scripts

Scripts for testing GPS navigation features including Return-to-Home (RTH), position hold, GPS recovery, and EPH logging.

## Quick Start

```bash
# Test Return-to-Home
python3 gps_rth_test.py

# Test GPS recovery after signal loss
python3 gps_recovery_test.py

# GPS hover test with EPH logging
python3 gps_hover_test_30s.py
```

## Scripts

### gps_rth_test.py - Return-to-Home navigation test
Comprehensive RTH test: arms SITL, flies to position, triggers RTH, validates return.

### gps_rth_bug_test.py - RTH bug reproduction
Reproduces specific RTH bugs based on issue reports.

### gps_recovery_test.py - GPS signal recovery test
Tests position estimator when GPS is lost then recovered.

### gps_test_v6.py - General GPS testing suite
Comprehensive test script with multiple scenarios (version 6).

### gps_hover_test_30s.py - 30-second hover test
Quick validation of GPS position hold stability.

---

### gps_with_naveph_logging.py - EPH logging (uNAVlib)
GPS injection with navEPH logging using legacy uNAVlib library.

### gps_with_naveph_logging_mspapi2.py - EPH logging (mspapi2) ⭐
Modern navEPH logging using mspapi2. **Prefer this for new work.**

## Common Test Workflows

### RTH Testing
```bash
# 1. Configure SITL for arming
cd ../config
python3 configure_sitl_for_arming.py

# 2. Run RTH test
cd ../testing
python3 gps_rth_test.py
```

### GPS Recovery Testing
```bash
python3 gps_recovery_test.py
```

### EPH Analysis
```bash
# Use mspapi2 version (modern)
python3 gps_with_naveph_logging_mspapi2.py

# Analyze EPH spectrum
cd ../monitoring
python3 analyze_naveph_spectrum.py <log_file.csv>
```

## Prerequisites

- **SITL running:** Start SITL before running tests
- **MSP receiver configured:** Use `../config/configure_sitl_for_arming.py`
- **GPS provider set to MSP:** Some tests require this

## Dependencies

- **mspapi2:** `pip3 install ~/Documents/planes/inavflight/mspapi2`
- **uNAVlib:** Available in `~/Documents/planes/inavflight/uNAVlib`

## Notes

**Port Usage:**
- Default MSP port: 5760 (UART1)
- Most scripts auto-detect SITL on localhost:5760

**Arming:**
- Most navigation tests require SITL to be armed
- Use `../config/configure_sitl_for_arming.py` for one-time setup
- Configuration persists in `eeprom.bin`

**Test Duration:**
- Tests run until completion or timeout
- Some tests have configurable duration parameters

## See Also

- `../injection/` - GPS data injection scripts used by these tests
- `../workflows/` - Complete automated test workflows
- `../docs/README_GPS_BLACKBOX_TESTING.md` - Detailed testing procedures
