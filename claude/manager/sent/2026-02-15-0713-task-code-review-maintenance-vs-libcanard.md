# Task Assignment: Code Review - maintenance-10.0 vs add-libcanard Branches

**Date:** 2026-02-15 07:13 | **From:** Manager | **To:** Developer | **Priority:** MEDIUM
**Project:** code-review-maintenance-10-vs-libcanard
**Estimated Effort:** 6-8 hours

## Task

Perform a comprehensive code review comparing the `maintenance-10.0` and `add-libcanard` branches. Focus on understanding the libcanard integration, architectural impact, code quality, and compatibility.

**Important:** Exclude generated DSDL files and build artifacts from the review.

## Background

The `add-libcanard` branch introduces libcanard (a lightweight DroneCAN protocol stack) into INAV. This review will help us understand:
- What changes were made
- How libcanard is integrated
- Any architectural concerns
- Code quality assessment
- Compatibility and breaking changes

## What to Do

**Phase 1: Setup & Analysis (0.5 hours)**
1. Fetch both branches: `maintenance-10.0` and `add-libcanard`
2. Generate diff statistics excluding build artifacts and DSDL files
3. Categorize changes (new files, modified, deleted)
4. Identify high-impact files

**Phase 2: Architecture Review (1.5 hours)**
1. Understand how libcanard is integrated into INAV
2. Review build system changes (CMakeLists.txt)
3. Identify new CAN/DroneCAN driver code
4. Map integration points

**Phase 3: Detailed Code Review (4 hours)**
1. Review each new file completely
2. Review changes to existing files
3. Check against INAV coding standards (`claude/developer/guides/coding-standards.md`)
4. Categorize findings by severity (Critical/Major/Minor/Good)
5. Assess code quality, error handling, memory safety

**Phase 4: Report Writing (1.5 hours)**
1. Create main review report: `code-review-maintenance-10-vs-libcanard.md`
   - Executive summary, file inventory, architecture overview
   - Critical/major/minor findings, quality assessment
   - Compatibility notes, recommendations

2. Create branch summary: `branch-changes-summary.md`
   - What libcanard adds, integration strategy, key decisions

3. Create detailed analysis: `libcanard-integration-details.md`
   - File-by-file breakdown, function changes, potential issues

## Success Criteria

- [ ] All non-generated source files reviewed thoroughly
- [ ] DSDL generated files confirmed excluded
- [ ] File inventory complete (new/modified/deleted)
- [ ] Architecture changes understood and documented
- [ ] Code quality assessment completed
- [ ] All findings categorized by severity
- [ ] Three reports generated and complete
- [ ] Recommendations provided for stakeholders

## Finding Categories

Use these severity levels when documenting issues:

- **🔴 Critical:** Security, safety, architecture, breaking changes without migration
- **🟠 Major:** Quality issues, performance regressions, compatibility problems
- **🟡 Minor:** Style deviations, documentation gaps, minor optimizations
- **🟢 Good:** Exemplary code, best practices, well-structured implementations

## Project Directory

`claude/projects/active/code-review-maintenance-10-vs-libcanard/`

**Files:**
- `summary.md` - Project overview, scope, methodology
- `todo.md` - Detailed task breakdown by phase

## References

**Coding Standards:** `claude/developer/guides/coding-standards.md`
**Code Review Agent:** Use `inav-code-review` agent for architectural assessment

## Branches

- **Base:** `maintenance-10.0`
- **Target:** `add-libcanard`
- **Exclude:** Generated DSDL files, build/ directory, auto-generated code

---

**Manager**
