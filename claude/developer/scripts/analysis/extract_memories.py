#!/usr/bin/env python3
"""
extract_memories.py - Use an LLM to extract structured memory entries from compacted logs.

Supports two backends:
  --backend anthropic   Use Claude Haiku via ANTHROPIC_API_KEY (default if key set)
  --backend ollama      Use a local Ollama model (default if no API key)

Recommended local models (4GB VRAM or less):
  qwen2.5:3b            ~2GB VRAM — best instruction following at this size
  phi3:mini             ~2.3GB VRAM — excellent JSON output
  llama3.2:3b           ~2GB VRAM — well-tested general purpose
  mistral:7b-instruct   ~4.1GB VRAM — higher quality, tight fit at 4GB

Usage:
    python3 extract_memories.py                             # auto-detect backend
    python3 extract_memories.py --backend ollama --model qwen2.5:3b
    python3 extract_memories.py --file path/to/log.txt     # single session
    python3 extract_memories.py --review                   # show extracted memories
    python3 extract_memories.py --query "ESC spinup fix"   # semantic search
    python3 extract_memories.py --stats                    # show DB stats
    python3 extract_memories.py --list-models              # show available Ollama models
"""

import argparse
import glob
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# Paths
SCRIPT_DIR    = Path(__file__).parent
REPO_ROOT     = SCRIPT_DIR.parents[3]
LOG_DIR       = REPO_ROOT / "claude/log-memories/compacted-logs"
DB_PATH       = str(REPO_ROOT / "claude/log-memories/chromadb")
CHECKPOINT    = REPO_ROOT / "claude/log-memories/extract-checkpoints"
MEMORY_DIR    = REPO_ROOT / "claude/log-memories/extracted"
COLLECTION    = "extracted_memories"

MIN_LOG_CHARS        = 500    # skip trivially short sessions
MAX_LOG_CHARS        = 40000  # truncate very long sessions (token budget)
MAX_LOG_CHARS_OLLAMA = 10000  # smaller budget for local 3B models
OLLAMA_TIMEOUT       = 300    # seconds — 3B models are slow on long inputs

DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_OLLAMA_MODEL    = "qwen2.5:3b"
OLLAMA_URL              = "http://localhost:11434"

SYSTEM_PROMPT = """\
You analyze Claude Code conversation logs and extract memory-worthy lessons.

A memory-worthy lesson is something that:
- Was non-obvious or required effort to discover
- Is specific to this project or codebase (not generic programming knowledge)
- Would be useful to recall in a future session on the same topic
- Can be stated as a standalone fact without needing conversation context

LOOK FOR:
1. **solution** — Problems that took multiple failed attempts before working.
   Focus on WHAT FINALLY WORKED and WHY previous attempts failed.
2. **dead_end** — Approaches explicitly abandoned with a reason.
3. **correction** — Lines starting "⚠️ REJECTED" with a "USER REDIRECT:" show
   what Claude did wrong and what the user actually wanted instead.
4. **fact** — Specific discovered facts: board configs, pin conflicts, command
   flags, version behaviors, file locations, timing constraints.
5. **preference** — Consistent patterns in how the user wants things done
   (commit style, PR approach, tool choices, communication style).

SKIP:
- Things that worked on the first try with no errors or corrections
- Generic knowledge (Python syntax, standard git commands, common APIs)
- Ephemeral state (PR numbers, specific file contents that will change)
- Anything already obvious from the code or standard documentation

OUTPUT FORMAT — a JSON object with a single key "memories" containing an array.
If nothing is memory-worthy, output {"memories": []}.

EXAMPLE (follow this structure exactly):
{"memories": [
  {
    "type": "solution",
    "lesson": "ESC spinup during settings save is caused by CPU blocking during STM32 flash writes; DMA circular mode prevents it.",
    "problem": "ESCs reboot whenever flight controller saves settings mid-flight.",
    "tags": ["ESC", "flash", "DMA", "STM32"],
    "effort": 4
  }
]}

Field rules:
- "type": one of solution, dead_end, correction, fact, preference
- "lesson": standalone factual sentence — no pronouns, no story, just the fact
- "problem": one sentence describing the situation this addresses
- "tags": 2-5 keywords
- "effort": integer 1-5 (1=minor note, 3=several attempts, 5=major investigation)

Output only the JSON object, no prose before or after."""


