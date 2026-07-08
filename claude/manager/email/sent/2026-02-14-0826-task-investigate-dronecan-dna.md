# Task Assignment: Investigate DroneCAN DNA Implementation

**Date:** 2026-02-14 08:26
**From:** Manager
**To:** Developer
**Project:** investigate-dronecan-dna
**Priority:** MEDIUM
**Estimated Effort:** 8-16 hours (investigation phase)

## Task

Investigate implementing DroneCAN DNA (Dynamic Node Allocation) in INAV. DNA is like DHCP for CAN bus - it automatically assigns unique node IDs to devices on the CAN network, eliminating manual configuration.

## Background

DroneCAN DNA (Dynamic Node Allocation) is a protocol feature that automatically assigns unique node IDs to devices on the CAN network. This simplifies setup and prevents ID conflicts. We need to understand:
- How DNA works at the protocol level
- What libcanard provides
- What changes would be needed in INAV

## What to Do

### Phase 1: Understand DNA Specification
- Research DroneCAN DNA protocol (messages, state machine, timing)
- Check if libcanard has DNA implementation

### Phase 2: Analyze Current Implementation
- Review dronecan.c and dronecan.h
- Search for existing DNA-related code
- Check DSDL files for dynamic_node_id messages

### Phase 3: Determine Implementation Requirements
- Identify required changes to INAV
- Analyze UI implications

### Phase 4: Create Implementation Plan
- Document architecture
- Create step-by-step plan
- Estimate timeline and risks

### Phase 5: Document Findings
- Write investigation report in project directory
- Submit completion report

## Deliverables

A comprehensive investigation report with:
1. Executive Summary - What DNA is and why it matters
2. Technical Analysis - How DNA works at protocol level
3. Current State - What's already in INAV
4. Implementation Plan - Step-by-step approach
5. Risk Assessment - Potential issues and mitigations
6. Timeline Estimate - Effort required

## Success Criteria

- [ ] Clear explanation of DroneCAN DNA
- [ ] Analysis of what already exists in INAV
- [ ] Implementation plan with specific steps
- [ ] Estimated effort and timeline
- [ ] Any potential issues identified

## Project Directory

`claude/projects/active/investigate-dronecan-dna/`

## Base Branch

`maintenance-9.x` (INAV firmware)

---
**Manager**
