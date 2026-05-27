# Session State Management

To prevent context loss during conversation compaction, maintain `claude/session-state.json`.

## How It Works

OpenCode compresses earlier conversation turns when the context window fills up. During compression, the LLM loses track of runtime state like todo progress and current task context. The session state file provides a persistent record that survives compaction.

A plugin injects this state into the compaction prompt so the summary preserves your context.

## Instructions

### At the start of each user turn (REQUIRED):

1. **Read `claude/session-state.json`** before responding to the user
2. If `last_user_query` differs from the current message, the session may have been compacted — restore context from the state file before proceeding
3. Check `in_progress_todo` to know what you were working on

### When you update todo items (REQUIRED):

Update `claude/session-state.json` with:

```json
{
  "current_task": "the-project-name",
  "current_todo_description": "what you're actively doing right now",
  "last_user_query": "the user's last message",
  "in_progress_todo": "the exact todo item text",
  "completed_todos": ["item 1", "item 2"],
  "notes": "any context worth preserving",
  "updated_at": "2026-05-27T12:00:00Z"
}
```

### When to update:

- **Todo starts** → set `in_progress_todo` and `current_todo_description`
- **Todo completes** → append to `completed_todos`, clear `in_progress_todo`
- **User sends new query** → update `last_user_query` and `current_todo_description`
- **Agent sub-task completes** → add relevant context to `notes`

### The state file path:

`claude/session-state.json`
