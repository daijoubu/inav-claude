# Project: Investigate DroneCAN DNA Implementation

**Status:** ✅ COMPLETED
**Priority:** MEDIUM
**Type:** Investigation
**Created:** 2026-02-14
**Completed:** 2026-02-14
**Estimated Effort:** 3-4 hours
**Actual Effort:** ~45 min

## Overview

Investigate implementing DroneCAN DNA (Dynamic Node Allocation) feature in INAV. DNA is like DHCP for CAN bus - it automatically assigns unique node IDs to devices on the CAN network, eliminating the need for manual configuration.

## Background

DroneCAN DNA consists of two parts:
1. **Dynamic Node Allocation (DNA)** - Client-side functionality where a node requests a node ID
2. **Allocation Server** - Server that manages node ID assignments

Currently, INAV's DroneCAN implementation uses static node IDs. Adding DNA support would:
- Simplify setup for users (no manual node ID configuration)
- Prevent node ID conflicts
- Enable plug-and-play CAN device functionality

## Investigation Goals

### 1. Understand DNA Specification
- How does DroneCAN DNA work?
- What messages are involved?
- What is the state machine?
- What are the timing requirements?

### 2. Analyze Current Implementation
- What is INAV's current node ID handling?
- How are CAN nodes initialized?
- What infrastructure exists that could be reused?

### 3. Determine Implementation Requirements
- What libcanard functions are needed?
- What changes to dronecan.c/dronecan.h are needed?
- What new files/functions are needed?
- What are the UI implications?

### 4. Create Implementation Plan
- Architecture design
- File changes needed
- Step-by-step implementation approach
- Testing strategy

## Research Areas

- **DroneCAN Specification:** DNA protocol messages and state machines
- **libcanard:** Existing DNA support (if any)
- **INAV Code:** Current DroneCAN implementation
- **Other Implementations:** How other DroneCAN firmwares implement DNA

## Deliverables

A comprehensive investigation report containing:

1. **Executive Summary** - What DNA is and why it matters
2. **Technical Analysis** - How DNA works at protocol level
3. **Current State** - What's already in INAV
4. **Implementation Plan** - Step-by-step approach
5. **Risk Assessment** - Potential issues and mitigations
6. **Timeline Estimate** - Effort required

## Related

- **PR:** [#11313](https://github.com/iNavFlight/inav/pull/11313)
- **libcanard:** https://github.com/dronecan/libcanard
- **DroneCAN Spec:** https://dronecan.github.io/
- **DSDL-GUIDE.md:** `completed/dsdlc-submodule-generation/DSDL-GUIDE.md`

## Success Criteria

- [ ] Clear explanation of DroneCAN DNA
- [ ] Analysis of what already exists in INAV
- [ ] Implementation plan with specific steps
- [ ] Estimated effort and timeline
- [ ] Any potential issues identified
