# Developer Directory Index

This document describes the organization of the `claude/developer/` workspace.

---

## Directory Structure

```
claude/developer/
│
├── CLAUDE.md                 # Developer role guide
├── README.md                 # Detailed developer documentation
├── INDEX.md                  # This file - directory organization
│
├── docs/                     # Documentation and guides (tracked in git)
│   ├── testing/              # Testing guides and results
│   ├── debugging/            # Debugging techniques and tools
│   ├── transpiler/           # Transpiler documentation
│   ├── patterns/             # Code patterns and best practices
│   └── mspapi2/              # MSP API documentation
│
├── scripts/                  # Reusable scripts (tracked in git)
│   ├── testing/              # Test scripts and utilities
│   ├── build/                # Build and flash helpers
│   └── analysis/             # Code analysis and verification tools
│
├── projects/                 # Active project working directories (GITIGNORED)
│   └── [project-name]/       # One subdirectory per active project/task
│       ├── notes.md          # Project notes
│       ├── scripts/          # Project-specific scripts
│       ├── data/             # Test data, logs
│       └── session-state.md  # Session tracking
│
├── investigations/           # Detailed technical investigations (GITIGNORED)
│   ├── crsf-telemetry/       # CRSF telemetry testing
│   ├── h743-msc/             # H743 USB MSC regression
│   ├── blueberry-pid/        # PID performance investigation
│   ├── gps/                  # GPS-related investigations
│   └── [other-topics]/       # Legacy investigation directories
│
├── work-in-progress/         # Flat working directory (GITIGNORED, legacy)
│                             # NOTE: Use projects/ for new work
│
├── reports/                  # Analysis reports (GITIGNORED)
│
├── archive/                  # Old/completed work (GITIGNORED)
│   ├── completed-tasks/      # Completed task assignments
│   ├── data/                 # Test logs, profiling data
│   └── legacy/               # Legacy scripts, old documents
│
├── builds/                   # Build artifacts (GITIGNORED)
│
└── inbox/outbox/sent/        # Email directories (GITIGNORED)
    inbox-archive/
```

---

## What Goes Where

### `docs/` - Documentation (Tracked)

General-purpose documentation that applies across projects:

| Subdirectory | Contents |
|--------------|----------|
| `testing/` | Testing guides, approaches, configurator testing |
| `debugging/` | Serial printf, GCC techniques, USB/MSC, performance, target splitting |
| `transpiler/` | Transpiler AST types, implementation notes |
| `patterns/` | Code patterns (e.g., MSP async data access) |
| `mspapi2/` | MSP API library documentation |

**Key debugging docs:**
- `debugging/usb-msc-debugging.md` - USB mass storage issues
- `debugging/performance-debugging.md` - PID loop performance
- `debugging/target-split-verification.md` - Target directory splitting
- `debugging/gcc-preprocessing-techniques.md` - GCC preprocessing

### `scripts/` - Reusable Scripts (Tracked)

Scripts that can be reused across multiple projects:

| Subdirectory | Contents |
|--------------|----------|
| `testing/` | CRSF test scripts, configurator startup tests, MSP test utilities |
| `build/` | Build and flash helpers |
| `analysis/` | Target verification, dead code detection, preprocessing tools |

### `projects/` - Active Project Working Directories (Gitignored) **← NEW, USE THIS**

**Per-project working directories for active tasks.**

Each active project/task gets its own subdirectory with all related working files:

**Structure:**
```
projects/
└── my-feature-implementation/
    ├── notes.md                # Design notes, findings
    ├── session-state.md        # Session tracking
    ├── test-results.md         # Test output
    ├── scripts/                # Project-specific scripts
    │   └── test_feature.py
    └── data/                   # Test data, logs
        └── sample.bin
```

**What goes here:**
- Session notes and scratch files
- Project-specific test scripts
- Test data and logs
- Status tracking documents
- Anything you're actively working on

