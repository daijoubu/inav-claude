# Task Assignment: Investigate CAN Driver Circular Buffer

**From:** Manager
**To:** Developer
**Date:** 2026-02-14
**Priority:** MEDIUM
**Type:** Investigation
**Estimated Effort:** 2-3 hours

---

## Task

Investigate whether the STM32F7 CAN driver's circular buffer implementation can be replaced with INAV's existing circular buffer library to reduce code duplication and improve maintainability.

## Background

The STM32F7 CAN driver currently uses its own circular buffer implementation for CAN message queuing. INAV has a generic circular buffer implementation in its common library that may be suitable for this purpose. We want to understand if switching makes sense.

## Questions to Answer

### 1. Where is the CAN driver's circular buffer?
- Find the circular buffer implementation in the STM32F7 CAN driver
- Document its structure and API
- Note any CAN-specific requirements (element size, ISR usage, etc.)

### 2. Where is INAV's circular buffer library?
- Find the common circular buffer implementation (likely `common/circular_queue.c` or similar)
- Document its API and capabilities
- Check where else it's used in the codebase

### 3. Are they compatible?
Compare:
- Buffer element types (fixed size vs variable?)
- Thread safety (ISR-safe? volatile? critical sections?)
- Memory allocation (static vs dynamic?)
- API differences
- Any missing features

### 4. Should we switch?
Assess:
- **Benefits:** Code reuse, single implementation to maintain, consistency
- **Risks:** ISR timing sensitivity, battle-tested CAN code, regression potential
- **Effort:** How much work to switch?

## Deliverables

Create FINDINGS.md with:
1. Current CAN buffer implementation details
2. INAV library buffer implementation details
3. Comparison table
4. **Recommendation:** Switch / Adapt library / Keep current
5. If switching: outline implementation approach

## Project Directory

`claude/projects/active/investigate-can-circular-buffer/`

Send FINDINGS.md and completion report to Manager when done.
