# GPS Testing Tools

Comprehensive GPS testing infrastructure for INAV firmware. Supports motion simulation, blackbox logging, position estimation analysis, and automated test workflows for SITL and physical flight controllers.

## Quick Start

```bash
cd ~/Documents/planes/inavflight/claude/test_tools/inav/gps

# Motion simulation + telemetry (RECOMMENDED)
workflows/test_motion_simulator.sh climb 30

# GPS + blackbox logging
workflows/run_gps_blackbox_test.sh climb 60

# Monitor GPS status
monitoring/monitor_gps_status.py
```

## Directory Structure

| Directory | Purpose | Scripts |
|-----------|---------|---------|
| **[workflows/](workflows/)** | **⭐ Start here** - GPS testing workflows | 3 scripts |
| **[injection/](injection/)** | GPS data injection (MSP) | 6 scripts |
| **[testing/](testing/)** | GPS navigation tests (RTH, recovery, EPH logging) | 7 scripts |
| **[monitoring/](monitoring/)** | GPS status, diagnostics, analysis | 4 scripts |
| **[config/](config/)** | GPS configuration | 1 script |
| **[docs/](docs/)** | GPS-specific documentation | 3 docs |

## Common Tasks

| I Want To... | Go To... |
|--------------|----------|
| **Test GPS with CRSF telemetry** | [workflows/test_motion_simulator.sh](workflows#test_motion_simulatorsh--recommended) |
| **Capture blackbox logs** | [workflows/run_gps_blackbox_test.sh](workflows#run_gps_blackbox_testsh) |
| **Inject GPS altitude** | [injection/inject_gps_altitude.py](injection#inject_gps_altitudepy) |
| **Reproduce GPS fluctuation bug** | [injection/simulate_gps_fluctuation_issue_11202.py](injection#simulate_gps_fluctuation_issue_11202py) |
| **Test Return-to-Home** | [testing/gps_rth_test.py](testing#gps_rth_testpy) |
| **Monitor GPS in real-time** | [monitoring/monitor_gps_status.py](monitoring#monitor_gps_statuspy) |
| **Configure GPS settings** | [config/configure_sitl_gps.py](config/) |
| **Configure SITL for arming** | [../sitl/configure_sitl_for_arming.py](../sitl/) |
| **Enable blackbox logging** | [../blackbox/config/configure_sitl_blackbox_file.py](../blackbox/) |

## Primary Workflows

### test_motion_simulator.sh (RECOMMENDED)
**Motion simulation + CRSF telemetry validation**

```bash
workflows/test_motion_simulator.sh climb 30
```

Coordinates GPS injection (port 5760) with CRSF RC sender (port 5761). Validates GPS altitude appears correctly in CRSF telemetry.

**See:** [workflows/README.md](workflows#test_motion_simulatorsh--recommended)

---

### run_gps_blackbox_test.sh
**Complete GPS + blackbox workflow**

```bash
workflows/run_gps_blackbox_test.sh climb 60
```

Automated: SITL config → arming → GPS injection → blackbox capture. Output in `inav/build_sitl/*.TXT`

**See:** [workflows/README.md](workflows#run_gps_blackbox_testsh)

---

## Key Concepts

**Port Separation:**
- **5760** - UART1 (MSP) - GPS injection, configuration
- **5761** - UART2 (CRSF) - RC commands, telemetry
- Zero interference between protocols

**Motion Profiles:**
- `climb` - 0m → 100m at 5 m/s
- `descent` - 100m → 0m at 2 m/s
- `hover` - Constant 50m
- `sine` - Oscillating ±30m

**Blackbox Modes:**
- **FILE** - Saves to .TXT files (SITL default)
- **SERIAL** - Streams via MSP port

## Prerequisites

**SITL Built and Running:**
```bash
cd ~/Documents/planes/inavflight/inav/build_sitl
./bin/SITL.elf &
```

**Python Libraries:**
```bash
# mspapi2 (modern - recommended)
pip3 install ~/Documents/planes/inavflight/mspapi2

# uNAVlib (legacy - some scripts)
# Already available in ~/Documents/planes/inavflight/uNAVlib
```

## Documentation

**Start here:** [docs/README_GPS_BLACKBOX_TESTING.md](docs/README_GPS_BLACKBOX_TESTING.md) - Complete blackbox workflow (300+ lines)

**Full index:** [docs/README.md](docs/) - All 14+ documentation files organized by topic

**Blackbox documentation:** [../blackbox/docs/](../blackbox/docs/) - Blackbox workflows and troubleshooting

**Related tools:**
- `../blackbox/` - Blackbox logging, replay, analysis
- `../sitl/` - SITL configuration and utilities
- `../crsf/` - CRSF protocol tools

## Related Tools

**Skills:** /sitl-arm, /test-crsf-sitl
**Directories:** `../crsf/` (CRSF tools), `../sitl/` (SITL utilities)

## Project History

**Issue #11202** (Dec 2025) - GPS fluctuation simulator, blackbox enhancements, replay workflow
**Infrastructure** (Nov-Dec 2025) - Motion simulation, CRSF telemetry, blackbox automation

## Notes

**Configuration Persistence:**
- SITL: Settings in `eeprom.bin` (delete to reset)
- Physical FC: Settings in EEPROM

**BLACKBOX Feature Flag:**
- Must enable BLACKBOX feature (bit 19)
- `blackbox_device` setting alone insufficient
- Use `config/enable_blackbox_feature.py`

**Dependencies:**
- Prefer **mspapi2** for new scripts
- **uNAVlib** for legacy compatibility

---

**Questions?** See subdirectory READMEs or [docs/](docs/) for detailed documentation.
