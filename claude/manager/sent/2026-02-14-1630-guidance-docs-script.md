# Guidance: Run Docs Script When Configuration Settings Change

**Date:** 2026-02-14 16:30 | **From:** Manager | **To:** Developer | **Type:** GUIDANCE

## Summary

When adding or modifying INAV settings in `settings.yaml`, you must run the documentation generation script afterwards to update the settings documentation.

## What to Do After Modifying settings.yaml

1. Run the documentation generation script (typically located in the `tools/` or `scripts/` directory)
2. Verify the generated docs are updated
3. Include any doc changes in your PR

## Why This Matters

This ensures the INAV settings documentation stays in sync with the actual firmware settings. Outdated documentation can confuse users and lead to support issues.

---
**Manager**
