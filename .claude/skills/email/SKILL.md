---
name: email
description: Read, send, and manage internal email messages between project roles (Manager, Developer, Release Manager, Security Analyst). Use when user mentions email, inbox, messages, send task, complete task, or assign work.
---

<objective>Handle all internal email operations for the INAV project communication system.</objective>

<intake>
Before any operation, determine the caller's role from the prompt (look for "Current role:", "I am the [role]", or infer from context).
</intake>

<email_directories>
| Role | Inbox | Sent |
|------|-------|------|
| manager | claude/manager/email/inbox/ | claude/manager/email/sent/ |
| developer | claude/developer/email/inbox/ | claude/developer/email/sent/ |
| release-manager | claude/release-manager/email/inbox/ | claude/release-manager/email/sent/ |
| security-analyst | claude/security-analyst/email/inbox/ | claude/security-analyst/email/sent/ |
</email_directories>

<operations>

### Read Inbox (Most Common)
```
ls -lt claude/{role}/email/inbox/
```
Display messages in table format with Date|Type|Subject|From|Action.

### Send Email
1. Create in `claude/{your-role}/email/sent/` with format: `YYYY-MM-DD-HHMM-{type}-{description}.md`
2. Copy to recipient: `cp claude/{your-role}/email/sent/{file}.md claude/{recipient-role}/email/inbox/`

### Archive Message
```
mv claude/{role}/email/inbox/{file}.md claude/{role}/email/inbox-archive/
```

### Check Outbox (Undelivered)
```
find claude/*/email/outbox/ -type f -name "*.md"
```

</operations>

<templates>

### Task Assignment (Manager → Developer)
```
# Task Assignment: <Title>

**Date:** YYYY-MM-DD HH:MM
**From:** Manager
**To:** Developer
**Project:** <project-name>
**Priority:** HIGH | MEDIUM-HIGH | MEDIUM | LOW
**Estimated Effort:** X-Y hours
**Base Branch:** <branch>

## Task
<What needs to be done>

## Background
<Context and why>

## What to Do
1. Step 1
2. Step 2

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Project Directory
`claude/projects/active/<project-name>/`

---
**Manager**
```

### Completion Report (Developer → Manager)
```
# Task Completed: <Title>

**Date:** YYYY-MM-DD HH:MM
**From:** Developer
**To:** Manager
**Status:** COMPLETED

## Summary
<What was accomplished>

## Branch/PR
**Branch:** `name` | **PR:** #XXXX

## Changes
- `file.c` - Description

## Testing
- [ ] Tests passed

---
**Developer**
```

### Status Update (Developer → Manager)
```
# Status Update: <Title>

**Date:** YYYY-MM-DD HH:MM
**From:** Developer
**To:** Manager

## Status
<Where things stand>

## Blockers
<Issues or "None">

## Next Steps
<What's planned>

---
**Developer**
```

### Guidance (Manager → Developer)
```
# Guidance: <Topic>

**Date:** YYYY-MM-DD HH:MM
**From:** Manager
**To:** Developer
**Re:** <Project or question>

## Guidance
<Direction on how to proceed>

## Rationale
<Why this approach>

## References
<Documentation or examples>

---
**Manager**
```

</templates>

<response_formats>

**Read Inbox:**
```
┌──────────────┬─────────────────┬─────────────────────┬─────────┬────────────────────┐
│ Date        │ Type            │ Subject             │ From    │ Action            │
├────────────┼─────────────────┼───────────────────���─┼─────────┼────────────────────┤
│ 2026-04-14│ Task Assignment │ Investigate Drone...│ Manager │ Review & accept   │
└────────────┴─────────────────┴─────────────────────┴─────────┴────────────────────┘
```

**Sent:** "Files created: [path], Copied to: [path], Status: DELIVERED"

**Archived:** "File: [filename], Moved: [src] → [dst], Status: ARCHIVED"

</response_formats>

<file_naming>
`YYYY-MM-DD-HHMM-{type}-{description}.md`

Types: task, completed, status, guidance, question, reminder
</file_naming>

<quick_actions>
- **Check my inbox**: `ls -lt claude/{role}/email/inbox/`
- **Send task**: Create in sent/, copy to developer inbox
- **Archive report**: Move to inbox-archive/
- **Check undelivered**: `find claude/*/email/outbox/ -type f`
</quick_actions>

<workflow>
Manager → Task Assignment → Developer → Completion Report → Manager
</workflow>

<related_skills>
- `.claude/skills/communication/SKILL.md` - Message templates
- `.claude/skills/projects/SKILL.md` - Project task workflows
</related_skills>