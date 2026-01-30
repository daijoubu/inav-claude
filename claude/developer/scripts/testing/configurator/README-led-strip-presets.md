# LED Strip Presets Test Suite

This directory contains test scripts for validating the three new LED strip quick layout presets added to INAV Configurator.

---

## Overview

**Feature:** Quick Layout Presets for LED Strip Tab
**Presets Added:**
1. **xframe** - X-frame quadcopter (20 LEDs)
2. **crossframe** - Cross-frame quadcopter (20 LEDs)
3. **wing** - Fixed-wing aircraft (20 LEDs)

**Test Files:**
- `test_led_strip_presets.py` - Test data and validation script
- `test_led_presets_interactive.md` - Interactive MCP testing guide
- `LED_STRIP_PRESET_TEST_REPORT.md` - Test report template
- `README-led-strip-presets.md` - This file

---

## Quick Start

### 1. Review Expected Behavior

Run the Python test script to see expected preset configurations:

```bash
python3 test_led_strip_presets.py
```

This displays:
- Expected LED count for each preset
- Grid positions (x, y coordinates)
- Color assignments (red=2, green=6, white=1)
- Direction flags (n/e/s/w/u/d)
- Function flags (f/w/i)
- JavaScript snippets for MCP testing

### 2. Execute Interactive Tests

Follow the step-by-step guide in `test_led_presets_interactive.md`:

```markdown
1. Open LED Strip tab in configurator
2. Execute JavaScript test snippets via MCP Chrome DevTools
3. Verify LED count, colors, and positions
4. Take screenshots
5. Compare with expected results
```

### 3. Document Results

Update `LED_STRIP_PRESET_TEST_REPORT.md` with:
- Test execution date
- Pass/fail status for each preset
- Screenshots
- Any issues found

---

## Test Coverage

### What These Tests Verify

✅ **UI Functionality:**
- Preset buttons are clickable
- Grid cells update when preset is applied
- LED count displayed correctly
- Colors assigned correctly

✅ **Preset Definitions:**
- X-frame: 10 red (left), 10 green (right) on diagonal arms
- Cross-frame: 5 red (left), 5 green (right), 10 white (front/back)
- Wing: 11 red (port), 9 green (starboard) in 2 rows

✅ **Grid Layout:**
- LEDs placed at correct x,y positions
- Direction indicators applied (n/e/s/w/u/d)
- Function flags applied (f=FlightMode, w=Warnings, i=Indicator)

### What These Tests Don't Cover

❌ **Backend State:**
- FC.LED_STRIP array contents (internal JavaScript state)
- MSP message encoding when saved
- Settings persistence across sessions

❌ **Hardware Behavior:**
- Actual LED strip behavior
- Color rendering on physical LEDs
- Timing and effects

❌ **Edge Cases:**
- Applying preset with existing LEDs
- Undo (Ctrl+Z) functionality
- Rapid preset switching
- Save/load behavior

---

## Aviation Navigation Light Standards

The presets follow aviation navigation light conventions:

**Port (Left) Side:** Red
- Helps other aircraft determine your orientation
- Visible from the left side

**Starboard (Right) Side:** Green
- Helps other aircraft determine your orientation
- Visible from the right side

**Front/Rear:** White (for crossframe)
- Indicates direction of travel

This standard applies to:
- Aircraft (fixed-wing and rotary)
- Boats and ships
- Some ground vehicles

---

## Preset Specifications

### X-Frame Quadcopter

**Description:** Diagonal arm configuration (racing/freestyle quad)

**LED Count:** 20 (5 per arm)

**Layout:**
```
        Front
    NW       NE
     \      /
      \    /
       \  /
        \/
        /\
       /  \
      /    \
     /      \
    SW       SE
        Rear
```

**Colors:**
- Left arms (NW, SW): Red (color 2) - 10 LEDs
- Right arms (NE, SE): Green (color 6) - 10 LEDs

**Arm Details:**
- Front-left (NW): Wires 0-4, positions (2,2) to (6,6)
- Front-right (NE): Wires 5-9, positions (13,2) to (9,6)
- Back-left (SW): Wires 10-14, positions (2,13) to (6,9)
- Back-right (SE): Wires 15-19, positions (13,13) to (9,9)

### Cross-Frame Quadcopter

**Description:** + pattern arm configuration (AP/cinematic quad)

**LED Count:** 20 (5 per arm)

**Layout:**
```
        N
        |
        |
    W---+---E
        |
        |
        S
```

**Colors:**
- Front arm (N): White (color 1) - 5 LEDs
- Right arm (E): Green (color 6) - 5 LEDs
- Back arm (S): White (color 1) - 5 LEDs
- Left arm (W): Red (color 2) - 5 LEDs

**Arm Details:**
- Front (N): Wires 0-4, positions (7,2) to (7,6)
- Right (E): Wires 5-9, positions (9,7) to (13,7)
- Back (S): Wires 10-14, positions (8,9) to (8,13)
- Left (W): Wires 15-19, positions (2,8) to (6,8)

### Fixed-Wing Aircraft

**Description:** Two horizontal rows along wing span

**LED Count:** 20 (10 per row)

**Layout:**
```
Row 1 (y=7):  RED RED RED RED RED RED | GRN GRN GRN GRN
                    Port (left)        |  Starboard (right)

Row 2 (y=9):       RED RED RED RED RED | GRN GRN GRN GRN GRN
                    Port (left)        |  Starboard (right)
```

