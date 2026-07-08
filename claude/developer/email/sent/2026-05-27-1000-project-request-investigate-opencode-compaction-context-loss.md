# Project Request: Investigate OpenCode Compaction Context Loss

**Date:** 2026-05-27
**From:** Developer
**To:** Manager
**Type:** Project Request

## Summary

Investigate and fix an issue where OpenCode loses task context during conversation compaction. When OpenCode compresses earlier conversation history to manage the context window, the agent loses track of the current task state and reverts to the first incomplete item on the todo list.

## Observed Behavior

- During long development sessions, OpenCode performs context compaction
- After compaction, the agent can no longer answer the current query
- Instead, it restarts work from the first incomplete todo item
- This causes wasted work, confusion, and repeated cycles

## Suggested Scope

- Investigate how OpenCode handles context compaction
- Understand how the TodoWrite tool state interacts with compaction
- Determine if there's a way to preserve current task context across compactions
- Implement a fix or workaround (plugin, skill modification, or documentation)

## Suggested Type

Investigation / Bug Fix

## Suggested Priority

MEDIUM-HIGH

## Suggested Effort

3-6 hours

---
**Developer**
