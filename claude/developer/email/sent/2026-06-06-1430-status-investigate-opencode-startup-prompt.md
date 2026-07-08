# Status Update: investigate-opencode-startup-prompt

**Date:** 2026-06-06 14:30
**From:** Developer
**To:** Manager
**Type:** Status Update

## Finding: Plugin Works But UX Gap Remains

The role-prompt.js plugin (using experimental.chat.system.transform) successfully injects role selection instructions into the LLM system prompt. I do ask for the role — but only after the user sends their first message.

The user expects to be prompted BEFORE typing anything. This isn't possible with current OpenCode hooks — there is no "session start" hook. The investigation notes (session-state.json) explicitly state this:

> "OpenCode has NO session.start hook. The experimental.chat.system.transform hook directly modifies the LLM system prompt."

## Impact

The project delivers what was technically possible, but fails to meet the user's actual expectation. The user has to send a message first, then get asked — which defeats the purpose of an automatic startup prompt.

## Recommended Next Steps

1. Reopen the project or create a new investigation
2. Monitor OpenCode's plugin API for future additions of session start / pre-prompt hooks
3. Look into alternative approaches:
   - OpenCode startup scripts or config hooks
   - Wrapper script that prompts before launching OpenCode
   - Custom OpenCode CLI launcher

---
**Developer**