def get_db_collection():
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=DefaultEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )


def checkpoint_path(log_file):
    CHECKPOINT.mkdir(parents=True, exist_ok=True)
    stem = Path(log_file).stem
    return CHECKPOINT / f"{stem}.done"


def already_processed(log_file):
    return checkpoint_path(log_file).exists()


def mark_done(log_file):
    checkpoint_path(log_file).touch()


class AnthropicBackend:
    def __init__(self, model=DEFAULT_ANTHROPIC_MODEL):
        import anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("ANTHROPIC_API_KEY not set", file=sys.stderr)
            sys.exit(1)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model  = model

    def extract(self, log_text, session_id, project):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=[{"type": "text", "text": SYSTEM_PROMPT,
                     "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user",
                       "content": f"Session: {session_id[:8]} | Project: {project}\n\n"
                                  f"<log>\n{log_text[:MAX_LOG_CHARS]}\n</log>"}],
        )
        return response.content[0].text.strip()

    def handle_rate_limit(self, exc):
        import anthropic
        if isinstance(exc, anthropic.RateLimitError):
            time.sleep(30)
            return True
        return False


class OllamaBackend:
    def __init__(self, model=DEFAULT_OLLAMA_MODEL, url=OLLAMA_URL):
        self.model = model
        self.url   = url.rstrip("/")
        self._check_server()

    def _check_server(self):
        try:
            urllib.request.urlopen(f"{self.url}/api/tags", timeout=3)
        except urllib.error.URLError:
            print(f"Ollama not running at {self.url}. Start it with: ollama serve",
                  file=sys.stderr)
            sys.exit(1)

    def extract(self, log_text, session_id, project):
        payload = json.dumps({
            "model":  self.model,
            "format": "json",
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",
                 "content": (
                     f"Session: {session_id[:8]} | Project: {project}\n\n"
                     f"<log>\n{sample_log(log_text, MAX_LOG_CHARS_OLLAMA)}\n</log>\n\n"
                     'Respond with ONLY: {"memories": [ ...entries... ]} '
                     'where each entry has keys: type, lesson, problem, tags, effort. '
                     'If nothing is memory-worthy output {"memories": []}'
                 )},
            ],
        }).encode()

        req = urllib.request.Request(
            f"{self.url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            data = json.loads(resp.read())
        return data["message"]["content"].strip()

    def handle_rate_limit(self, exc):
        return False   # local model, no rate limits


def list_ollama_models(url=OLLAMA_URL):
    """Print available Ollama models with size info."""
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=5) as resp:
            data = json.loads(resp.read())
        models = data.get("models", [])
        if not models:
            print("No models installed. Try: ollama pull qwen2.5:3b")
            return
        print(f"{'MODEL':<35} {'SIZE':>8}")
        print("-" * 45)
        for m in sorted(models, key=lambda x: x["name"]):
            size_gb = m.get("size", 0) / 1e9
            print(f"{m['name']:<35} {size_gb:>7.1f}GB")
    except urllib.error.URLError:
        print(f"Ollama not running at {url}")


def make_backend(args):
    """Pick backend based on args and environment."""
    backend = args.backend
    if backend == "auto":
        backend = "anthropic" if os.environ.get("ANTHROPIC_API_KEY") else "ollama"
        print(f"Backend: {backend}")

    if backend == "anthropic":
        return AnthropicBackend(model=args.model or DEFAULT_ANTHROPIC_MODEL)
    else:
        return OllamaBackend(model=args.model or DEFAULT_OLLAMA_MODEL)


def parse_raw(raw):
    """Parse LLM output into a list of memory entries."""
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
    raw = raw.rstrip("`").strip()
    try:
        entries = json.loads(raw)
        if isinstance(entries, list):
            return entries
        if isinstance(entries, dict):
            # Prefer "memories" key (schema-enforced wrapper), fall back to first list value
            if isinstance(entries.get("memories"), list):
                return entries["memories"]
            for v in entries.values():
                if isinstance(v, list):
                    return v
        return []
    except json.JSONDecodeError:
        return []


