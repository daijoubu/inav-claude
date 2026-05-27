import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

export default async function SessionStatePlugin(ctx) {
  const statePath = join(ctx.directory, "claude", "session-state.json");

  return {
    "experimental.session.compacting": async (_input, output) => {
      if (!existsSync(statePath)) return;

      try {
        const state = JSON.parse(readFileSync(statePath, "utf-8"));
        const lines = [];

        if (state.current_task) {
          lines.push(`Current task: ${state.current_task}`);
        }
        if (state.in_progress_todo) {
          lines.push(`In progress todo: ${state.in_progress_todo}`);
        }
        if (state.current_todo_description) {
          lines.push(`Currently working on: ${state.current_todo_description}`);
        }
        if (state.last_user_query) {
          lines.push(`Last user request: ${state.last_user_query}`);
        }
        if (state.completed_todos?.length > 0) {
          lines.push(`Completed todos this session: ${state.completed_todos.join(", ")}`);
        }
        if (state.notes) {
          lines.push(`Session notes: ${state.notes}`);
        }
        if (state.updated_at) {
          lines.push(`State last updated: ${state.updated_at}`);
        }

        if (lines.length > 0) {
          output.context = [
            "=== Session State (current task context) ===",
            ...lines,
            "==========================================",
          ];
        }
      } catch {
        // If the file is corrupted or unparseable, skip gracefully
      }
    },
  };
}