**Colors:**
- Port (left) half: Red (color 2) - 11 LEDs
- Starboard (right) half: Green (color 6) - 9 LEDs

**Row Details:**
- Row 1: Wires 0-9, y=7, x=0-9
  - Left 6 LEDs: Red (x=0-5)
  - Right 4 LEDs: Green (x=6-9)
- Row 2: Wires 10-19, y=9, x=6-15
  - Left 5 LEDs: Red (x=6-10)
  - Right 5 LEDs: Green (x=11-15)

---

## Understanding the Data

### Grid Coordinates

The LED grid is 16×16 (x=0-15, y=0-15):
- **x=0** is left edge
- **x=15** is right edge
- **y=0** is top edge
- **y=15** is bottom edge

**Grid index calculation:**
```
gridIndex = y * 16 + x
```

Example: Position (7, 3) = grid index 55

### Color Codes

INAV uses color indexes 0-15:
- **0** = Black (off)
- **1** = White
- **2** = Red
- **3** = Orange
- **4** = Yellow
- **5** = Lime Green
- **6** = Green
- **7** = Mint Green
- **8** = Cyan
- **9** = Light Blue
- **10** = Blue
- **11** = Dark Violet
- **12** = Magenta
- **13** = Deep Pink
- **14** = Black (custom)
- **15** = Black (custom)

### Direction Flags

- **n** = North (forward)
- **e** = East (right)
- **s** = South (rear)
- **w** = West (left)
- **u** = Up
- **d** = Down

LEDs can have multiple direction flags (e.g., "nw" = northwest)

### Function Flags

- **f** = Flight Mode (changes color based on flight mode)
- **w** = Warnings (blinks on warnings)
- **i** = Indicator (shows status)
- **c** = Color (static color)
- **a** = Armed state
- **r** = Ring (circular pattern)
- **l** = Battery level
- **s** = RSSI level
- **g** = GPS status
- **b** = Blink always
- **o** = Larson scanner
- **n** = Blink on landing
- **t** = Throttle hue
- **h** = Channel
- **e** = Strobe

Common combinations:
- **"fwi"** = Flight mode + warnings + indicator (corner LEDs)
- **"fw"** = Flight mode + warnings (edge LEDs)
- **"f"** = Flight mode only (middle LEDs)

---

## Troubleshooting

### Test Script Issues

**Problem:** Python script won't run
**Solution:**
```bash
chmod +x test_led_strip_presets.py
python3 test_led_strip_presets.py
```

**Problem:** Missing modules
**Solution:** Script has no dependencies (uses only standard library)

### MCP Testing Issues

**Problem:** Can't connect to configurator
**Solution:**
1. Ensure configurator is running
2. Check Chrome DevTools is enabled
3. Verify MCP server is connected
4. Try refreshing configurator

**Problem:** Preset button not found
**Solution:**
1. Navigate to LED Strip tab first
2. Take snapshot to get current UIDs
3. Verify tab is fully loaded
4. Check button selector: `button.quickLayout[data-layout="xframe"]`

**Problem:** LED count is wrong
**Solution:**
1. Clear grid first (Clear All button)
2. Wait for preset to fully apply (500ms delay)
3. Check for JavaScript errors in console

### Visual Issues

**Problem:** Colors look wrong
**Solution:**
1. Verify CSS color definitions in led_strip.css
2. Check custom palette colors (Edit Palette button)
3. Take screenshot and compare with expected

**Problem:** Layout doesn't match
**Solution:**
1. Check grid coordinates in console
2. Verify x,y positions match preset definition
3. Use wire numbers to trace LED positions

---

## Adding New Tests

To add tests for new presets:

1. **Add preset definition** to `test_led_strip_presets.py`:
   ```python
   PRESETS["new_preset"] = {
       "led_count": 16,
       "description": "Description here",
       "leds": [
           {"x": 0, "y": 0, "directions": "n", "functions": "f", "color": 2},
           # ... more LEDs
       ]
   }
   ```

2. **Update interactive guide** with new test steps

3. **Add expected results** to test report template

4. **Update this README** with new preset specifications

---

## Related Documentation

**Configurator Code:**
- `inav-configurator/tabs/led_strip_presets.js` - Preset definitions
- `inav-configurator/tabs/led_strip.js` - LED Strip tab implementation
- `inav-configurator/tabs/led_strip.html` - LED Strip tab UI
- `inav-configurator/src/css/tabs/led_strip.css` - LED Strip styles

**INAV Firmware:**
- `inav/src/main/io/ledstrip.h` - LED strip definitions
- `inav/src/main/io/ledstrip.c` - LED strip implementation

**Testing Guides:**
- `claude/developer/docs/testing/chrome-devtools-mcp.md` - MCP testing guide
- `claude/developer/docs/testing/configurator-automated-testing.md` - Configurator test automation

**MCP Tools:**
- MCP Chrome DevTools server (for UI testing)
- mspapi2 (for MSP/CLI testing)

---

## Test Execution Summary

**Created:** 2026-01-28
**Status:** Test scripts ready, execution pending
**Next Steps:**
1. Execute tests via MCP Chrome DevTools
2. Document results in test report
3. Take screenshots for visual verification
4. Consider adding SITL/MSP tests for backend validation

**Test Engineer Notes:**
All test artifacts are ready. The parent session or user can now execute the tests using the MCP Chrome DevTools interface following the interactive guide.
