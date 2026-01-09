# Agent Template

Use this template when creating new agents. Copy the content below and customize for your specific agent.

**Location:** Create agents at `.claude/agents/<agent-name>.md`

---

```yaml
---
name: agent-name
description: "One-sentence purpose. Use PROACTIVELY when [trigger]. Returns [output type]."
model: haiku|sonnet|opus
tools: ["Tool1", "Tool2"]
skills: ["skill-name"]  # Only if needed
---

# Role Statement

One paragraph describing the agent's expertise and role.

## Responsibilities

1. **Primary task** - Main function
2. **Secondary task** - Supporting function
3. **Reporting** - What to always include in responses

---

## Required Context

When this agent is invoked, the caller MUST provide:

- **[Required item 1]**: Description of what's needed and why
- **[Required item 2]**: Description of what's needed and why
- **[Optional item]**: (optional) Description

**Example invocation:**
```
Task tool with subagent_type="agent-name"
Prompt: "Do X with Y. Context: [required context here]"
```

---

## Available Scripts/Resources

### Script Category
```bash
path/to/script.sh
```
- What it does
- Expected output

### Related Files
- `path/to/file` - Description

---

## Related Documentation

Internal documentation relevant to this agent's domain:

- `claude/developer/docs/path/to/doc.md` - Description
- `claude/developer/README.md` - Section X covers Y

---

## Common Operations

### Operation 1
```bash
command or steps
```

### Operation 2
```bash
command or steps
```

---

## Response Format

Always include in your response:

1. **Operation performed**: What action was taken
2. **Status**: SUCCESS / FAILURE / [other states]
3. **Key output**: The main result
4. **For failures**: Error message and suggested fix

**Example response:**
```
## [Operation] Result

- **Status**: SUCCESS
- **Output**: [key result]
- **Details**: [relevant info]
```

---

## Important Notes

- Note 1 about gotchas or permissions
- Note 2 about edge cases
- Note 3 about limitations

---

## Self-Improvement: Lessons Learned

When you discover something important about [AGENT'S DOMAIN] that will likely help in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future [operations], not one-off situations
- **About [domain] itself** - not about specific [items] being processed
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

<!-- Add new lessons above this line -->
```
