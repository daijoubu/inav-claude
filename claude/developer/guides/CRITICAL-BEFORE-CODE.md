# ⚠️ CRITICAL CHECKLIST - Read Before Modifying Any Code

**STOP! Complete this checklist before making ANY code changes:**

## 1. Check Lock Files

```bash
# Check if repo is locked by another session
cat claude/locks/inav.lock 2>/dev/null || echo "No lock"
cat claude/locks/inav-configurator.lock 2>/dev/null || echo "No lock"
```

**If locked:** STOP. Report to manager that repo is locked. Do NOT proceed.

## 2. Acquire Lock (if unlocked)

Use the `/start-task` skill - it handles lock acquisition and branch creation automatically.

OR manually:
```bash
# Create lock file with session info
echo "Locked by: [task-name] at $(date)" > claude/locks/inav.lock
# (or inav-configurator.lock depending on which repo)
```

## 3. Create Git Branch

```bash
cd inav  # or inav-configurator
git checkout master && git pull
git checkout -b fix/issue-XXXX-description
```

## 4. Plan End-User Documentation (If Needed)

**Evaluate if your planned change needs end-user documentation:**

- ✅ **New features** → Draft documentation NOW (before coding)
- ✅ **Behavior changes** → Draft documentation NOW
- ℹ️ **Bug fixes** → Generally no docs needed
- ℹ️ **New targets** → Generally no docs needed
- ℹ️ **Refactoring** → Only if user-facing behavior changes

**If documentation is needed:**

1. **Draft the user documentation NOW** (before implementing)
   - Write it in `claude/developer/workspace/[task-name]/draft-user-docs.md`
   - Describe the feature from the user's perspective
   - Include examples, configuration steps, and any CLI/settings changes

2. **Use this as a design review:**
   - **If the draft docs are complex** → Feature design may be too complex
   - **If hard to explain clearly** → User experience needs simplification
   - **If requires many steps** → Consider streamlining the workflow

3. **This draft will be updated later:**
   - After implementation, update the draft to match actual behavior
   - Then add to `inav/docs/` and/or `inavwiki/` before PR

## 5. Check for Specialized Agents

**Before starting implementation, check if specialized agents apply:**

| Task involves... | Use this agent FIRST |
|------------------|----------------------|
| MSP protocol work | **msp-expert** - Message formats, mspapi2 usage |
| Settings/CLI parameters | **settings-lookup** - Setting names, defaults, valid values |
| Finding firmware code | **inav-architecture** - Locates subsystems before Grep |
| Target configuration issues | **target-developer** - Flash overflow, DMA conflicts, gyro detection, pin mapping |
| SITL operations | **sitl-operator** - Start/stop/configure SITL |
| Building firmware/configurator | **inav-builder** - ALL builds (never cmake/make/npm directly) |
| Testing/validation | **test-engineer** - Reproduce bugs, run tests |

**Pattern matching:**
- Task mentions "MSP" → use **msp-expert**
- Task mentions "setting" or CLI → use **settings-lookup**
- Need to find code location → use **inav-architecture**
- Task mentions "target", "flash overflow", "DMA conflict", "gyro detection" → use **target-developer**
- Need to build anything → use **inav-builder**

## 5. Use Agents - NEVER Direct Commands

**❌ NEVER:**
- `cmake ..`
- `make TARGETNAME`
- `npm start` (for builds)
- Direct Grep on `inav/src/` without agent guidance

**✅ ALWAYS:**
- Use `inav-builder` agent for ALL builds
- Use `test-engineer` agent for ALL testing
- Use `inav-architecture` agent BEFORE searching firmware code

## 6. Before Searching Firmware Code

**❌ NEVER:** Start with `Grep` or `Explore` on `inav/src/`

**✅ ALWAYS:** Ask `inav-architecture` agent first:
```
"Where is [functionality I need to find]?"
```

The agent will tell you exactly which files/directories to look at. THEN use Grep/Read on those specific locations.

## 6. Debugging Tools Available

When investigating bugs or understanding code behavior:

1. **Serial printf debugging** - Use DEBUG macros in firmware code (via `/mwptools` for CLI)
2. **Chrome DevTools MCP** - For configurator debugging (via `/test-configurator`)
3. **GDB** - For SITL debugging (`gdb inav/build_sitl/bin/SITL.elf`)

See `guides/debugging-guide.md` for detailed usage instructions.

---

**Once this checklist is complete, proceed with your task.**

---

## Self-Improvement: Lessons Learned

When you discover something important about PRE-CODING SETUP that will likely help in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future pre-coding setup, not one-off situations
- **About setup/preparation** - lock files, branches, agent usage, search strategy
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

<!-- Add new lessons above this line -->
