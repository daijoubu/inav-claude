# Project: Redesign LED Strip UI

**Status:** ✅ COMPLETED (Draft PR - Awaiting Manual Testing)
**Priority:** MEDIUM
**Type:** UI/UX Design
**Created:** 2026-01-26
**Completed:** 2026-01-29
**Actual Effort:** 8-10 hours (design + implementation)

## Overview

Design four different UI proposals for the LED Strip tab in INAV Configurator, starting with fresh perspective then improving existing interface.

## Problem

The current LED Strip tab in inav-configurator is **very unintuitive**:
- Users need to do "wire ordering mode" near the bottom of the screen BEFORE they can do items above
- If they click on an LED to set its color, it clears the work they did in wiring order mode
- Unless they first choose a mode over on the right side
- Workflow is confusing and error-prone

## Objectives

Create **four UI proposals** in this specific order:

### 1. Fresh Perspective (without looking at existing UI)
- Read `inav/docs/LedStrip.md` to understand features
- Design UI from scratch based purely on requirements
- **Do NOT look at the existing configurator UI yet**

### 2. Improve Existing UI (approach 1)
- **NOW look at the existing LED Strip tab**
- Propose reorganization/improvements to existing interface
- Keep the same general structure but fix workflow issues

### 3. Improve Existing UI (approach 2)
- Alternative reorganization/improvement to existing interface
- Different approach from #2
- Still based on existing structure

### 4. Fresh Design (informed by existing)
- Completely different UI design
- Now that you've seen the existing one, design something better
- Not constrained by existing structure

## Requirements

**Read first:**
- `inav/docs/LedStrip.md` - LED strip feature documentation
- URL: https://github.com/iNavFlight/inav/blob/master/docs/LedStrip.md

**Then examine (ONLY after Proposal 1):**
- `inav-configurator` LED Strip tab
- Current UI implementation
- Workflow and interaction patterns

## Key Features to Support

From `LedStrip.md`:
- LED positioning on the craft
- Color configuration
- Functions (GPS, warnings, flight mode, etc.)
- Wire ordering
- Color modes and overlays
- Directions (North, East, South, West, Up, Down)

## Workflow Steps

**IMPORTANT: Follow this order exactly:**

1. **Read documentation**
   - Read `inav/docs/LedStrip.md` thoroughly
   - Understand all LED strip features
   - Note key user tasks

2. **Create Proposal 1 (Fresh)**
   - Design UI without seeing existing configurator
   - Focus on intuitive workflow
   - **Stop here - do NOT look at configurator yet**

3. **Examine existing UI**
   - Open inav-configurator LED Strip tab
   - Document current workflow
   - Identify pain points

4. **Create Proposals 2 & 3 (Improvements)**
   - Two different approaches to improve existing UI
   - Fix workflow issues (wire ordering, mode selection)
   - Keep familiar structure where it works

5. **Create Proposal 4 (Fresh, Informed)**
   - New design from scratch
   - Now informed by seeing what exists
   - Address all pain points with fresh approach

## Expected Deliverables

For **each of the 4 proposals**, provide:

1. **Mockup or wireframe**
   - Can be hand-drawn sketch, ASCII art, or HTML mockup
   - Show layout and key UI elements

2. **Workflow description**
   - Step-by-step: How does a user configure LEDs?
   - Example: "User selects LED position → sets color → assigns function"

3. **Key improvements** (for Proposals 2-4)
   - What problems does this solve?
   - How is it better than current/previous proposals?

4. **Trade-offs**
   - What are the downsides?
   - Complexity vs simplicity balance

## Current Pain Points to Address

- Wire ordering must be done first, but it's at the bottom
- Clicking LEDs clears previous work unexpectedly
- Mode selection on the right isn't obvious
- Workflow order is unclear
- No clear visual indication of required steps

## Success Criteria

- [ ] `LedStrip.md` documentation read and understood
- [ ] Proposal 1 created WITHOUT looking at existing UI
- [ ] Existing LED Strip tab examined and documented
- [ ] Proposal 2 created (improvement approach 1)
- [ ] Proposal 3 created (improvement approach 2)
- [ ] Proposal 4 created (fresh design, informed)
- [ ] All 4 proposals have mockups and workflow descriptions
- [ ] Completion report sent to manager with all proposals

## Completion Details

**Proposal Selected:** Proposal 2b - Improved existing UI with numbered steps

**Implementation:**
- Removed step progress bar (cramped layout)
- Reorganized into four numbered sections with inline instructions
- Migrated from float-based to inline-block layout
- Created `tabs/led_strip_presets.js` with 3 aviation-standard presets
- Fixed clear buttons to properly remove functions/directions/colors
- Added auto-add Color function feature

**Files Changed:**
- `tabs/led_strip.html` - Restructured layout
- `tabs/led_strip.js` - Fixed functionality issues
- `src/css/tabs/led_strip.css` - Improved layout
- `tabs/led_strip_presets.js` - New preset definitions (X-Frame, Cross-Frame, Wing)

**Testing:**
- Code-level validation: ✅ Complete
- Code review: ✅ Passed (all IMPORTANT issues fixed)
- Manual testing: ⏳ Pending (PR marked as DRAFT)

**Documentation:** Added CSS best practices section to `CLAUDE.md`

## Related

- **PR:** #2543 - https://github.com/iNavFlight/inav-configurator/pull/2543
- **Branch:** `feature/led-strip-ui-redesign-2b`
- **Status:** DRAFT (awaiting manual testing)
- **Repository:** inav-configurator
- **Completion Report:** `manager/email/inbox/2026-01-29-0100-completed-led-strip-ui-redesign.md`
