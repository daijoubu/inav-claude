# Todo: Code Review - maintenance-10.0 vs add-libcanard

## Phase 1: Setup & Diff Analysis (0.5 hours)

### Repository Setup
- [ ] Ensure both branches are fetched and current
  - [ ] `git fetch origin maintenance-10.0`
  - [ ] `git fetch origin add-libcanard`
  - [ ] Verify branches exist locally

### Generate Diff (Excluding DSDL)
- [ ] Create git diff command to exclude generated files
  - [ ] Exclude build/ directory
  - [ ] Exclude auto-generated code
  - [ ] Exclude .pdf and binary files
  - [ ] Run: `git diff maintenance-10.0...add-libcanard --stat`

### Categorize Changes
- [ ] Count files by type:
  - [ ] New files added
  - [ ] Files modified
  - [ ] Files deleted
  - [ ] Files renamed

- [ ] Identify change magnitude:
  - [ ] Lines added/removed per file
  - [ ] High-impact files (>500 line changes)
  - [ ] Medium-impact files (50-500 lines)
  - [ ] Low-impact files (<50 lines)

### Create Change Inventory
- [ ] Document all files with substantial changes
- [ ] Note file purposes (driver, utility, test, etc.)
- [ ] Flag files for detailed review

---

## Phase 2: Architecture Review (1.5 hours)

### Understand Libcanard Integration
- [ ] Identify where libcanard is integrated
  - [ ] New libcanard-specific files/directories
  - [ ] What subsystems use libcanard?
  - [ ] What does it replace or supplement?

- [ ] Review high-level architecture
  - [ ] CAN driver abstraction layer changes
  - [ ] DroneCAN protocol changes
  - [ ] Integration points with INAV

### Build System Changes
- [ ] Review CMakeLists.txt modifications
  - [ ] New source files included
  - [ ] Removed source files
  - [ ] New compiler flags or dependencies
  - [ ] Changes to include paths

- [ ] Check for new external dependencies
  - [ ] Where is libcanard source?
  - [ ] How is it built/linked?
  - [ ] Version information

### Key Files Review
- [ ] Identify critical files for deep review:
  - [ ] New CAN/DroneCAN drivers
  - [ ] Abstraction layers
  - [ ] Integration headers
  - [ ] Configuration files

### Architecture Summary
- [ ] Document how libcanard fits into INAV
- [ ] Note major architectural decisions
- [ ] Identify potential concerns

---

## Phase 3: Detailed Code Review (4 hours)

### New Files (2 hours)
- [ ] Review each new file completely
  - [ ] Purpose and responsibility
  - [ ] Integration with existing code
  - [ ] Code quality assessment
  - [ ] Error handling
  - [ ] Documentation/comments

- [ ] For each new file, check:
  - [ ] Follows coding standards
  - [ ] Proper header comments
  - [ ] Error conditions handled
  - [ ] Memory management (allocation/deallocation)
  - [ ] Thread safety (if applicable)
  - [ ] Performance implications

### Modified Files (1.5 hours)
- [ ] Review changes to existing files
  - [ ] Why was each change made?
  - [ ] Impact on existing functionality
  - [ ] Compatibility with rest of codebase
  - [ ] Breaking changes?

- [ ] Check critical areas:
  - [ ] Initialization code
  - [ ] Message handling
  - [ ] Error paths
  - [ ] State management

### Deleted/Deprecated Files (0.5 hours)
- [ ] Understand what was removed
  - [ ] Why was it removed?
  - [ ] What replaces it?
  - [ ] Migration path for existing code?

### Categorize Findings
- [ ] Severity categories:
  - [ ] 🔴 Critical (safety, security, architecture)
  - [ ] 🟠 Major (quality, compatibility, performance)
  - [ ] 🟡 Minor (style, documentation)
  - [ ] 🟢 Good (exemplary code, best practices)

---

## Phase 4: Specialized Reviews

### Code Quality Assessment (1 hour)
- [ ] Check against coding standards
  - [ ] File/function size limits
  - [ ] Naming conventions
  - [ ] Comment quality (WHY not WHAT)
  - [ ] Error handling patterns

- [ ] Review for common issues:
  - [ ] Null pointer dereferences
  - [ ] Buffer overflows
  - [ ] Memory leaks
  - [ ] Race conditions (if multi-threaded)

- [ ] Performance assessment:
  - [ ] Any performance regressions?
  - [ ] Memory footprint changes
  - [ ] CPU usage implications

### Compatibility Check (0.5 hours)
- [ ] Breaking changes?
  - [ ] API changes
  - [ ] Settings/CLI changes
  - [ ] Configuration format changes
  - [ ] Default behavior changes

- [ ] Migration path?
  - [ ] How do users transition?
  - [ ] Are there backwards-compatibility shims?
  - [ ] Documentation of breaking changes?

### Testing Coverage (0.5 hours)
- [ ] New tests added?
  - [ ] Unit tests
  - [ ] Integration tests
  - [ ] SITL tests
  - [ ] HITL tests

- [ ] Test adequacy?
  - [ ] Error cases covered?
  - [ ] Edge cases tested?
  - [ ] Performance tested?

---

## Phase 5: Report Writing (1.5 hours)

### Main Review Report
- [ ] Create `code-review-maintenance-10-vs-libcanard.md`
  - [ ] Executive summary (1 page)
  - [ ] File inventory (1 page)
  - [ ] Architecture overview (2 pages)
  - [ ] Critical findings (1+ pages)
  - [ ] Major findings (1+ pages)
  - [ ] Minor findings (reference table)
  - [ ] Quality assessment (1 page)
  - [ ] Compatibility notes (0.5 page)
  - [ ] Recommendations (0.5 page)

### Branch Changes Summary
- [ ] Create `branch-changes-summary.md`
  - [ ] What is libcanard?
  - [ ] Why was it added?
  - [ ] What does it provide?
  - [ ] Key integration points
  - [ ] File structure overview

### Detailed Findings
- [ ] Create `libcanard-integration-details.md`
  - [ ] File-by-file analysis
  - [ ] Function/API changes
  - [ ] New abstractions
  - [ ] Integration architecture
  - [ ] Potential issues with details

### Compile Statistics
- [ ] Files added/modified/deleted counts
- [ ] Lines of code added/removed
- [ ] Files by impact category
- [ ] Issues found by severity

---

## Completion Checklist

### Quality Assurance
- [ ] All non-DSDL files reviewed
- [ ] No generated files included
- [ ] Findings categorized correctly
- [ ] Recommendations are actionable

### Documentation
- [ ] Main report complete and thorough
- [ ] Summary report easy to understand
- [ ] Detailed findings reference lines/files
- [ ] All findings have rationale

### Review Standards
- [ ] Applied INAV coding standards
- [ ] Referenced architecture documentation
- [ ] Checked against best practices
- [ ] Severity levels consistent

### Reporting
- [ ] All three reports generated
- [ ] Reports saved to `claude/developer/reports/`
- [ ] Report references accurate
- [ ] Completion report ready

### Final Steps
- [ ] Review complete and thorough
- [ ] No major issues unidentified
- [ ] Recommendations clear and actionable
- [ ] Ready for stakeholder presentation
