# Guidance: Reminder - Run docs script when configuration settings change

**Date:** 2026-02-14 09:00 | **From:** Manager | **To:** Developer

## Guidance

When adding or modifying INAV settings in settings.yaml, you must run the documentation generation script afterwards to update the settings documentation.

**What to do after modifying settings.yaml:**

1. Run the documentation generation script (typically located in the tools/ or scripts/ directory)
2. Verify the generated docs are updated
3. Include any doc changes in your PR

This ensures the INAV settings documentation stays in sync with the actual firmware settings.

---
**Manager**
