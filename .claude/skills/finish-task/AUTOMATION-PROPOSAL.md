# Automation Proposal: finish-task Skill Enhancement

**File:** `.claude/skills/finish-task/SKILL.md`
**Objective:** Prevent stale task assignments in developer inbox
**Scope:** Add automatic archiving of original task assignment

---

## Current Limitation

The finish-task skill guides developers through:
1. Verify changes
2. Run tests
3. Stage changes
4. Create commit
5. Push to remote
6. Create PR
7. Release lock
8. **Send completion report** ✅
9. (Missing) Archive original assignment ❌

**Problem:** Step 9 exists in README.md but isn't enforced or automated

## Proposed Changes to SKILL.md

### Add New Section After "Send Completion Report"

**Location:** After section 8 (Send Completion Report), add section 9

```markdown
### 9. Archive Original Task Assignment

**IMPORTANT:** Remove original assignment from your inbox to keep it clean.

Identify the original task assignment file:
```bash
ls -ltr claude/developer/email/inbox/ | grep -i "<task-name>"
```

Archive it:
```bash
# Option A: Using email-manager agent (recommended)
Task tool with subagent_type="email-manager"
Prompt: "Archive the following message to inbox-archive: <filename>. Current role: developer"

# Option B: Manual
mv claude/developer/email/inbox/<original-assignment>.md \
   claude/developer/email/inbox-archive/
```

This completes the task lifecycle:
- ✅ Original assignment received
- ✅ Work completed
- ✅ Completion report sent
- ✅ Original assignment archived
```

### Update Step Numbers Throughout

- Section 8: "Send Completion Report"
- Section 9: "Archive Original Task Assignment" (NEW)
- Section 10: "Release the Lock" (was 7)

**Note:** Update related skills reference section at bottom.

---

## Enhanced email-manager Agent Integration

### Proposed New Capability

Add to email-manager agent description:

```markdown
name: email-manager
description: "...Manage internal project email...
Also supports linking completion reports to original assignments
and automatic archiving of original task files when completion reports are sent."
```

### New email-manager Workflow

When developer sends completion report:

```
Developer asks: "Send completion report for task X"
email-manager prompts: "Original assignment file? (e.g., 2026-02-17-1545-task-finalize-libcanard-dronecan.md)"
Developer responds: "2026-02-17-1545-task-finalize-libcanard-dronecan.md"
email-manager THEN:
1. Create completion report in developer/email/sent/
2. Copy to manager/email/inbox/
3. Archive original assignment to developer/email/inbox-archive/
4. Return status summary showing both actions completed
```

---

## Implementation Details

### Change 1: Update SKILL.md

**File:** `.claude/skills/finish-task/SKILL.md`

**Add:**
```markdown
### 9. Archive Original Task Assignment

When completing a task, you must also archive the original task assignment
from your inbox. This prevents stale entries and keeps your inbox clean.

**Find the original assignment:**
```bash
ls -ltr claude/developer/email/inbox/ | grep -i <task-name>
```

**Archive it using email-manager agent:**
```
Task tool with subagent_type="email-manager"
Prompt: "Archive message <filename>. Current role: developer"
```

**Verify success:**
```bash
ls claude/developer/email/inbox-archive/ | grep <task-name>
```

This completes the task lifecycle and keeps your inbox clean.
```

**Renumber:**
- Old steps 7-8 become steps 10-11

### Change 2: Update Related Skills Section

```markdown
## Related Skills

- **start-task** - Begin tasks with proper setup
- **git-workflow** - Commit changes and manage branches
- **create-pr** - Create pull request after task completion
- **check-builds** - Verify builds pass before finishing
- **email-manager** - Send completion reports AND archive original assignments
```

### Change 3: Add to Completion Report Template

Add checkbox to completion report template:

```markdown
## Completion Checklist

- [ ] All changes committed and pushed
- [ ] PR created (if applicable)
- [ ] Lock released
- [ ] Completion report created
- [ ] **Original task assignment archived** ← NEW
```

---

## Benefits

| Benefit | Impact |
|---------|--------|
| **Cleaner inbox** | Developers see only active tasks |
| **No forgotten steps** | Archiving is part of workflow |
| **Clear task lifecycle** | Easy to trace from start to finish |
| **Scalability** | Works as task volume increases |
| **Better habits** | Reinforces good practices |

---

## Risks & Mitigations

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Developer forgets to provide filename | Medium | Add to checklist, emphasize in prompt |
| Wrong file archived | Low | Verify with filename pattern matching |
| Loss of historical records | Very Low | Archived files stay in inbox-archive |

---

## Testing the Change

### Test Case 1: Normal Workflow
1. Developer has assignment in inbox
2. Completes work and creates completion report
3. Uses email-manager to send report
4. email-manager prompts for original assignment file
5. Developer provides filename
6. email-manager archives it
7. ✅ Verify both actions completed

### Test Case 2: Manual Archive
1. Developer completes work
2. Sends completion report manually
3. Uses separate email-manager call to archive
4. ✅ Verify file moved to inbox-archive

---

## Rollout Plan

### Phase 1 (Now)
1. Update SKILL.md with archiving step
2. Add to completion report template
3. Communicate to developer

### Phase 2 (Next Week)
1. Monitor first 3 task completions
2. Verify developers are archiving
3. Adjust guidance if needed

### Phase 3 (Future)
1. Consider email-manager enhancement for auto-prompting
2. Create dashboard to track inbox health
3. Implement long-term automation

---

## Related Documentation

- `claude/manager/WORKFLOW-IMPROVEMENTS.md` - Manager-level improvement proposal
- `claude/developer/README.md` - Developer workflow guide
- `.claude/agents/email-manager.md` - email-manager agent documentation

---

**Status:** Proposed - awaiting implementation decision
**Priority:** LOW (organizational improvement, no blocking issues)
**Effort:** 1-2 hours (documentation updates only)
