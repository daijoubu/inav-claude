#!/usr/bin/env python3
"""
query_memory.py - Hybrid semantic + keyword search over session memories.

Vector search (ChromaDB) catches semantic synonyms and paraphrases.
Ripgrep fallback catches exact domain-specific tokens (board names, registers, etc.)

Usage:
    python3 query_memory.py "why do ESCs reboot during config save"
    python3 query_memory.py "MATEKF405 DMA conflict"  --n 8
    python3 query_memory.py "my question"  --only-rejections
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

DB_PATH     = os.path.join(os.path.dirname(__file__), "../../../../claude/log-memories/chromadb")
LOG_ROOT    = os.path.join(os.path.dirname(__file__), "../../../../claude/log-memories/compacted-logs")
COLLECTION  = "session_memories"


def vector_search(query, n, only_rejections, db_path):
    import chromadb
    from chromadb.utils import embedding_functions

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=os.path.abspath(db_path))
    try:
        col = client.get_collection(name=COLLECTION, embedding_function=ef)
    except Exception:
        print("[vector] Collection not found — run ingest_session.py --all first", file=sys.stderr)
        return []

    where = {"has_rejection": True} if only_rejections else None
    kwargs = dict(query_texts=[query], n_results=min(n, col.count() or 1))
    if where:
        kwargs["where"] = where

    results = col.query(**kwargs)
    docs  = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    hits = []
    for doc, meta, dist in zip(docs, metas, dists):
        hits.append({
            "text":       doc,
            "session":    meta.get("session_id", "?")[:8],
            "project":    meta.get("project", "?"),
            "score":      round(1 - dist, 3),   # cosine similarity
            "rejection":  meta.get("has_rejection", False),
            "source":     "vector",
        })
    return hits


def keyword_search(query, n, log_root):
    """Ripgrep across compacted logs for exact-token matches."""
    if not os.path.isdir(log_root):
        return []
    try:
        result = subprocess.run(
            ["rg", "--context", "4", "--max-count", str(n * 2),
             "--glob", "*.txt", query, log_root],
            capture_output=True, text=True, timeout=10
        )
        raw = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    if not raw:
        return []

    # Group by file, each match becomes one hit
    hits = []
    current_file = None
    current_lines = []
    for line in raw.splitlines():
        if line.startswith(log_root) or (os.sep in line and line.endswith(":")):
            if current_file and current_lines:
                hits.append(_rg_hit(current_file, current_lines))
            current_file = line.split(":")[0]
            current_lines = [line[len(current_file)+1:]]
        elif line == "--":
            if current_file and current_lines:
                hits.append(_rg_hit(current_file, current_lines))
            current_lines = []
        else:
            current_lines.append(line)

    if current_file and current_lines:
        hits.append(_rg_hit(current_file, current_lines))

    return hits[:n]


def _rg_hit(filepath, lines):
    p = Path(filepath)
    return {
        "text":      "\n".join(lines),
        "session":   p.stem[:8],
        "project":   p.parent.name,
        "score":     None,
        "rejection": any("REJECTED" in l for l in lines),
        "source":    "keyword",
    }


def merge_hits(vector_hits, keyword_hits, n):
    """Deduplicate by session prefix + first 60 chars; vector hits rank first."""
    seen = set()
    merged = []
    for h in vector_hits + keyword_hits:
        key = h["session"] + h["text"][:60]
        if key not in seen:
            seen.add(key)
            merged.append(h)
    return merged[:n]


def print_results(hits, query):
    if not hits:
        print(f"No results for: {query}")
        return

    print(f"\n── Memory search: {query!r} ──\n")
    for i, h in enumerate(hits, 1):
        score_str = f"  score={h['score']}" if h["score"] is not None else ""
        rej_str   = "  ⚠️ has rejection" if h["rejection"] else ""
        header    = f"[{i}] {h['project']}/{h['session']}…  ({h['source']}){score_str}{rej_str}"
        print(header)
        print(h["text"])
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Natural language query")
    parser.add_argument("--n",   type=int, default=5, help="Number of results (default 5)")
    parser.add_argument("--only-rejections", action="store_true",
                        help="Restrict to chunks containing user corrections")
    parser.add_argument("--db-path",  default=DB_PATH)
    parser.add_argument("--log-root", default=LOG_ROOT)
    args = parser.parse_args()

    v_hits = vector_search(args.query, args.n, args.only_rejections, args.db_path)
    k_hits = keyword_search(args.query, args.n, args.log_root)
    merged = merge_hits(v_hits, k_hits, args.n)
    print_results(merged, args.query)
