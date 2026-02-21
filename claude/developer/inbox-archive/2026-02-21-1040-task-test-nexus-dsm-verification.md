# Task Assignment: Test NEXUS DSM Verification

**Date:** 2026-02-21 10:40 | **From:** Manager | **To:** Developer | **Priority:** MEDIUM

## Task
Test and verify DSM satellite receiver functionality on the NEXUS target (RadioMaster Nexus Original) from PR #11324.

## Background
PR #11324 adds the NEXUS target with a dedicated DSM port on UART1 (PA9/PA10). The target defaults to CRSF on UART4, but we need to verify DSM works when properly configured. The DSM port provides 3.3V/0.5A power for satellite receivers.

## What to Do
1. Build NEXUS firmware from PR #11324
2. Flash to Nexus hardware via DFU
3. Configure UART1 for serial RX with SPEKTRUM2048 provider
4. Connect DSM satellite receiver to DSM port
5. Bind and verify channel values in Configurator
6. Document configuration steps
7. Optionally check if hardware has bind button for SPEKTRUM_BIND_PIN

## Success Criteria
- [ ] DSM satellite detected on UART1
- [ ] Channel values display correctly in Configurator
- [ ] Transmitter inputs map correctly
- [ ] No signal stability issues
- [ ] Configuration steps documented

## Estimated Effort
2-4 hours

## Project
**Name:** test-nexus-dsm-verification
**Directory:** `claude/projects/active/test-nexus-dsm-verification/`

## Related
PR #11324 (iNavFlight/inav)

---
**Manager**
