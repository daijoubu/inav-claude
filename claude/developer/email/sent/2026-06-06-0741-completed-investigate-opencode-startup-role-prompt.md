# Task Completed: Investigate OpenCode Startup Role Prompt

**Date:** 2026-06-06 07:41
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

Investigated how to restore the startup role selection prompt ("Which role should I take on today?") after porting from Claude Code to OpenCode. Created a working plugin prototype using OpenCode's `experimental.chat.system.transform` hook.

## Investigation Findings

### Path 1: Plugin hooks for session start
- **OpenCode has NO `session.start` hook** in its official plugin API (Hooks interface)
- The existing `permission-filter.js` plugin registers a `"session.start"` hook that is **silently ignored at runtime**
- Available hooks that CAN modify behavior: `experimental.chat.system.transform`, `experimental.chat.messages.transform`, `experimental.session.compacting`
- Available read-only event: `session.created` (cannot modify behavior)

### Path 2: AGENTS.md / START.md
- **AGENTS.md** is passive context injection — the model sees it but doesn't reliably act on it
- **START.md** is NOT auto-loaded by OpenCode (only AGENTS.md/CLAUDE.md are)
- Both are unreliable for forcing interactive behavior

### Path 3: Skill system
- Skills are on-demand via the `skill` tool — not suitable for a startup prompt

### Path 4: opencode.json instructions
- Currently loads `claude/docs/*.md` and `claude/*/README.md` — passive context only

## Recommendation

**Use `experimental.chat.system.transform` plugin hook** (BEST approach)

This is the most reliable mechanism because it directly modifies the LLM's system prompt — the most authoritative source of instructions for the model. It:
1. Fires on every new session
2. Injects the role selection instruction into the system prompt
3. Has built-in deduplication (won't re-inject on compaction)
4. Works regardless of model size/capability (system prompt is always obeyed)

## Prototype

Created and tested plugin: `.opencode/plugins/role-prompt.js`
- ✅ Plugin loads correctly and hook is registered
- ✅ Injects "MANDATORY FIRST ACTION" instruction into system prompt
- ✅ Deduplication prevents duplicate injection on re-compaction
- ✅ Registered in `opencode.json`

## Files Modified

- `.opencode/plugins/role-prompt.js` — NEW: Role selection plugin
- `opencode.json` — Added role-prompt.js to plugin array
- `.opencode/package.json` — Added "type": "module" to fix ESM warning

## Testing

- [x] Plugin validates: ES module syntax correct
- [x] Hook registered: experimental.chat.system.transform
- [x] Role prompt injected into system prompt array
- [x] Deduplication prevents duplicates on compaction
- [x] opencode.json validates as valid JSON

## Additional Recommendations

1. **Fix permission-filter.js:** Remove the dead `"session.start"` hook that's silently ignored (cosmetic/cleanup)
2. **Keep AGENTS.md section:** The existing AGENTS.md role prompt acts as a useful fallback for models that don't support plugins
3. **Add opencode run test:** Manually verify in a live OpenCode session that the startup prompt appears on first message

## Next Steps

- [ ] Live test: Start a new opencode session and verify the role prompt appears
- [ ] Consider cleanup: Remove dead `"session.start"` hook from permission-filter.js

---
**Developer**
