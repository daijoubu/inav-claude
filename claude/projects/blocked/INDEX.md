# Blocked Projects Index

Projects waiting on external dependencies and cannot progress without resolution.

**Last Updated:** 2026-02-12
**Total Blocked:** 2

> **Active projects:** See [../INDEX.md](../INDEX.md)
> **Backburner projects:** See [../backburner/INDEX.md](../backburner/INDEX.md)
> **Completed projects:** See [../completed/INDEX.md](../completed/INDEX.md)

---

## Blocked Status

🚫 **BLOCKED** - Project waiting on external dependency:
- User bug reproduction
- Hardware availability
- External library/upstream dependency
- Third-party collaboration

---

## Blocked Projects

### 🚫 esc-passthrough-bluejay-am32

**Status:** BLOCKED | **Type:** Bug Fix / Feature Parity | **Priority:** HIGH
**Created:** 2026-01-09

ESC passthrough (4-way interface) works in Betaflight with both BLHeli32 and Bluejay/AM32 ESCs, but fails in INAV. Needs ESC passthrough protocol analysis and fix.

**Directory:** `blocked/esc-passthrough-bluejay-am32/`
**Blocking Issue:** ESC protocol analysis needed, hardware testing required

---

### 🚫 implement-3d-hardware-acceleration-auto-fallback

**Status:** BLOCKED | **Type:** Feature Enhancement / Error Handling | **Priority:** MEDIUM
**Created:** 2025-12-26

Implement automatic fallback when 3D hardware acceleration fails, instead of crashing or showing blank screen.

**Directory:** `blocked/implement-3d-hardware-acceleration-auto-fallback/`
**Blocking Issue:** Requires platform-specific testing across Windows, macOS, Linux; waiting on volunteer testers

---

## Summary

- **Total Blocked:** 2
- **By Priority:**
  - HIGH: 1 (esc-passthrough-bluejay-am32)
  - MEDIUM: 1 (implement-3d-hardware-acceleration-auto-fallback)
