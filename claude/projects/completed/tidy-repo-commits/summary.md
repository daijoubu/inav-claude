# Project: Tidy Repo - Organize Commits

**Status:** ✅ COMPLETED
**Priority:** MEDIUM
**Type:** Repository Maintenance
**Created:** 2026-01-27
**Completed:** 2026-01-29
**Actual Effort:** 2-3 hours

## Overview

Batch untracked and modified files into organized, feature-based commits. Clean up files that don't need to be committed.

## Files to SKIP (do not commit)

- `.bash_profile`, `.bashrc`, `.gitconfig`, `.profile`, `.zprofile`, `.zshrc` - Shell configs
- `.idea/`, `.vscode/` - IDE configs
- `.mcp.json` - MCP config
- `.ripgreprc` - Ripgrep config
- `.claude/hooks/.claude`, `.claude/hooks/tool_permissions.log.1` - Local/log files
- All cloned repos: `PrivacyLRS/`, `aikonf405v3/`, `ardupilot/`, `betaflight*/`, `blackbox-tools*/`, `bluejay-configurator/`, `inav-blackbox-log-viewer/`, `inav-configurator/`, `inav/`, `inav2/`, `inavwiki/`, `mspapi2/`, `mwptools/`, `uNAVlib/`, `flight_controller_tester_spi/`
- `test_msp_reboot_refactor.py` - Stale test script at root
- All `*.bak` files in scripts directories
- `claude/developer/scripts/build/*.backup` files
- `claude/developer/README-ORIGINAL-840lines.md` - Old backup

## Suggested Commit Groupings

### Commit 1: Update Claude agent definitions
- `.claude/agents/check-pr-bots.md`
- `.claude/agents/fc-flasher.md`
- `.claude/agents/inav-architecture.md`
- `.claude/agents/inav-builder.md`
- `.claude/agents/inav-code-review.md`
- `.claude/agents/target-developer.md`
- `.claude/agents/test-engineer.md`

### Commit 2: Update Claude skills and hooks
- `.claude/hooks/hook_common.py`
- `.claude/skills/check-pr-docs/SKILL.md`
- `.claude/skills/check-pr-docs/tag_pr_docs.py` (deleted)
- `.claude/skills/finish-task/SKILL.md`
- `.claude/skills/flash-firmware-dfu/SKILL.md`
- `.claude/skills/flash-firmware-dfu/fc-cli.py` (deleted)
- `.claude/skills/flash-firmware-dfu/reboot-to-dfu.py` (deleted)
- `.claude/skills/flash-firmware-dfu/reboot-to-dfu.sh`
- `.claude/skills/test-configurator/SKILL.md`

### Commit 3: Update developer testing scripts (sandbox compatibility)
All modified scripts in `claude/developer/scripts/testing/`:
- `inav/blackbox/` (11 files)
- `inav/gps/` (5 files)
- `inav/msp/` (2 files)
- `inav/sitl/` (4 files)
- `inav/usb_throughput_test.py`
- `test_msp_commands.py`

### Commit 4: Update build scripts
- `claude/developer/scripts/build/flash-dfu-preserve-settings.py` (modified)
- `claude/developer/scripts/build/flash-dfu-preserve-settings-v2.py` (modified)
- New scripts: `fc-cli.py`, `reboot-to-dfu.py`, `flash-dfu-configurator-clone.py`, `flash-dfu-node.js`
- New docs: `DOCUMENTATION-UPDATE-SUMMARY.md`, `FLASH-DFU-NODE-SUMMARY.md`, `README-node-flasher.md`
- Skip: `*.backup` files

### Commit 5: Add new developer documentation
- `claude/developer/docs/gps/` (GPS M9 docs)
- `claude/developer/docs/parameter_groups/`
- `claude/developer/docs/targets/stm32h7/`
- `claude/developer/docs/aerodynamics/` (modified files)

### Commit 6: Add developer utility scripts
- `claude/developer/scripts/pdfindexer/` (new tool)
- `claude/developer/scripts/analysis/`
- `claude/developer/scripts/tag_pr_docs.py`
- `claude/developer/scripts/SANDBOX-ERROR-*.md`
- `claude/developer/scripts/testing/README-configurator-cdp.md`
- `claude/developer/scripts/testing/configurator_cdp_test.py`
- New blackbox analysis scripts (not the .bak files)

### Commit 7: Update project tracking
- `claude/projects/INDEX.md`
- `claude/projects/completed/INDEX.md`
- Deleted old active project dirs (moved to completed)
- New active project dirs
- New completed project dirs
- `claude/projects/backburner/feature-auto-alignment-tool/`
- `claude/projects/completed/add-ble-debug-logging/cliff-log-01.txt`

### Commit 8: Add manager guide
- `claude/manager/MULTI-FEATURE-PROJECTS.md`

### Commit 9: Update root config and security docs
- `CLAUDE.md`
- `.gitignore`
- `claude/security-analyst/guides/CRITICAL-BEFORE-ANALYSIS.md`
- `claude/release-manager/guides/7-pg-validation.md`

## Notes

- Review each file before committing to ensure it belongs
- Skip any files that look like temporary work or personal config
- Group by logical feature/area, not just directory
- Write clear, concise commit messages

## Completion Details

**Branch:** `chore/organize-repo-files`
**Commits Created:** 10 organized commits

**Files Processed:**
- Total staged: 619 files
- Documentation: 484+ files (GPS M9 specs, aerodynamics research, parameter groups)
- Scripts: 27 files (testing, build, utilities)
- Project tracking: 90 files
- Guides: 4 files
- Agent configs: 11 files
- Root config: 3 files

**Properly Excluded:** 46 files (personal configs, IDE settings, cloned repos, backups)

**Key Decisions:**
- Committed only current flasher versions (flash-dfu-node.js, flash-dfu-preserve-settings.py)
- Updated .gitignore to exclude email/, workspace/, IDE configs
- Files grouped logically by functional area

**Status:** Ready to merge to master when approved

## Related

- **Repository:** inavflight (meta-repo)
- **Branch:** `chore/organize-repo-files`
- **Completion Report:** `manager/email/inbox/2026-01-29-2237-completed-tidy-repo-organize-commits.md`
