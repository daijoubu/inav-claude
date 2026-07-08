# Task Assignment: Auto Compass Orientation Detection — Feasibility Investigation

**Date:** 2026-06-08 14:00
**From:** Manager
**To:** Developer
**Project:** investigate-auto-compass-orientation
**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours

## Task

Investigate the feasibility of implementing automatic compass orientation detection in INAV, based on ArduPilot's variance-minimisation algorithm. This is a research task only — no implementation code.

## Background

You already researched ArduPilot's algorithm (`libraries/AP_Compass/CompassCalibrator.cpp`) in your 2026-06-07 project request, which is the starting point here. The algorithm records per-sample attitude snapshots during calibration, then tries every candidate orientation and picks the one that produces the lowest variance in the implied earth field. Confidence is expressed as second_best / best variance ratio.

Compass misorientation is a common user mistake that silently causes navigation failures. Auto-detection during calibration would catch it without requiring users to understand rotation matrices.

## What to Do

Answer the four feasibility questions:

1. **Memory**: Is INAV's calibration architecture compatible with recording per-sample attitude snapshots? (300 samples × ~9 bytes = ~2.7 KB RAM — is that acceptable on F4?)
2. **Rotation coverage**: Does INAV's rotation enum cover the same set of orientations as ArduPilot's, or is a mapping needed?
3. **Configurator UI**: What changes would be required to surface orientation confidence and auto-correction to the user?
4. **Worth it?**: Given flash/RAM constraints on F4 targets, is the feature viable and valuable enough to implement?

## Deliverable

Write `investigation-findings.md` in the project directory with your answers to all four questions and a clear go/no-go recommendation. If go, include a rough implementation phase breakdown and effort estimate.

## Branch

No branch needed — investigation only. If you recommend proceeding, the implementation would target `maintenance-10.x`.

## Success Criteria

- [ ] All four feasibility questions answered with supporting evidence from the codebase
- [ ] `investigation-findings.md` written in project directory
- [ ] Go/no-go recommendation stated clearly with rationale
- [ ] Completion report sent to manager

## Project Directory

`claude/projects/active/investigate-auto-compass-orientation/`

---
**Manager**