def sample_log(log_text, max_chars):
    """Extract only signal lines (USER/CLAUDE/REJECTED) up to max_chars.

    Strips tool output, file contents, and markdown from Claude responses
    so the model sees clean conversational signal without confusing content.
    """
    lines     = log_text.splitlines()
    sampled   = []
    budget    = max_chars
    in_claude = False   # True while accumulating a multi-line CLAUDE: response

    for ln in lines:
        s = ln.strip()
        if not s:
            in_claude = False
            continue

        if s.startswith("# Session:") or s.startswith("# File:"):
            sampled.append(ln); budget -= len(ln) + 1
            in_claude = False
        elif s.startswith("USER:"):
            sampled.append(ln); budget -= len(ln) + 1
            in_claude = False
        elif s.startswith("⚠️"):
            sampled.append(ln); budget -= len(ln) + 1
            in_claude = False
        elif s.startswith("CLAUDE:"):
            # Truncate long Claude responses to first 200 chars to avoid markdown confusion
            short = s[:200] + ("…" if len(s) > 200 else "")
            sampled.append(short); budget -= len(short) + 1
            in_claude = False  # skip continuation lines
        # Everything else (tool output, markdown, file contents) is skipped

        if budget <= 0:
            break

    return "\n".join(sampled)


def extract_from_log(backend, log_text, session_id, project):
    raw = backend.extract(log_text, session_id, project)
    return parse_raw(raw)


def store_entries(collection, entries, session_id, project, log_file):
    """Upsert extracted entries into ChromaDB and optionally save as markdown."""
    if not entries:
        return 0

    VALID_TYPES = {"solution", "dead_end", "correction", "fact", "preference"}
    EFFORT_MAP  = {"low": 1, "minor": 1, "medium": 3, "high": 4, "major": 5}

    ids, docs, metas = [], [], []
    for i, e in enumerate(entries):
        lesson = e.get("lesson", "").strip()
        if not lesson:
            continue
        chunk_id = f"mem_{session_id[:8]}_{i}"
        problem  = e.get("problem", "")
        tags     = e.get("tags", [])
        etype    = e.get("type", "fact")
        if etype not in VALID_TYPES:
            etype = "fact"
        effort = e.get("effort", 1)
        if isinstance(effort, str):
            effort = EFFORT_MAP.get(effort.lower(), 2)
        effort = max(1, min(5, int(effort)))

        # The document stored and embedded is lesson + problem for rich retrieval
        doc = f"{lesson}\nContext: {problem}" if problem else lesson

        ids.append(chunk_id)
        docs.append(doc)
        metas.append({
            "type":       etype,
            "lesson":     lesson[:500],
            "problem":    problem[:300],
            "tags":       " ".join(tags),
            "effort":     effort,
            "session_id": session_id,
            "project":    project,
            "source_log": str(log_file),
        })

    if ids:
        collection.upsert(ids=ids, documents=docs, metadatas=metas)

    return len(ids)


def save_markdown(entries, session_id, project):
    """Save entries as human-readable markdown for review."""
    if not entries:
        return
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    out = MEMORY_DIR / f"{session_id[:8]}_{project[:20]}.md"
    lines = [f"# Memories: {session_id[:8]} ({project})\n"]
    for e in entries:
        etype  = e.get("type", "?")
        lesson = e.get("lesson", "")
        problem = e.get("problem", "")
        tags   = ", ".join(e.get("tags", []))
        effort = e.get("effort", 1)
        lines.append(f"## [{etype.upper()}] effort={effort}")
        if problem:
            lines.append(f"**Situation:** {problem}")
        lines.append(f"**Lesson:** {lesson}")
        if tags:
            lines.append(f"**Tags:** {tags}")
        lines.append("")
    out.write_text("\n".join(lines))


def process_file(backend, collection, log_file, verbose=False):
    log_file = Path(log_file)
    if not log_file.exists():
        print(f"Not found: {log_file}", file=sys.stderr)
        return 0

    if already_processed(log_file):
        return 0

    text = log_file.read_text(encoding="utf-8", errors="replace")
    if len(text) < MIN_LOG_CHARS:
        mark_done(log_file)
        return 0

    session_id = log_file.stem
    project    = log_file.parent.name

    try:
        entries = extract_from_log(backend, text, session_id, project)
    except Exception as exc:
        if backend.handle_rate_limit(exc):
            try:
                entries = extract_from_log(backend, text, session_id, project)
            except Exception as e2:
                print(f"  ERROR {session_id[:8]}: {e2}", file=sys.stderr)
                return 0
        else:
            print(f"  ERROR {session_id[:8]}: {exc}", file=sys.stderr)
            return 0

    count = store_entries(collection, entries, session_id, project, log_file)
    if count:
        save_markdown(entries, session_id, project)

    mark_done(log_file)

    if verbose or count:
        types = [e.get("type", "?") for e in entries]
        print(f"  {session_id[:8]}… {count} memories  {types}")

    return count