**When to create a project directory:**
- Starting a new task assignment
- Beginning an investigation
- Any work that needs multiple files

**Cleanup:** When project is complete, move reusable content to `docs/` or `scripts/`, then archive the rest to `archive/`.

### `investigations/` - Detailed Technical Investigations (Gitignored, Legacy)

**NOTE:** This directory is kept for backward compatibility with existing investigations. **For new work, use `projects/` instead.**

Detailed investigation notes for specific technical issues. Contains legacy investigation directories with extensive notes and test data.

### `reports/` - Analysis Reports (Gitignored)

Code review reports, qodo analysis, PR reviews.

### `archive/` - Completed Work (Gitignored)

Historical data that might be useful for reference:
- `completed-tasks/` - Old task assignments
- `data/` - Test logs, profiling output, eeprom dumps
- `legacy/` - Old scripts, superseded documents

---

## test_tools vs developer/scripts Distinction

There are two places for test-related code:

### `claude/test_tools/` - Project-Level Test Infrastructure

Located **outside** the developer directory at the project level:

```
claude/test_tools/
├── inav/                    # INAV-specific test tools
│   ├── crsf/                # CRSF telemetry testing
│   ├── gps/                 # GPS testing infrastructure
│   ├── msp/                 # MSP protocol testing
│   └── sitl/                # SITL testing tools
├── eph_replay/              # Ephemeris replay tools
└── configurator_indexer/    # Configurator code indexing
```

**Purpose:** Shared test infrastructure used across roles (developer, manager, security analyst)

**Use when:** Test tools need to be shared across the project or used by multiple roles

### `claude/developer/scripts/testing/` - Developer-Specific Utilities

Located in the developer directory:

**Purpose:** Developer's personal test utilities and helpers

**Use when:** Scripts are specific to developer workflow and not needed by other roles

---

## Finding Things

### Need a test script?
Look in `scripts/testing/`

### Need to understand a past investigation?
1. Check `docs/LESSONS-LEARNED.md` for key insights
2. Look in `investigations/` for full details

### Need to verify a target split?
Use scripts in `scripts/analysis/`:
- `comprehensive_verification.py`
- `verify_target_conditionals.py`
- `split_omnibus_targets.py`

### Need debugging techniques?
Look in `docs/debugging/`

---

## Adding New Content

### Starting a new task?
**Create a project directory:**
```bash
mkdir -p claude/developer/projects/my-task-name
cd claude/developer/projects/my-task-name
```

**Structure it:**
```
projects/my-task-name/
├── README.md           # What this project is about
├── notes.md            # Working notes
├── session-state.md    # Session tracking
├── scripts/            # Project-specific scripts
└── data/               # Test data, logs
```

### New reusable script?
Add to appropriate `scripts/` subdirectory with documentation.

### New documentation?
Add to appropriate `docs/` subdirectory.

### Test infrastructure?
- **Developer-specific:** `scripts/testing/`
- **Project-wide (shared):** `claude/test_tools/`

### Temporary scratch work?
Use `work-in-progress/` for quick notes (but prefer creating a `projects/` directory for anything more than a single file).

---

## Gitignored Directories

The following are excluded from version control (`.gitignore`):

- `projects/` - Active project working directories **← NEW**
- `investigations/` - Legacy investigation directories
- `work-in-progress/` - Legacy flat working directory
- `reports/` - Analysis reports
- `archive/` - Completed work
- `builds/` - Binary artifacts
- `inbox/`, `outbox/`, `sent/`, `inbox-archive/` - Email

**Why?** These contain session-specific and task-specific data. Reusable content (documentation, scripts) is extracted to tracked directories (`docs/`, `scripts/`) before archiving.

---

## Related Files

- **Developer guide:** `README.md`
- **Lessons learned:** `docs/LESSONS-LEARNED.md`
- **Skills:** `.claude/skills/*/SKILL.md`
- **Root CLAUDE.md:** `../CLAUDE.md`
