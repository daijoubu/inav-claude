#!/usr/bin/env python3
"""
ingest_session.py - Compact and ingest a Claude Code session into ChromaDB.

Called after each turn via the Stop hook. Uses a delta checkpoint so only
new lines are processed, keeping per-turn cost low.

Usage:
    python3 ingest_session.py <session.jsonl>
    python3 ingest_session.py <session.jsonl> --db-path /path/to/chromadb
"""

import json
import os
import sys
import glob
import hashlib
import argparse
from pathlib import Path

# Lazy imports — only loaded when embedding is needed
_chroma_client = None
_collection = None
_embedder = None

CHUNK_EVENT_SIZE = 6        # events per chunk
CHUNK_OVERLAP = 2           # events overlap between chunks
DB_PATH = os.path.join(os.path.dirname(__file__), "../../../../claude/log-memories/chromadb")
CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), "../../../../claude/log-memories/checkpoints")
COLLECTION_NAME = "session_memories"

REJECTION_MARKER = "The user doesn't want to proceed with this tool use"

TOOL_PARAM_INCLUDE = {
    "Bash":   ["command", "description"],
    "Read":   ["file_path"],
    "Write":  ["file_path"],
    "Edit":   ["file_path", "old_string", "new_string"],
    "Glob":   ["pattern", "path"],
    "Grep":   ["pattern", "path"],
    "Agent":  ["description", "subagent_type", "prompt"],
    "Skill":  ["skill", "args"],
    "WebSearch": ["query"],
    "WebFetch":  ["url"],
}
MAX_PARAM_LEN = 120
MAX_TEXT_LEN  = 600


def truncate(s, n):
    s = str(s)
    return s[:n] + "…" if len(s) > n else s


def fmt_tool(name, inp):
    keys = TOOL_PARAM_INCLUDE.get(name, list(inp.keys())[:2])
    parts = [f"{k}={truncate(' '.join(str(inp[k]).split()), MAX_PARAM_LEN)}"
             for k in keys if k in inp]
    return f"{name}({', '.join(parts)})"


def is_rejection(item):
    return REJECTION_MARKER in str(item.get("content", ""))


def extract_redirect(content):
    content = str(content)
    marker = "the user said:\n"
    idx = content.lower().find(marker)
    return content[idx + len(marker):].strip() if idx != -1 else None


def parse_jsonl(filepath):
    """Parse JSONL, skipping bad lines. Returns list of records."""
    records = []
    with open(filepath, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records


def records_to_events(records):
    """Convert raw records to a flat list of text events (same logic as compact_logs.py)."""
    # Deduplicate streamed assistant messages — last record per message id wins
    seen = {}
    for i, r in enumerate(records):
        if r.get("type") == "assistant":
            mid = r.get("message", {}).get("id")
            if mid:
                seen[mid] = i
    final_asst = set(seen.values())
    emitted = set()

    # Map tool_use_id → (name, input)
    tool_map = {}
    for i in final_asst:
        for c in records[i].get("message", {}).get("content", []):
            if isinstance(c, dict) and c.get("type") == "tool_use":
                tool_map[c["id"]] = (c.get("name", "?"), c.get("input", {}))

    events = []
    for i, r in enumerate(records):
        t = r.get("type", "")

        if t in ("file-history-snapshot", "last-prompt"):
            continue
        if t == "system" and r.get("subtype") == "turn_duration":
            continue
        if t == "progress":
            continue

        if t == "assistant":
            mid = r.get("message", {}).get("id")
            if mid and i != seen.get(mid):
                continue
            if mid in emitted:
                continue
            if mid:
                emitted.add(mid)
            parts = []
            for c in r.get("message", {}).get("content", []):
                if not isinstance(c, dict):
                    continue
                ct = c.get("type")
                if ct == "thinking":
                    continue
                elif ct == "text":
                    parts.append("CLAUDE: " + truncate(c.get("text", ""), MAX_TEXT_LEN))
                elif ct == "tool_use":
                    parts.append("TOOL: " + fmt_tool(c.get("name", "?"), c.get("input", {})))
            if parts:
                events.append("\n".join(parts))

        elif t == "user":
            content = r.get("message", {}).get("content", "")
            if isinstance(content, str) and content.strip():
                text = content.strip()
                # Skip system-injected XML blocks (boilerplate, not memory-worthy)
                if text.startswith(("<local-command", "<command-name",
                                    "<command-message", "<system-reminder",
                                    "This session is being continued")):
                    continue
                if text.startswith("<") and len(text) > 2000:
                    continue
                events.append("USER: " + truncate(text, MAX_TEXT_LEN))
            elif isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict) or item.get("type") != "tool_result":
                        continue
                    tid = item.get("tool_use_id", "")
                    info = tool_map.get(tid)
                    rc = item.get("content", "")
                    is_err = item.get("is_error", False)

                    if is_rejection(item):
                        call = fmt_tool(info[0], info[1]) if info else "?"
                        redirect = extract_redirect(str(rc))
                        line = f"⚠️ REJECTED: {call}"
                        if redirect:
                            line += f"\n   USER REDIRECT: {redirect}"
                        events.append(line)
                    elif is_err:
                        events.append("ERROR: " + truncate(str(rc), 200))

    return events


