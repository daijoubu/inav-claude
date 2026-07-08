# Project: DroneCAN Node Transport Statistics

**Status:** ⏸️ BACKBURNER
**Priority:** MEDIUM
**Type:** Feature
**Created:** 2026-02-14
**Estimated Time:** TBD — not yet scoped in detail

## Overview

Poll DroneCAN nodes for transport statistics (TX/RX transfer counts, error rates) via `uavcan.protocol.GetTransportStats`, and expose per-node stats via CLI.

## Problem

Bus-level CAN error stats (tracked separately in `feature-canbus-errors-blackbox`) show FC-side transport health, but say nothing about individual peripheral nodes' own reported transfer/error counts. Diagnosing a specific misbehaving node currently has no per-node visibility.

## Objectives

1. Send `uavcan.protocol.GetTransportStats` requests to known nodes
2. Store and expose per-node TX/RX/error counts via a CLI command

## Scope

**In Scope:**
- `GetTransportStats` request/response handling
- Per-node stats storage (extend existing node table or a parallel structure)
- CLI display command

**Out of Scope:**
- Blackbox logging of these stats (that's the bus-level `feature-canbus-errors-blackbox` project's scope, not per-node)

## Success Criteria

- [ ] `GetTransportStats` requests sent and responses parsed
- [ ] Per-node stats retrievable via CLI
- [ ] Full build matrix passes (F4, F7, H7, AT32, SITL)
- [ ] Draft PR opened against `maintenance-10.x`

## Priority Justification

Complements `feature-canbus-errors-blackbox` with per-node granularity, but not urgent — deprioritized behind higher-priority DroneCAN work.

## Dependencies

Complements `feature-canbus-errors-blackbox` (bus-level stats); no hard blocking dependency. Not yet assigned or discussed with developer beyond this outline — backfilled 2026-07-07 from the INDEX.md description to give this project actual doc files (previously just an empty directory).
