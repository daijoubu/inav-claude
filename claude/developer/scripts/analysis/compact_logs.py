#!/usr/bin/env python3
"""
compact_logs.py - Compact Claude Code conversation logs into readable summaries.

Strips metadata noise while preserving:
- User messages and assistant text
- Tool calls (condensed)
- Tool REJECTIONS (always preserved in full — these signal user corrections)
- User edits / redirects attached to rejections

Usage:
    python3 compact_logs.py [project_dir] [output_dir]
    python3 compact_logs.py  # defaults: ~/.claude/projects/  ./compact_logs/
"""

import json
import os
import sys
import glob
from pathlib import Path
from datetime import datetime

REJECTION_MARKER = "The user doesn't want to proceed with this tool use"

# Map source project dir names → canonical output dir names.
# Entries with the same target value get merged into one output directory.
PROJECT_ALIASES = {
    "-home-raymorris-Documents-planes-inavflight-inav":  "inav-firmware",
    "-home-raymorris-Documents-planes-inavflight-inav2": "inav-firmware",
    "-home-raymorris-Documents-planes-inavflight-inav-build-sitl": "inav-firmware",
}

# Tool params to include (per tool name) — skip verbose/long params
TOOL_PARAM_INCLUDE = {
    "Bash": ["command", "description"],
    "Read": ["file_path", "offset", "limit"],
    "Write": ["file_path"],          # skip content — too long
    "Edit": ["file_path", "old_string", "new_string"],
    "Glob": ["pattern", "path"],
    "Grep": ["pattern", "path", "glob"],
    "Agent": ["description", "subagent_type", "prompt"],
    "Skill": ["skill", "args"],
    "WebFetch": ["url"],
    "WebSearch": ["query"],
    "TaskCreate": ["title", "description"],
    "TaskUpdate": ["task_id", "status"],
}

MAX_PARAM_LEN = 200   # truncate individual param values beyond this
MAX_RESULT_LEN = 300  # truncate tool results beyond this
MAX_TEXT_LEN = 800    # truncate long assistant/user text blocks


def truncate(s, n=MAX_PARAM_LEN):
    s = str(s)
    if len(s) > n:
        return s[:n] + f"…[+{len(s)-n}]"
    return s


def format_tool_call(name, input_dict):
    """Render a tool call as a compact line."""
    include = TOOL_PARAM_INCLUDE.get(name, list(input_dict.keys())[:3])
    params = []
    for k in include:
        if k in input_dict:
            v = input_dict[k]
            if isinstance(v, str):
                # Collapse whitespace for commands
                v = " ".join(v.split())
            params.append(f"{k}={truncate(v)}")
    return f"  → {name}({', '.join(params)})"


def format_tool_result(content, is_error=False):
    """Render a tool result as a compact line."""
    if isinstance(content, list):
        # List of content blocks
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", str(item)))
            else:
                parts.append(str(item))
        content = "\n".join(parts)
    content = str(content)
    prefix = "  ✗ ERROR: " if is_error else "  ← "
    return prefix + truncate(content, MAX_RESULT_LEN)


def is_rejection(tool_result_item):
    content = tool_result_item.get("content", "")
    if isinstance(content, list):
        content = " ".join(str(x) for x in content)
    return REJECTION_MARKER in str(content)


def extract_rejection_text(content):
    """Pull out the user's redirect message from a rejection, if any."""
    content = str(content)
    marker = "the user said:\n"
    idx = content.lower().find(marker)
    if idx != -1:
        return content[idx + len(marker):].strip()
    return None


