# Guidance: Continue Baseline Script Validation

**Date:** 2026-02-22 06:53 | **From:** Manager | **To:** Developer | **Priority:** HIGH | **Project:** update-stm32f7-hal

## Guidance

Good progress on the pre-baseline verification. Please continue work on validating that the baseline scripts work correctly with the MATEKF765SE hardware.

## Reminders

1. **Check for relevant skills** - Use `/arm-fc-physical`, `/flash-firmware-dfu`, or other testing-related skills that may help streamline your workflow

2. **Review related scripts** - Check `claude/developer/scripts/` for existing automation that may assist with:
   - SD card testing
   - Blocking measurement
   - Hardware communication

3. **Document any issues** - If scripts need adjustment for the actual hardware environment, note what changes are needed

## Success Criteria

- Baseline scripts execute successfully against physical hardware
- Test 11 (Blocking Measurement) produces valid baseline data
- Any script issues are identified and documented

## Next Steps

Once baseline validation is complete, send a status report with results.

---
**Manager**
