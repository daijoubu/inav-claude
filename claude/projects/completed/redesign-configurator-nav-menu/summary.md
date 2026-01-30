# Project: Redesign Configurator Navigation Menu

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** UX Design / Mockup
**Created:** 2026-01-20
**Assignment:** 📝 Planned
**Estimated Time:** 3-4 hours

## Overview

Design three alternative UI mockups for the inav-configurator's left-side navigation menu to address the current menu being too long and clunky with 24+ items in a single vertical list.

## Problem

The current navigation menu in inav-configurator has grown to 24+ tabs in a single vertical list:
- Status, Calibration, Mixer, Outputs, Ports, Configuration, Failsafe, Tuning, Advanced Tuning, Programming, JavaScript Programming, Receiver, Modes, Adjustments, GPS, Alignment Tool, Mission Control, OSD, LED Strip, Sensors, Tethered Logging, Blackbox, CLI, Search

**Issues:**
- Long scrolling list is clunky to navigate
- No logical grouping or hierarchy
- Takes up significant vertical space
- Difficult to find specific tabs quickly
- Poor visual organization

## Objectives

1. Analyze current navigation structure and usage patterns
2. Identify logical groupings of tabs (e.g., Setup, Tuning, Sensors, Advanced, etc.)
3. Create **three distinct mockup approaches** for improved navigation
4. Each mockup should demonstrate different UI paradigms
5. Provide rationale for each design approach
6. Recommend preferred option with pros/cons analysis

## Scope

**In Scope:**
- Design exploration and mockups (HTML/CSS prototypes or visual mockups)
- Three different UI approaches (see suggestions below)
- Logical grouping of tabs
- User experience analysis
- Recommendations document

**Out of Scope:**
- Full implementation (this is mockup/design phase only)
- Backend refactoring
- Tab functionality changes (only navigation structure)
- User testing (can be recommended for later)

## Suggested Mockup Approaches

### Option 1: Collapsible/Accordion Groups
Group related tabs under collapsible sections:
- **Setup** (Status, Calibration, Alignment Tool, Configuration, Ports)
- **Flight Control** (Mixer, Outputs, Receiver, Modes, Failsafe)
- **Tuning** (Tuning, Advanced Tuning, Adjustments)
- **Navigation** (GPS, Mission Control)
- **Sensors & Peripherals** (Sensors, OSD, LED Strip, Blackbox, Tethered Logging)
- **Programming** (Programming, JavaScript Programming)
- **Tools** (CLI, Search)

### Option 2: Tabbed Categories
Top-level tabs with sub-navigation:
- Main categories across the top or as tabs
- Subitems appear in secondary navigation area

### Option 3: Hybrid Sidebar + Top Navigation
- Most common items in sidebar (collapsed by default)
- Category switcher at top
- Contextual navigation based on category

**Note:** These are suggestions - developer should explore and may propose different approaches.

## Implementation Steps

1. **Research Phase**
   - Review all 24 current tabs and their purposes
   - Identify logical groupings (initial setup, flight tuning, advanced features, etc.)
   - Research common navigation patterns in similar applications
   - Consider user workflows (beginner vs advanced users)

2. **Design Phase**
   - Create three distinct mockup approaches
   - Each mockup should be:
     - Visually different (not just variations on same theme)
     - Address the "long list" problem
     - Maintain accessibility to all tabs
     - Consider mobile/responsive needs (if applicable)
   - Use HTML/CSS for interactive prototypes OR visual design tools

3. **Documentation Phase**
   - Document each design approach
   - Provide rationale for groupings
   - List pros and cons for each approach
   - Recommend preferred option with justification
   - Consider implementation complexity

4. **Review Phase**
   - Present mockups for feedback
   - Identify any missing considerations
   - Refine recommendation

## Success Criteria

- [ ] All 24 tabs analyzed and categorized
- [ ] Logical groupings identified and documented
- [ ] Three distinct mockup approaches created
- [ ] Each mockup demonstrates different UI paradigm
- [ ] Mockups are visual/interactive (HTML/CSS or design files)
- [ ] Pros/cons analysis for each approach
- [ ] Recommendation provided with rationale
- [ ] Documentation includes implementation considerations
- [ ] User workflow considerations documented

## Deliverables

1. **Mockups** (HTML/CSS prototypes or design files)
   - Mockup Option 1: [approach name]
   - Mockup Option 2: [approach name]
   - Mockup Option 3: [approach name]

2. **Documentation**
   - Tab categorization analysis
   - Design rationale for each option
   - Pros/cons comparison table
   - Recommendation with justification
   - Implementation complexity assessment

3. **Files Location**
   - Save mockups to: `claude/developer/workspace/redesign-configurator-nav-menu/mockups/`
   - Save documentation to: `claude/developer/workspace/redesign-configurator-nav-menu/design-proposal.md`

## Design Considerations

**User Types:**
- Beginners: Need clear, simple navigation to setup essentials
- Advanced users: Need quick access to tuning and advanced features
- Occasional users: Need to find features quickly without memorization

**Workflow Patterns:**
- Initial setup: Status → Calibration → Configuration → Receiver → Modes
- Pre-flight checks: Status → Failsafe → GPS
- Tuning sessions: Tuning → Advanced Tuning → Adjustments
- Advanced features: Programming, Mission Control, etc.

**Technical Constraints:**
- Must work with Electron framework
- Should be responsive (if configurator supports different window sizes)
- Maintain current dark theme aesthetic
- Keep icon usage consistent

## Current Navigation Structure

From the screenshot provided:
```
☁ Status (currently selected)
⚙ Calibration
🎛 Mixer
📊 Outputs
🔌 Ports
⚙ Configuration
⚠ Failsafe
🎚 Tuning
📈 Advanced Tuning
⚙ Programming
📝 JavaScript Programming
📡 Receiver
🎛 Modes
🎚 Adjustments
📍 GPS
🧭 Alignment Tool
🗺 Mission Control
📺 OSD
💡 LED Strip
📊 Sensors
🔗 Tethered Logging
📦 Blackbox
💻 CLI
🔍 Search
```

## Priority Justification

MEDIUM: This is a UX improvement that would enhance user experience but doesn't block functionality. The current navigation works but is not optimal. This is design/mockup work, so it's not as urgent as bug fixes but valuable for long-term usability.

## References

- **Current UI:** See provided screenshot
- **Repository:** inav-configurator
- **UI Framework:** Electron with HTML/CSS/JavaScript
- **Design Files:** TBD (developer to create)

## Notes

- This is a **design exploration phase** - no implementation required yet
- Focus on **three distinct approaches** not minor variations
- Consider both **beginner and advanced user workflows**
- Mock-ups should be **visual/interactive** enough to evaluate UX
- If developer has better ideas than suggestions, explore them!
