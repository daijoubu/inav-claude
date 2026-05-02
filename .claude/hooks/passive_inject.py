#!/usr/bin/env python3
"""
passive_inject.py - Auto-inject highly relevant memories into the current session.

Called by stop-hook.sh after each turn. Queries ChromaDB using the last user
message + recent tool names as signal. Only injects chunks that haven't been
seen in this session yet.

Exits 0 with no output if nothing to inject.
Exits 0 with a plain-text memory block on stdout if something should be injected.
"""

import json
import os
import sys
from pathlib import Path

INJECT_DIR  = os.path.expanduser("~/.claude/hooks/injected")
DB_PATH     = os.path.join(os.path.dirname(__file__),
              "../../claude/log-memories/chromadb")
COLLECTION  = "session_memories"
THRESHOLD   = 0.62   # cosine similarity — raise if too noisy, lower if misses too much
                     # ONNX all-MiniLM-L6-v2 top semantic matches score ~0.65-0.72
MAX_INJECT  = 2      # max new chunks to inject per turn
MAX_CHUNK_DISPLAY = 400  # truncate chunk text in the injected message


def load_injected(session_id):
    path = os.path.join(INJECT_DIR, f"{session_id}.json")
    if os.path.exists(path):
        try:
            return set(json.loads(open(path).read()))
        except Exception:
            pass
    return set()


def save_injected(session_id, ids):
    os.makedirs(INJECT_DIR, exist_ok=True)
    path = os.path.join(INJECT_DIR, f"{session_id}.json")
    with open(path, "w") as f:
        json.dump(sorted(ids), f)


