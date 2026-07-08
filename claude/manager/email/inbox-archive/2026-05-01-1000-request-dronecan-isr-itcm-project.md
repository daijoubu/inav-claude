# Project Creation Request: DroneCAN TX/RX ISR Migration and ITCM Usage

**Date:** 2026-05-01 10:00
**From:** Developer
**To:** Manager
**Type:** Project Creation Request
**Re:** MATEKF765SE ITCM headroom and DroneCAN optimization

## Summary

During the MATEKF765SE build for PR #11527 (fix-pr-11527-qodo-review), ITCM_RAM came in at 88.67% utilized (14,528 of 16,384 bytes), leaving only ~1.8KB headroom. This is worth tracking and investigating proactively.

The user wants to investigate moving the DroneCAN TX and RX handlers into interrupt context (ISR). If done, those handlers would likely need to be placed in ITCM to meet the deterministic latency requirements of ISR code on the STM32F7 Cortex-M7 — which would consume some or all of that remaining headroom.

## Scope

Create a project to:

1. **Assess current ITCM usage** - Identify what's currently placed in ITCM and why
2. **Investigate DroneCAN ISR migration** - Evaluate moving DroneCAN TX/RX handlers to interrupt-driven operation
3. **Evaluate ITCM headroom impact** - Determine whether anything can be moved out to make room for ISR handlers

## Context

This project is a prerequisite or companion to the STM32F7 CAN TX ISR migration task already in the inbox. Understanding ITCM usage and constraints will inform decisions about whether ISR handlers can be placed there.

**Related PR:** #11527 (fix-pr-11527-qodo-review) - baseline ITCM measurement

## Next Steps

Please create a new active project for this investigation. Happy to start work once the project is set up.

---
**Developer**