def chunk_events(events, session_id, project):
    """Slide a window over events to produce overlapping chunks."""
    chunks = []
    step = CHUNK_EVENT_SIZE - CHUNK_OVERLAP
    for start in range(0, max(1, len(events) - CHUNK_OVERLAP), step):
        window = events[start: start + CHUNK_EVENT_SIZE]
        if not window:
            break
        text = "\n".join(window)
        idx = start // step
        chunk_id = f"{session_id}_{idx}"
        has_rejection = any("⚠️ REJECTED" in e for e in window)
        has_redirect  = any("USER REDIRECT" in e for e in window)
        chunks.append({
            "id":            chunk_id,
            "text":          text,
            "session_id":    session_id,
            "project":       project,
            "chunk_index":   idx,
            "has_rejection": has_rejection,
            "has_redirect":  has_redirect,
        })
    return chunks


def get_db(db_path):
    global _chroma_client, _collection, _embedder
    if _collection is not None:
        return _collection

    try:
        import chromadb
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    except ImportError:
        return None  # chromadb not installed — caller skips ingest

    os.makedirs(db_path, exist_ok=True)
    _chroma_client = chromadb.PersistentClient(path=db_path)

    ef = DefaultEmbeddingFunction()
    _collection = _chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


def checkpoint_path(session_id):
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    return os.path.join(CHECKPOINT_DIR, f"{session_id}.offset")


def read_checkpoint(session_id):
    p = checkpoint_path(session_id)
    if os.path.exists(p):
        try:
            return int(open(p).read().strip())
        except ValueError:
            pass
    return 0


def write_checkpoint(session_id, line_count):
    with open(checkpoint_path(session_id), "w") as f:
        f.write(str(line_count))


def ingest(jsonl_path, db_path=None):
    db_path = db_path or os.path.abspath(DB_PATH)
    jsonl_path = os.path.abspath(jsonl_path)

    if not os.path.exists(jsonl_path):
        print(f"[ingest] File not found: {jsonl_path}", file=sys.stderr)
        return

    session_id = Path(jsonl_path).stem
    proj_root  = os.path.expanduser("~/.claude/projects")
    try:
        rel      = Path(jsonl_path).relative_to(proj_root)
        project  = rel.parts[0]
    except ValueError:
        project = "unknown"

    # Count lines to detect new content since last checkpoint
    with open(jsonl_path, encoding="utf-8", errors="replace") as f:
        all_lines = f.readlines()
    total_lines = len(all_lines)

    last = read_checkpoint(session_id)
    if total_lines <= last:
        return  # nothing new

    # Parse only new lines (delta), but include all for proper dedup context
    records = []
    for line in all_lines:
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass

    events = records_to_events(records)
    if not events:
        write_checkpoint(session_id, total_lines)
        return

    chunks = chunk_events(events, session_id, project)
    if not chunks:
        write_checkpoint(session_id, total_lines)
        return

    collection = get_db(db_path)
    if collection is None:
        return  # chromadb not installed

    # Upsert all chunks (idempotent — chunk IDs are stable)
    collection.upsert(
        ids       = [c["id"]   for c in chunks],
        documents = [c["text"] for c in chunks],
        metadatas = [{k: v for k, v in c.items() if k not in ("id", "text")}
                     for c in chunks],
    )

    new_chunks = len(chunks)
    rejections = sum(1 for c in chunks if c["has_rejection"])
    rej_note   = f", {rejections} rejection chunk(s)" if rejections else ""
    print(f"[ingest] {session_id[:8]}… {new_chunks} chunks upserted{rej_note}")

    write_checkpoint(session_id, total_lines)


def ingest_all(proj_root=None, db_path=None):
    """Bulk-ingest all sessions across all projects."""
    proj_root = proj_root or os.path.expanduser("~/.claude/projects")
    db_path   = db_path   or os.path.abspath(DB_PATH)

    all_jsonl = sorted(glob.glob(os.path.join(proj_root, "**/*.jsonl"), recursive=True))
    print(f"[ingest_all] {len(all_jsonl)} session files found")
    for path in all_jsonl:
        try:
            ingest(path, db_path)
        except Exception as e:
            print(f"[ingest_all] ERROR {path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", nargs="?", help="Path to session .jsonl (omit for bulk ingest)")
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--all", action="store_true", help="Bulk-ingest all sessions")
    args = parser.parse_args()

    if args.all or not args.jsonl:
        ingest_all(db_path=args.db_path)
    else:
        ingest(args.jsonl, db_path=args.db_path)