def build_query(transcript_path):
    """Extract last user message + recent tool names as query string."""
    if not transcript_path or not os.path.exists(transcript_path):
        return None

    records = []
    with open(transcript_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    last_user_msg = ""
    recent_tools = []

    # Walk backward for last user message
    for r in reversed(records):
        if r.get("type") == "user":
            content = r.get("message", {}).get("content", "")
            if isinstance(content, str) and content.strip():
                text = content.strip()
                # Skip system-injected blocks
                # Skip system-injected XML blocks of any length
                if text.startswith("<local-command") or text.startswith("<command-name"):
                    continue
                if text.startswith("<") and len(text) > 500:
                    continue
                last_user_msg = text[:600]
                break

    # Walk backward for recent tool names (last ~3 assistant turns)
    turns_seen = 0
    seen_msg_ids = set()
    for r in reversed(records):
        if r.get("type") == "assistant":
            mid = r.get("message", {}).get("id", "")
            if mid in seen_msg_ids:
                continue
            seen_msg_ids.add(mid)
            for c in r.get("message", {}).get("content", []):
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    name = c.get("name", "")
                    inp  = c.get("input", {})
                    # Include description or first meaningful param
                    detail = (inp.get("description") or inp.get("command","")[:60]
                              or inp.get("pattern","") or inp.get("query",""))
                    recent_tools.append(f"{name} {detail}".strip())
            turns_seen += 1
            if turns_seen >= 3:
                break

    if not last_user_msg:
        return None

    parts = [last_user_msg]
    if recent_tools:
        parts.append("Tools used: " + ", ".join(recent_tools[:6]))

    return " | ".join(parts)


def search(query, already_injected, current_session_id=""):
    """Return list of (chunk_id, text, project, session, score) above threshold."""
    try:
        import chromadb
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    except ImportError:
        return []

    db_path = os.path.abspath(DB_PATH)
    if not os.path.isdir(db_path):
        return []

    try:
        ef = DefaultEmbeddingFunction()
        client = chromadb.PersistentClient(path=db_path)
        col = client.get_collection(name=COLLECTION, embedding_function=ef)
    except Exception:
        return []

    total = col.count()
    if total == 0:
        return []

    results = col.query(
        query_texts=[query],
        n_results=min(10, total),
    )

    docs   = results.get("documents", [[]])[0]
    metas  = results.get("metadatas", [[]])[0]
    dists  = results.get("distances", [[]])[0]
    ids    = results.get("ids", [[]])[0]

    hits = []
    for chunk_id, doc, meta, dist in zip(ids, docs, metas, dists):
        similarity = 1.0 - dist
        if similarity < THRESHOLD:
            continue
        if chunk_id in already_injected:
            continue
        # Skip chunks written in the current session — Claude already said them.
        if current_session_id and meta.get("session_id", "") == current_session_id:
            continue
        hits.append({
            "id":       chunk_id,
            "text":     doc,
            "project":  meta.get("project", ""),
            "session":  meta.get("session_id", "")[:8],
            "score":    round(similarity, 3),
            "rejection": meta.get("has_rejection", False),
        })

    # Sort by score descending, cap at MAX_INJECT
    hits.sort(key=lambda h: h["score"], reverse=True)
    return hits[:MAX_INJECT]


def format_message(hits):
    lines = ["📎 RELEVANT PAST EXPERIENCE (auto-recalled from memory):"]
    for h in hits:
        rej = " ⚠️ contains correction" if h["rejection"] else ""
        lines.append(f"\n[{h['project']}/{h['session']}… score={h['score']}{rej}]")
        text = h["text"]
        if len(text) > MAX_CHUNK_DISPLAY:
            text = text[:MAX_CHUNK_DISPLAY] + "…"
        lines.append(text)
    lines.append("\n(Use /memory <query> for a full search)")
    return "\n".join(lines)


INJECT_LOG = os.path.expanduser("~/.claude/hooks/passive_inject.log")


def log(msg):
    with open(INJECT_LOG, "a") as f:
        from datetime import datetime
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript", nargs="?", default="")
    parser.add_argument("session_id", nargs="?", default="")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be injected without marking as seen")
    parser.add_argument("--test-all", action="store_true",
                        help="Score every user message in the transcript (tuning mode)")
    parser.add_argument("--show-log", action="store_true",
                        help="Print the injection log and exit")
    parser.add_argument("--threshold", type=float, default=THRESHOLD,
                        help=f"Similarity threshold (default {THRESHOLD})")
    args = parser.parse_args()

    if args.show_log:
        if os.path.exists(INJECT_LOG):
            print(open(INJECT_LOG).read())
        else:
            print("No injection log yet.")
        sys.exit(0)

    transcript_path = args.transcript
    session_id      = args.session_id
    threshold       = args.threshold

    if not session_id:
        sys.exit(0)

    # ── Test-all mode: score every user message for tuning ────────────────────
    if args.test_all:
        import chromadb
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        db_path = os.path.abspath(DB_PATH)
        ef  = DefaultEmbeddingFunction()
        col = chromadb.PersistentClient(path=db_path).get_collection(
                  COLLECTION, embedding_function=ef)

        records = []
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try: records.append(json.loads(line))
                except: pass

        seen_prompts = set()
        for r in records:
            if r.get("type") != "user":
                continue
            content = r.get("message", {}).get("content", "")
            if not isinstance(content, str) or not content.strip():
                continue
            text = content.strip()
            if text.startswith("<local-command") or text.startswith("<command-name"):
                continue
            if text.startswith("<") and len(text) > 500:
                continue
            key = text[:60]
            if key in seen_prompts:
                continue
            seen_prompts.add(key)

            results = col.query(query_texts=[text[:600]], n_results=3)
            top_scores = [round(1 - d, 3) for d in results["distances"][0]]
            top_docs   = [d[:60] for d in results["documents"][0]]
            fires = "✓ WOULD INJECT" if top_scores and top_scores[0] >= threshold else "✗"
            print(f"{fires}  [{top_scores[0] if top_scores else 0:.3f}]  query={text[:70]!r}")
            if top_scores and top_scores[0] >= threshold:
                for score, doc in zip(top_scores, top_docs):
                    print(f"         score={score:.3f}  {doc!r}")
        sys.exit(0)

    # ── Normal / dry-run mode ─────────────────────────────────────────────────
    query = build_query(transcript_path)
    if not query:
        log(f"session={session_id[:8]} no query built")
        sys.exit(0)

    already_injected = load_injected(session_id)
    hits = [h for h in search(query, already_injected, session_id) if h["score"] >= threshold]

    log(f"session={session_id[:8]} query={query[:80]!r} hits={len(hits)} "
        f"already_injected={len(already_injected)}")

    for h in hits:
        log(f"  → {h['id']} score={h['score']} project={h['project']} "
            f"rejection={h['rejection']}")
        log(f"    text={h['text'][:120]!r}")

    if not hits:
        sys.exit(0)

    print(format_message(hits))

    if not args.dry_run:
        new_ids = already_injected | {h["id"] for h in hits}
        save_injected(session_id, new_ids)
    else:
        print("\n[dry-run: not marking as injected]", file=sys.stderr)
