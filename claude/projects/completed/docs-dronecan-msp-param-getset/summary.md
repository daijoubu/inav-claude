# Project: DroneCAN MSP Documentation — Param GetSet + Configurator Tab

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Documentation
**Created:** 2026-06-06
**Estimated Time:** 1-3 hours

## Overview

Audit and complete MSP protocol documentation for the DroneCAN param-getset feature and potentially the DroneCAN configurator tab.

## Problem

MSP documentation was missed during implementation of `feature-dronecan-param-getset` and possibly `feature-dronecan-configurator-tab`. Before these PRs open, the MSP message definitions and protocol details should be documented so reviewers and users understand the wire format.

## Objectives

1. Identify which MSP messages in the DroneCAN param-getset and configurator-tab features lack documentation
2. Write or update documentation to cover the missing entries
3. Verify existing documentation is accurate against the implementation

## Scope

**In Scope:**
- MSP messages introduced or modified in `feature/dronecan-param-getset`
- MSP messages introduced or modified in `feature/dronecan-configurator-tab`
- Any related DroneCAN MSP messages that may be undocumented

**Out of Scope:**
- Code changes to the implementation
- Documentation for other features

## Success Criteria

- [ ] All new/modified MSP messages in param-getset are documented
- [ ] All new/modified MSP messages in configurator-tab are documented
- [ ] Documentation is accurate against the implementation
- [ ] Documentation committed to the appropriate branch(es)

## Priority Justification

These PRs are currently backburner/blocked but will need documentation in order before they can be submitted. Better to address the gap now.
