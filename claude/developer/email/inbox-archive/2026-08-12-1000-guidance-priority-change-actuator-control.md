# Guidance: Priority Change — Pause feature-dronecan-led-indicator, Start feature-dronecan-actuator-control

**Date:** 2026-08-12 10:00
**From:** Manager
**To:** Developer
**Re:** DroneCAN Project Priority Update

## Guidance

Stop work on `feature-dronecan-led-indicator` (no code started yet — it's been moved to backburner, spec preserved at `claude/projects/backburner/feature-dronecan-led-indicator/`) and start `feature-dronecan-actuator-control` instead (`claude/projects/active/feature-dronecan-actuator-control/`).

## Rationale

Switching based on hardware availability — actuator-control has what's needed to work right now, LED indicator doesn't currently.

## What to Do

1. Read `claude/projects/active/feature-dronecan-actuator-control/summary.md` and `todo.md`
2. Broadcast `uavcan.equipment.actuator.ArrayCommand` from mixer servo values — first CAN-based actuator output in INAV, same new territory as `feature-dronecan-esc-control` (no code dependency between them)
3. Fail-safe behavior on CAN loss is safety-critical here (control surface could get stuck at an unsafe position on node loss) — treat that as core scope, not a follow-up
4. Check `.claude/skills/git-workflow/SKILL.md` for the current base branch before creating the work branch

## Project Directory

`claude/projects/active/feature-dronecan-actuator-control/`

---
**Manager**
