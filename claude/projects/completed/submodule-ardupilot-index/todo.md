# Todo: Add ArduPilot Fork as Submodule + Build Index

## ⚠️ Long-Running Operations

Phase 3 (submodule clone) and Phase 4 (ctags index) will take significant time:
- ArduPilot repo: ~800MB+ download, thousands of files
- ctags: scanning ~500K+ source files across 3 repos

If compaction occurs, recover by reading `summary.md` and this file.

---

## Phase 1: Project Setup ✅

- [x] Create project directory with summary.md and todo.md
- [x] Verify current git state (no .gitmodules, inav+inav-configurator submodule gitlinks exist)
- [x] Update INDEX.md with new project entry
- [x] Anchor summary updated (pause CAN investigation noted)

## Phase 2: Create .gitmodules + Add ArduPilot Submodule

- [ ] Stage 2a: Create .gitmodules with inav and inav-configurator entries (fixing pre-existing broken state)
- [ ] Stage 2b: `git submodule add` the ArduPilot fork at path `ArduPilot/`
- [ ] Stage 2c: Verify .gitmodules has all three entries
- [ ] Stage 2d: Commit .gitmodules (with user approval)

## Phase 3: Clone Submodule Contents

- [ ] `git submodule update --init --recursive ArduPilot`
- [ ] Verify checkout — check HEAD commit, branch
- [ ] Verify inav and inav-configurator submodules also populate correctly

## Phase 4: Build ctags Index

- [ ] ctags -R at repo root with proper exclusions
- [ ] Verify tag file size, check for ArduPilot symbols
- [ ] Test with `find-symbol` or raw `grep` on tags file
- [ ] Document `find-symbol` for ArduPilot in AGENTS.md or README

## Phase 5: Verification & Cleanup

- [ ] Verify index works: lookup a known symbol (e.g. CANFDIface, FDCAN)
- [ ] Update project tracking (complete project)
- [ ] Resume CAN investigation project
