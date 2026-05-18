# Configurator Ports Tab Test Scripts

Scripts for validating serial port function UI behavior in the INAV Configurator Ports tab.

## test-sensor-port-function.js

Tests a named sensor port function (e.g. CRSF_SENSOR, future SBUS_SENSOR) for:
- Rule existence and correct properties (groups, defaultBaud, lockedBaud, isUnique)
- Correct bit mask (bit position matches firmware FUNCTION_* enum)
- Round-trip mask→functions correctness
- i18n display name loaded
- Option appears in every UART's sensors dropdown
- Baud select disabled/enabled correctly on select/deselect
- Locked baud NOT in SENSOR baud list (prevents MSP index -1 on save)

### Usage

1. Connect FC to Configurator and navigate to Ports tab
2. In Chrome DevTools MCP (or DevTools console), run the script via evaluate_script
3. Configure the top constants for your function:
   - FUNCTION_NAME: internal rule name (e.g. 'SBUS_SENSOR')
   - EXPECTED_BIT: firmware bit position
   - EXPECTED_BAUD: required baud rate
   - LOCKED_BAUD: true if baud select should be disabled

### Notes

- Test 6 (baud lock) requires the var/let closure fix in ports.js (var column → let column)
  Without this fix all handlers fire with column='peripherals' instead of 'sensors'
- Sensor baud (EXPECTED_BAUD) should NOT be added to BAUD_RATES_post1_6_3 in MSPHelper.js
  unless the firmware also adds it to its serialBaudRate enum in the same position
- Firmware hardcodes the baud for sensor functions internally and ignores sensors_baudrate field

### Key findings from CRSF sensor testing (2026-05-17)

- var column bug: ports.js rendering loop used var column (function-scoped), causing all
  closures to see column='peripherals' (last iteration value). Fixed with let column.
- BAUD_RATES_post1_6_3: 420000 is NOT in firmware baud enum, so do not add it to MSPHelper.
  Firmware ignores sensors_baudrate for CRSF_SENSOR (hardcodes 420000 internally).
- Non-unique IDs: multiple selects share id="function-sensors" but jQuery.find() scopes
  correctly within parent TD context (portFunc-sensors-N).
