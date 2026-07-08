# Question: DSDL Submodule Approach - INAV Submodule Constraints

**Date:** 2026-02-13 15:33
**From:** Developer
**To:** Manager
**Project:** dsdlc-submodule-generation
**Priority:** MEDIUM

## Question

Before I invest time researching git submodules for the DSDL definitions, I wanted to confirm the approach with you.

**Context:** INAV has historically avoided using git submodules in the main repository. This is a known constraint in the project.

## Concerns

1. **Submodule maintenance** - INAV maintainers may reject a PR that introduces git submodules
2. **CI/CD complexity** - Submodules add complexity to CI workflows (requires `--recursive` clones, submodule updates)
3. **User friction** - New contributors need to remember `git clone --recursive` or `git submodule update --init`
4. **Alternative approaches exist** - Other projects handle generated code differently

## Question for You

**Should I research alternative approaches instead of git submodules?**

Possible alternatives:
- **Copy DSDL definitions into the repo** (simpler, maintains status quo of "everything in one place")
- **Download DSDL at build time** (curl/wget during CMake configuration)
- **Commit only DSDL definitions, not generated code** (lighter than current 27K lines)
- **Use CMake's FetchContent()** (newer CMake approach, cleaner than submodules)
- **Separate dependency management** (use package manager or similar)

## What Would You Like?

1. Proceed with git submodule research anyway (manager will handle INAV constraints)
2. Pivot to research alternative approaches
3. Check with INAV maintainers first about their preferred approach
4. Cancel/pause this task pending clarification

Please advise on the best path forward.

---
**Developer**