def review(n=20):
    """Print recently extracted memories for review."""
    collection = get_db_collection()
    total = collection.count()
    print(f"Total extracted memories: {total}\n")
    if total == 0:
        return

    results = collection.get(limit=n, include=["documents", "metadatas"])
    for doc, meta in zip(results["documents"], results["metadatas"]):
        etype  = meta.get("type", "?")
        effort = meta.get("effort", 1)
        proj   = meta.get("project", "?")
        print(f"[{etype.upper()}] effort={effort}  project={proj}")
        print(f"  {meta.get('lesson','')}")
        print()


def query_memories(query_text, n=5):
    """Query extracted memories by semantic similarity."""
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    client = chromadb.PersistentClient(path=DB_PATH)
    col = client.get_collection(COLLECTION, embedding_function=DefaultEmbeddingFunction())
    r = col.query(query_texts=[query_text], n_results=min(n, col.count() or 1))
    for doc, meta, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0]):
        score = round(1 - dist, 3)
        etype = meta.get("type", "?")
        print(f"[{etype.upper()}] score={score}  {meta.get('lesson','')[:120]}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured memories from Claude Code session logs")
    parser.add_argument("--file",    help="Process a single compacted log file")
    parser.add_argument("--review",  action="store_true", help="Show extracted memories")
    parser.add_argument("--query",   help="Semantic search over extracted memories")
    parser.add_argument("--stats",   action="store_true", help="Show DB stats")
    parser.add_argument("--list-models", action="store_true",
                        help="List available Ollama models and exit")
    parser.add_argument("--reprocess", action="store_true",
                        help="Re-process already-checkpointed files")
    parser.add_argument("--backend", choices=["anthropic", "ollama", "auto"],
                        default="auto",
                        help="LLM backend (default: auto-detect from env)")
    parser.add_argument("--model",   default=None,
                        help="Model name override "
                             "(e.g. qwen2.5:3b, phi3:mini, mistral:7b-instruct)")
    parser.add_argument("--ollama-url", default=OLLAMA_URL,
                        help=f"Ollama server URL (default: {OLLAMA_URL})")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.list_models:
        list_ollama_models(args.ollama_url)
        return

    if args.review:
        review()
        return

    if args.query:
        query_memories(args.query)
        return

    if args.stats:
        col = get_db_collection()
        print(f"Extracted memories: {col.count()}")
        done = len(list(CHECKPOINT.glob("*.done"))) if CHECKPOINT.exists() else 0
        print(f"Sessions processed:  {done}")
        return

    if args.reprocess and CHECKPOINT.exists():
        for f in CHECKPOINT.glob("*.done"):
            f.unlink()

    # Patch OllamaBackend URL if overridden
    if args.ollama_url != OLLAMA_URL:
        OllamaBackend.__init__.__defaults__ = (args.model or DEFAULT_OLLAMA_MODEL,
                                               args.ollama_url)

    backend    = make_backend(args)
    collection = get_db_collection()

    if args.file:
        count = process_file(backend, collection, args.file, verbose=True)
        print(f"Stored {count} memories.")
        return

    all_logs = sorted(glob.glob(str(LOG_DIR / "**/*.txt"), recursive=True))
    pending  = [f for f in all_logs if not already_processed(f)]

    print(f"Found {len(all_logs)} logs, {len(pending)} to process  "
          f"[backend={backend.__class__.__name__}  "
          f"model={getattr(backend,'model','?')}]")

    total = 0
    for i, log_file in enumerate(pending, 1):
        count = process_file(backend, collection, log_file, verbose=args.verbose)
        total += count
        if i % 50 == 0:
            print(f"  [{i}/{len(pending)}] {total} memories so far")
        if isinstance(backend, OllamaBackend):
            time.sleep(0.05)   # small pause between local calls
        else:
            time.sleep(0.15)   # respect Anthropic rate limits

    print(f"\nDone. {total} memories extracted from {len(pending)} sessions.")
    print(f"Total in DB: {collection.count()}")


if __name__ == "__main__":
    main()
