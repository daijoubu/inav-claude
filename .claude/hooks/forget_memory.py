#!/usr/bin/env python3
"""
forget_memory.py - Remove memories from ChromaDB that are no longer useful.

Usage:
    # Search and delete by semantic query (shows matches, prompts confirmation):
    python3 forget_memory.py "you are a developer"

    # Delete a specific chunk by ID (no confirmation prompt):
    python3 forget_memory.py --id session123abc_0

    # List all chunks in the database:
    python3 forget_memory.py --list [--session SESSION_PREFIX]

    # Dry run — show what would be deleted without deleting:
    python3 forget_memory.py "query" --dry-run

    # Adjust similarity threshold (default 0.55, lower = broader match):
    python3 forget_memory.py "query" --threshold 0.5
"""

import argparse
import os
import sys

DB_PATH    = os.path.join(os.path.dirname(__file__),
             "../../claude/log-memories/chromadb")
COLLECTION = "session_memories"
DEFAULT_THRESHOLD = 0.55   # slightly lower than inject threshold — cast a wider net for deletion
MAX_RESULTS = 10


def get_collection():
    try:
        import chromadb
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    except ImportError:
        print("ERROR: chromadb is not installed. Run: pip install chromadb", file=sys.stderr)
        sys.exit(1)

    db_path = os.path.abspath(DB_PATH)
    if not os.path.isdir(db_path):
        print(f"ERROR: ChromaDB not found at {db_path}", file=sys.stderr)
        sys.exit(1)

    ef     = DefaultEmbeddingFunction()
    client = chromadb.PersistentClient(path=db_path)
    try:
        return client.get_collection(name=COLLECTION, embedding_function=ef)
    except Exception as e:
        print(f"ERROR: Could not open collection '{COLLECTION}': {e}", file=sys.stderr)
        sys.exit(1)


def show_chunk(chunk_id, text, meta, score=None):
    session = meta.get("session_id", "?")[:12]
    project = meta.get("project", "?")
    score_str = f"  score={score:.3f}" if score is not None else ""
    rej = "  ⚠️ has_rejection" if meta.get("has_rejection") else ""
    print(f"\n  ID: {chunk_id}")
    print(f"  [{project} / {session}…{score_str}{rej}]")
    for line in text.splitlines():
        print(f"    {line}")


def cmd_search(query, threshold, dry_run, yes):
    col   = get_collection()
    total = col.count()
    if total == 0:
        print("Database is empty — nothing to remove.")
        return

    results = col.query(
        query_texts=[query],
        n_results=min(MAX_RESULTS, total),
    )
    docs  = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    ids   = results.get("ids", [[]])[0]

    hits = []
    for chunk_id, doc, meta, dist in zip(ids, docs, metas, dists):
        sim = round(1.0 - dist, 3)
        if sim >= threshold:
            hits.append((chunk_id, doc, meta, sim))

    if not hits:
        print(f"No chunks above threshold {threshold} for query: {query!r}")
        print("Try lowering --threshold (e.g. --threshold 0.45)")
        return

    print(f"Found {len(hits)} chunk(s) matching {query!r} (threshold={threshold}):")
    for chunk_id, doc, meta, sim in hits:
        show_chunk(chunk_id, doc, meta, score=sim)

    if dry_run:
        print(f"\n[dry-run] Would delete {len(hits)} chunk(s).")
        return

    if not yes:
        print(f"\nDelete these {len(hits)} chunk(s)? [y/N] ", end="", flush=True)
        answer = sys.stdin.readline().strip().lower()
        if answer not in ("y", "yes"):
            print("Aborted.")
            return

    chunk_ids = [h[0] for h in hits]
    col.delete(ids=chunk_ids)
    print(f"Deleted {len(chunk_ids)} chunk(s).")


def cmd_delete_id(chunk_id, dry_run):
    col = get_collection()
    result = col.get(ids=[chunk_id])
    if not result["ids"]:
        print(f"Chunk ID not found: {chunk_id}")
        sys.exit(1)

    doc  = result["documents"][0]
    meta = result["metadatas"][0]
    show_chunk(chunk_id, doc, meta)

    if dry_run:
        print("\n[dry-run] Would delete this chunk.")
        return

    col.delete(ids=[chunk_id])
    print(f"\nDeleted chunk: {chunk_id}")


def cmd_list(session_prefix):
    col   = get_collection()
    total = col.count()
    if total == 0:
        print("Database is empty.")
        return

    # ChromaDB doesn't support server-side filtering by metadata prefix easily,
    # so we fetch all and filter client-side.
    all_data = col.get(include=["documents", "metadatas"])
    ids   = all_data["ids"]
    docs  = all_data["documents"]
    metas = all_data["metadatas"]

    rows = list(zip(ids, docs, metas))
    if session_prefix:
        rows = [(i, d, m) for i, d, m in rows
                if m.get("session_id", "").startswith(session_prefix)]

    if not rows:
        print(f"No chunks found" + (f" for session prefix '{session_prefix}'" if session_prefix else "") + ".")
        return

    print(f"{len(rows)} chunk(s) in database (total={total}):")
    for chunk_id, doc, meta in rows:
        show_chunk(chunk_id, doc, meta)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove memories from the ChromaDB session_memories collection.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("query", nargs="?", help="Semantic query to find memories to remove")
    parser.add_argument("--id",        metavar="CHUNK_ID", help="Delete a specific chunk by ID")
    parser.add_argument("--list",      action="store_true", help="List all chunks in the database")
    parser.add_argument("--session",   metavar="PREFIX",    help="Filter --list by session ID prefix")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help=f"Similarity threshold for query search (default {DEFAULT_THRESHOLD})")
    parser.add_argument("--dry-run",   action="store_true", help="Show what would be deleted, don't delete")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    if args.id:
        cmd_delete_id(args.id, args.dry_run)
    elif args.list:
        cmd_list(args.session)
    elif args.query:
        cmd_search(args.query, args.threshold, args.dry_run, args.yes)
    else:
        parser.print_help()
        sys.exit(1)
