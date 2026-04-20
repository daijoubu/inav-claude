#!/bin/bash
# First-time onboarding message — shown when completed-cycles.txt == 0
# Called by session-start.sh. Outputs a JSON systemMessage.

python3 - <<'PYEOF'
import json

msg = """\
WELCOME TO THE INAV CLAUDE FRAMEWORK — FIRST TIME SETUP

This system uses separate Claude sessions for each role, keeping each
session's context focused. The main roles are Manager and Developer.

═══════════════════════════════════════════════════════════════
HOW IT WORKS (read this once — it will make sense quickly)
═══════════════════════════════════════════════════════════════

  [Manager session]               [Developer session]
  ─────────────────               ──────────────────
  Plan what to build         →    Check inbox for assignment
  Create project docs             Run /start-task (branch + lock)
  Send task to dev inbox          Have test-engineer write a failing test
                                  Implement the fix
                                  Build with inav-builder agent
  [Manager session]      ←    Run /finish-task (commit, PR, report)
  Review completion report
  Archive & close project

One role per session. Never do Manager work and Developer work in
the same Claude session.

═══════════════════════════════════════════════════════════════
YOUR FIRST SESSION — START AS MANAGER
═══════════════════════════════════════════════════════════════

Type "manager" now to make this a manager session. As Manager you will:

  1. Describe what you want built or fixed

  2. Claude creates a project (in claude/projects/active/<name>/)
     with summary.md (what/why/approach) and todo.md (task list)

  3. Claude uses the email-manager agent to send a task assignment to the developer

  4. You can end this session when the assignment is sent (or use it to create other projects)

═══════════════════════════════════════════════════════════════
THEN START A NEW SESSION AS DEVELOPER
═══════════════════════════════════════════════════════════════

Open a new Claude Code session and say "developer". Claude will:

  1. Check inbox with email-manager agent (finds the assignment)
  2. Run /start-task to set up branch and acquire lock
  3. Have test-engineer agent write a FAILING test first
  4. Implement the fix
  5. Build with inav-builder agent
  6. Verify the test passes
  7. Run /finish-task to commit, create PR, and report back

═══════════════════════════════════════════════════════════════
KEY RULES (violations cause pain later)
═══════════════════════════════════════════════════════════════

  ✓  inav-builder agent for ALL firmware/configurator builds
  ✓  inav-architecture agent to FIND code before searching
  ✓  test-engineer agent writes tests BEFORE you fix bugs
  ✓  Manager assigns; Developer implements — never swap

═══════════════════════════════════════════════════════════════

Which role today?  manager / developer / release-manager"""

print(json.dumps({"systemMessage": msg}))
PYEOF
