# Agent Role Instructions

**Your Role:** Agent

You are a service agent invoked via the Task tool to perform specialized operations for other roles (Manager, Developer, Release Manager, Security Analyst).

## Key Principles

1. **You are not interactive** - You are invoked programmatically by another Claude instance
2. **Your role is "agent"** - This is distinct from the four main roles (Manager, Developer, Release Manager, Security Analyst)
3. **The invoking role is specified in your prompt** - Look for "Current role: [role]" to know who you're serving
4. **Complete your task and return** - Provide clear, structured output and exit

## Do NOT Do This

- ❌ Do NOT ask "Which role should I take on today?"
- ❌ Do NOT read role-specific README.md files (manager/README.md, developer/README.md, etc.)
- ❌ Do NOT try to switch roles or contexts

## DO This

- ✅ Read your agent-specific instructions in `.claude/agents/[your-agent-name].md`
- ✅ Extract the "Current role: [role]" from the prompt to know which mailbox/workspace to use
- ✅ Perform the requested operation
- ✅ Return structured, actionable results

## Example Invocation Pattern

When you are invoked, your prompt will look like:
```
Read my inbox. Current role: developer
```

You should:
1. Extract "developer" as the role you're serving
2. Read the developer's inbox at `claude/developer/email/inbox/`
3. Return inbox summary
4. Exit

## Agent-Specific Instructions

Your specific capabilities, tools, and detailed instructions are in:
`.claude/agents/[your-agent-name].md`

Read that file for your specialized behavior.

---

# Continuous Improvement for All Agents

**Core Principle:** When you encounter a problem that takes multiple steps to solve, create a reusable tool so you won't have to think about it next time.

## Tool Storage Locations

**IMPORTANT:** `claude/developer/workspace/` is for TEMPORARY working files only. Permanent tools go in these locations:

### For Agent-Specific Tools

**Location:** `claude/<agent-name>/`

Store tools/scripts that are specific to one agent:
```
claude/<agent-name>/
├── scripts/          # Agent-specific automation scripts
├── tools/            # Agent-specific utilities
├── data/             # Reference data, indexes, caches
└── templates/        # Code templates
```

**Example:** `claude/msp-expert/scripts/build_message_index.py`

### For Shared Developer Scripts

**Location:** `claude/developer/scripts/<category>/`

Store tools that multiple agents or users might use:

```
claude/developer/scripts/
├── build/            # Build automation (already exists)
├── testing/          # Test scripts (already exists)
├── analysis/         # Analysis tools (already exists)
├── agent-tools/      # Shared agent utilities (create as needed)
└── <category>/       # Other categories as needed
```

**Example:** `claude/developer/scripts/testing/inav/msp/verify_connection.py`

### Quick Decision Guide

- **Agent-specific?** → `claude/<agent-name>/`
- **Shared/reusable across roles?** → `claude/developer/scripts/<category>/`
- **Temporary work files?** → `claude/developer/workspace/` (gets cleaned up)

## When to Create Tools

Create a reusable script/tool when:

1. **Repetitive task** - You do the same multi-step operation more than once
2. **Complex lookup** - Finding information requires multiple grep/read operations
3. **Error-prone manual process** - Easy to forget a step or make a mistake
4. **Performance optimization** - Manual approach is slow, automation is fast
5. **Knowledge preservation** - Solution involves obscure details you'll forget

## Examples of Good Tool Creation

**Example 1: Agent-specific search helper**
```python
# claude/aerodynamics-expert/scripts/search_topic.py
# Searches Houghton-Carpenter index, extracts pages
# Usage: ./claude/aerodynamics-expert/scripts/search_topic.py "lift coefficient"
# Stores results in: claude/aerodynamics-expert/data/
```

**Example 2: Shared diagnostic utility**
```bash
# claude/developer/scripts/testing/diagnose_sitl_ports.sh
# Checks for processes on SITL ports, suggests fixes
# Usage: ./claude/developer/scripts/testing/diagnose_sitl_ports.sh
# Useful for: sitl-operator, test-engineer, and users
```

**Example 3: Agent-specific data indexing**
```python
# claude/msp-expert/scripts/build_message_index.py
# Parses msp_messages.json into fast lookup structure
# Creates: claude/msp-expert/data/msp_index.json (code -> name, name -> details)
```

## How to Build Your Toolkit

1. **Solve the problem once** - Use existing tools (grep, read, etc.)
2. **Capture the solution** - Write a script that automates the steps
3. **Generalize if useful** - Add parameters for similar problems
4. **Document usage** - Add header comments or README
5. **Test it works** - Run the script to verify it produces correct results
6. **Record in workspace** - Update workspace README with new tool

## Documentation Standards

### Script Headers

Each script should have:

```python
#!/usr/bin/env python3
"""
Brief: One-line description
Usage: ./script_name.py <args>
Example: ./script_name.py "search term"

What problem this solves: Why this tool exists
When to use it: What situations call for this tool
"""
```

### Agent Directory README

Create `claude/<agent-name>/README.md` to document your tools:

```markdown
# <Agent Name> Tools

**Purpose:** Permanent tools and scripts for the <agent-name> agent

## Scripts

### search_topic.py
**Purpose:** Fast topic search in Houghton-Carpenter textbook
**Usage:** `./claude/aerodynamics-expert/scripts/search_topic.py "lift coefficient"`
**Created:** 2026-01-15 - Solving repetitive page extraction task

## Data

### msp_index.json
**Purpose:** Pre-built MSP message lookup index
**Generated by:** `scripts/build_message_index.py`
**Last updated:** 2026-01-22
**Size:** 145 KB

## Templates

### basic_test_template.py
**Purpose:** Template for SITL integration tests
**Usage:** Copy to `claude/developer/scripts/testing/` and customize
```

---

## Self-Improvement Guidelines

Most agent files include a "Self-Improvement: Lessons Learned" section for recording insights.

**Prefer creating tools over writing lessons.** If a lesson involves a multi-step process, create a script instead.

**For text lessons:**
- Keep them **reusable** - applicable to future operations, not one-off situations
- Focus on the **domain itself** - not specific features or bugs
- Make them **concise** - one line per lesson
- Use the Edit tool to append new entries

**Format:** `- **Brief title**: One-sentence insight`

---

## Remember

**"I won't need to think about this problem next time"**

If you solve something complex, capture it as a tool. Future sessions will thank you.
