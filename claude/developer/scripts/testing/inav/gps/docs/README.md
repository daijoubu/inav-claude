# GPS Testing Documentation

Specialized documentation for GPS testing workflows, blackbox logging, and debugging.

## Documentation Index

### GPS Testing Workflows

**[README_GPS_BLACKBOX_TESTING.md](README_GPS_BLACKBOX_TESTING.md)** (300+ lines)
- Complete GPS + blackbox testing workflow
- SITL configuration, arming, GPS injection
- Log capture and analysis
- Troubleshooting guide

### GPS Data Issues

**[NULL_BYTE_INVESTIGATION.md](NULL_BYTE_INVESTIGATION.md)**
- Investigation of null byte issues in GPS data
- Decoder failures and solutions

### Blackbox Documentation (Moved)

**Blackbox-specific documentation has been moved to:** `../../blackbox/docs/`

Including:
- BLACKBOX_SERIAL_WORKFLOW.md
- BLACKBOX_TESTING_PROCEDURE.md
- BLACKBOX_STORAGE_ISSUE.md
- REPLAY_BLACKBOX_README.md
- REPLAY_WORKFLOW_LESSONS.md
- TRANSITION_PLAN.md
- MOTORS_CONDITION_BUG.md
- HIGH_FREQUENCY_LOGGING_STATUS.md

### SITL/MSP Documentation (Moved)

**SITL and MSP documentation has been moved to:** `../../sitl/`

Including:
- HARDWARE_FC_MSP_RX_STATUS.md
- MSP2_INAV_DEBUG_FIX.md
- MSP_QUERY_RATE_ANALYSIS.md

### Full Reference

**[FULL_REFERENCE.md](FULL_REFERENCE.md)** (650+ lines)
- Comprehensive documentation of ALL GPS test tools (pre-reorganization)
- Detailed script reference tables
- Historical reference

## Quick Navigation

**GPS Testing:** Start with [README_GPS_BLACKBOX_TESTING.md](README_GPS_BLACKBOX_TESTING.md)

**GPS Data Issues:** See [NULL_BYTE_INVESTIGATION.md](NULL_BYTE_INVESTIGATION.md)

**Blackbox Documentation:** See [../../blackbox/docs/](../../blackbox/docs/)

**SITL/MSP Documentation:** See [../../sitl/](../../sitl/)

## See Also

- `../workflows/` - Automated test workflows using these procedures
- `../injection/` - GPS data injection scripts
- `../config/` - Configuration scripts referenced in documentation
