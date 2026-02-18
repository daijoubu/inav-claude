# Workflow Improvement: Task Assignment Lifecycle

**Date:** 2026-02-17
**Issue:** Stale task assignments accumulating in developer inbox
**Impact:** Inbox clutter, confusion about what's active vs. complete
**Severity:** LOW (organizational, not blocking)

## Problem Analysis

Task assignments are accumulating in the developer inbox even after completion. Example stale tasks found:
- HITL Tests for add-libcanard on MATEKH743 (completed 2026-02-16, archived 2026-02-17)
- DroneCAN Driver Documentation (completed 2026-02-16, archived 2026-02-17)

## Root Cause

The current workflow assumes developers will manually archive original task assignments after sending completion reports, but:

1. **Not automatic** - Manual cleanup required
2. **Not enforced** - No checklist item emphasizes this
3. **Not linked** - Original assignment and completion report aren't connected
4. **Not reminded** - Developers move to next task and forget to archive

### Current Workflow Flow

```
Manager sends assignment → Developer inbox
Developer completes work → Sends completion report → Manager inbox
Developer SHOULD archive assignment ← MANUAL (often forgotten)
Manager archives completion report ← AUTOMATIC (always happens)
Result: Original assignment sits in developer inbox indefinitely
```

## Proposed Solution

### Short-term (Process Improvement)

**Make archiving part of the completion workflow:**

1. **Update finish-task skill** - Add archiving step as explicit requirement
2. **Update developer README** - Emphasize step 15 (archive assignment)
3. **Add checklist reminder** - Include in completion report template

**Implementation:**
- When sending completion report via email-manager agent, automatically archive the original assignment
- Update finish-task skill to prompt for original assignment filename
- Add to completion report template: "Archive original assignment"

### Medium-term (Process Automation)

**Link assignments to completion reports:**

1. **Completion reports reference original assignment** - Include assignment filename in report
2. **email-manager agent improvement** - When sending completion report, prompt to archive original assignment
3. **Automatic linking** - Manager can trace completion report back to original assignment

### Long-term (System Improvement)

**Consider task tracking system:**

1. **Task ID system** - Each task gets a unique ID that persists through lifecycle
2. **Automatic archiving** - When completion report is created with task ID, auto-archive original
3. **Project linking** - Link task assignments to project directories automatically
4. **Inbox status tracking** - Dashboard showing inbox health (stale tasks, completed tasks, active tasks)

## Recommended Actions for Manager

### Now
1. ✅ **Update finish-task skill** - Add explicit archiving step
2. ✅ **Update developer README** - Emphasize inbox cleanup
3. ✅ **Add to email-manager agent** - Archive-on-completion option

### Next Sprint
4. **Create task ID system** - Assign IDs to all new assignments
5. **Add checklist to completion report** - Include "Original assignment archived"
6. **Monitor inbox health** - Track stale tasks quarterly

## Updated Developer Workflow (15 → 16 steps)

| Step | Action | Current | Updated |
|------|--------|---------|---------|
| 15 | Archive assignment | Manual | **Auto-prompt in email-manager** |
| 16 | Send completion report | Report only | **Report + archive original** |

## Example Updated Process

```markdown
# Step 15: Archive Original Assignment

When sending completion report to manager:

1. Identify original assignment filename:
   `claude/developer/email/inbox/<assignment-date>-<task-name>.md`

2. Use email-manager agent:
   - Send completion report
   - Archive original assignment
   - Verify both actions complete

Example:
Task tool with subagent_type="email-manager"
Prompt: "Send completion report and archive original assignment.
Report: <report-file>. Original assignment: <assignment-file>.
Current role: developer"
```

## Benefit Analysis

| Benefit | Impact | Effort |
|---------|--------|--------|
| Cleaner inbox | Improved UX | Low |
| No confusion | Clarity | Low |
| Better tracking | Easier project follow-up | Low |
| Reduced manual work | Time saved | Medium |
| Scalability | Works with more tasks | Medium |

## Files Affected

- `.claude/skills/finish-task/SKILL.md` - Add archiving step
- `claude/developer/README.md` - Emphasize step 15
- `.claude/agents/email-manager.md` - Auto-archive capability
- `claude/manager/README.md` - Explain new workflow

## Next Steps

1. **Manager:** Review this improvement proposal
2. **Manager + Developer:** Agree on updated workflow
3. **Implementation:** Update finish-task skill and README files
4. **Pilot:** Test with next 5 task completions
5. **Measure:** Track inbox health improvements

---

**Status:** Proposed - awaiting manager review and approval