def parse_session(filepath):
    """Parse a .jsonl session file into a list of compact event dicts."""
    records = []
    with open(filepath, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Build tool_use_id → tool call mapping (from assistant messages)
    # Use the LAST version of each message id (streaming dedup)
    seen_msg_ids = {}  # msg_id → record index (last wins)
    for i, r in enumerate(records):
        if r.get("type") == "assistant":
            mid = r.get("message", {}).get("id")
            if mid:
                seen_msg_ids[mid] = i

    final_assistant_idxs = set(seen_msg_ids.values())

    # Map tool_use_id → (tool_name, input_dict)
    tool_call_map = {}
    for i in final_assistant_idxs:
        r = records[i]
        for c in r.get("message", {}).get("content", []):
            if isinstance(c, dict) and c.get("type") == "tool_use":
                tool_call_map[c["id"]] = (c.get("name", "?"), c.get("input", {}))

    events = []

    # Track which assistant message ids we've already emitted
    emitted_asst = set()

    for i, r in enumerate(records):
        rtype = r.get("type", "")

        # Skip pure metadata
        if rtype in ("file-history-snapshot", "last-prompt"):
            continue
        if rtype == "system" and r.get("subtype") == "turn_duration":
            continue
        if rtype == "progress":
            hook = r.get("data", {}).get("hookName", "")
            if hook:
                events.append({"kind": "hook", "name": hook})
            continue
        if rtype == "summary":
            txt = r.get("summary", "")
            if txt:
                events.append({"kind": "summary", "text": truncate(txt, 400)})
            continue

        if rtype == "assistant":
            mid = r.get("message", {}).get("id")
            # Only emit the final streamed version
            if mid and i != seen_msg_ids.get(mid):
                continue
            if mid and mid in emitted_asst:
                continue
            if mid:
                emitted_asst.add(mid)

            text_parts = []
            tool_calls = []
            for c in r.get("message", {}).get("content", []):
                if not isinstance(c, dict):
                    continue
                ctype = c.get("type")
                if ctype == "thinking":
                    continue  # always strip
                elif ctype == "text":
                    text_parts.append(truncate(c.get("text", ""), MAX_TEXT_LEN))
                elif ctype == "tool_use":
                    tool_calls.append(
                        format_tool_call(c.get("name", "?"), c.get("input", {}))
                    )

            if text_parts or tool_calls:
                events.append({
                    "kind": "assistant",
                    "text": "\n".join(text_parts) if text_parts else None,
                    "tools": tool_calls,
                })
            continue

        if rtype == "user":
            content = r.get("message", {}).get("content", "")

            # Plain text user message
            if isinstance(content, str) and content.strip():
                text = content.strip()
                # Skip system-injected context blocks (very long)
                if text.startswith("<") and len(text) > 2000:
                    continue
                events.append({"kind": "user", "text": truncate(text, MAX_TEXT_LEN)})
                continue

            # Tool result messages
            if isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") != "tool_result":
                        continue

                    tid = item.get("tool_use_id", "")
                    tool_info = tool_call_map.get(tid)
                    result_content = item.get("content", "")
                    is_error = item.get("is_error", False)

                    if is_rejection(item):
                        # ALWAYS preserve rejections fully
                        tool_name = tool_info[0] if tool_info else "?"
                        tool_input = tool_info[1] if tool_info else {}
                        redirect = extract_rejection_text(str(result_content))
                        ev = {
                            "kind": "rejection",
                            "tool": tool_name,
                            "call": format_tool_call(tool_name, tool_input),
                            "redirect": redirect,
                        }
                        events.append(ev)
                    else:
                        events.append({
                            "kind": "tool_result",
                            "tool": tool_info[0] if tool_info else "?",
                            "result": format_tool_result(result_content, is_error),
                        })
            continue

    return events


def render_events(events, session_id, filepath):
    """Render events as human-readable text."""
    lines = []
    ts = datetime.now().strftime("%Y-%m-%d")
    lines.append(f"# Session: {session_id}")
    lines.append(f"# File: {os.path.basename(filepath)}")
    lines.append("")

    for ev in events:
        kind = ev["kind"]

        if kind == "user":
            lines.append(f"USER: {ev['text']}")
        elif kind == "assistant":
            if ev.get("text"):
                lines.append(f"CLAUDE: {ev['text']}")
            for t in ev.get("tools", []):
                lines.append(f"TOOL:{t}")
        elif kind == "tool_result":
            lines.append(ev["result"])
        elif kind == "rejection":
            lines.append(f"⚠️  REJECTED: {ev['call']}")
            if ev.get("redirect"):
                lines.append(f"   USER REDIRECT: {ev['redirect']}")
        elif kind == "hook":
            lines.append(f"[hook: {ev['name']}]")
        elif kind == "summary":
            lines.append(f"[session-summary: {ev['text']}]")

        lines.append("")

    return "\n".join(lines)


def main():
    proj_root = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.claude/projects")
    out_root = sys.argv[2] if len(sys.argv) > 2 else "./compact_logs"

    os.makedirs(out_root, exist_ok=True)

    all_jsonl = sorted(glob.glob(os.path.join(proj_root, "**/*.jsonl"), recursive=True))
    if not all_jsonl:
        all_jsonl = sorted(glob.glob(os.path.join(proj_root, "*.jsonl")))

    print(f"Found {len(all_jsonl)} session files under {proj_root}")

    for filepath in all_jsonl:
        session_id = Path(filepath).stem
        # Walk up to find the project dir (immediate child of proj_root)
        rel = Path(filepath).relative_to(proj_root)
        raw_proj = rel.parts[0]
        proj_name = PROJECT_ALIASES.get(raw_proj, raw_proj)

        try:
            events = parse_session(filepath)
        except Exception as e:
            print(f"  ERROR parsing {filepath}: {e}")
            continue

        if not events:
            continue

        # Count rejections for quick summary
        rejections = [e for e in events if e["kind"] == "rejection"]

        out_subdir = os.path.join(out_root, proj_name)
        os.makedirs(out_subdir, exist_ok=True)
        out_path = os.path.join(out_subdir, f"{session_id}.txt")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(render_events(events, session_id, filepath))

        size_in = os.path.getsize(filepath)
        size_out = os.path.getsize(out_path)
        pct = 100 * size_out // size_in
        rej_note = f"  {len(rejections)} rejection(s)" if rejections else ""
        print(f"  {proj_name}/{session_id[:8]}… {size_in//1024}KB → {size_out//1024}KB ({pct}%){rej_note}")


if __name__ == "__main__":
    main()
