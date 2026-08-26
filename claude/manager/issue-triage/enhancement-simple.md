# Simple Enhancements

Feature additions that are relatively straightforward to implement.

---

## Issues

### #11216 - Include APA parameters in Adjustments tab

**Created:** 2024-12-20
**Labels:** enhancement
**URL:** https://github.com/iNavFlight/inav/issues/11216

**Problem:**
APA (Airplane Pitch Adjustment?) parameters are not accessible in the Adjustments tab of the configurator.

**What's Needed:**
- Add UI elements to Adjustments tab
- Configurator-side change

**Notes:**
UI addition to configurator, no firmware changes needed.

---

### inav-configurator #2670 - Virtual pitot sensor enabled by default for new copters

**Created:** 2026-07-01
**Labels:** (none)
**URL:** https://github.com/iNavFlight/inav-configurator/issues/2670

**Problem:** New multirotor setups get the virtual pitot sensor enabled by default; reporter routinely disables it and questions whether it's actually needed for quadcopters.

**What's Needed:** Review/change the default `pitot_hardware` (or wizard preset) for the multirotor setup path in the configurator, or document why it defaults on.

**Notes:** Small, contained change once the maintainers decide the right default. **2026-08-11:** confirmed firmware's own `pitot_hardware` default is `NONE` — the VIRTUAL default comes from the configurator's setup wizard specifically, so the fix (if any) is configurator-side only.

**Assigned:** `active/investigate-virtual-pitot-default/`

---

### inav-configurator #2658 - Hardcoded English UI text in redesigned LED Strip tab

**Created:** 2026-06-12
**Labels:** Enhancement
**URL:** https://github.com/iNavFlight/inav-configurator/issues/2658

**Problem:** The redesigned LED Strip tab (`tabs/led_strip.html`) has hardcoded English strings ("Quick Presets", step headers/instructions, preset button labels, "/ 128 placed", "Edit palette colors") with no i18n keys, so they can't be localized.

**What's Needed:** Add i18n keys for the listed strings and update locale files.

**Notes:** Reporter self-tracked this in June ("will fix when I have time and after 9.1 is locked") but two months on it's still open. Claimed as an active project — see `claude/projects/active/fix-configurator-led-strip-i18n/`. Assigned to Developer 2026-08-10, with an explicit note to check whether the original reporter has already started work before duplicating it.

**Assigned:** fix-configurator-led-strip-i18n

---

### #10754 - Add support for W25N02K flash

**Created:** 2024-10-01
**Labels:** enhancement
**URL:** https://github.com/iNavFlight/inav/issues/10754

**Problem:**
The W25N02K flash chip is not supported for blackbox logging.

**What's Needed:**
- Add flash chip identification
- Configure chip parameters (size, page size, etc.)

**Notes:**
Flash chip support addition. Similar to previous flash chip additions.
