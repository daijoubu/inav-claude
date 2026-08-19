#!/usr/bin/env python3
"""
Brief: Classify files sitting in role outbox/ folders as genuinely undelivered vs. stale copies of already-delivered mail.
Usage: ./check_outbox.py [--clean] [--root PATH]
Example: ./check_outbox.py
         ./check_outbox.py --clean

What problem this solves:
  The email "send" workflow used to copy a message to the recipient's inbox
  without ever removing the original from the sender's outbox/. A plain
  `find claude/*/email/outbox/ -type f` check then reported those leftovers as
  undelivered mail. On 2026-08-02 that produced 5 false positives, and a
  follow-up agent re-delivered already-processed messages (PR #2644, #11365,
  #2652, plus an answered question) into the manager's inbox before a human
  caught it.

  A file in outbox/ is only genuinely undelivered if no byte-identical copy
  exists anywhere else in the email tree. If an identical copy is already in
  some sent/, inbox/, inbox-archive/, or archive/ folder, the message was
  delivered and the outbox file is a stale leftover.

When to use it:
  - The email-manager agent's "Check for Undelivered Mail" step (run with no
    flags; it exits non-zero only if genuinely undelivered mail is found).
  - One-time cleanup of accumulated stale outbox files (run with --clean).
"""

import argparse
import hashlib
import sys
from pathlib import Path

ROLES = ["manager", "developer", "release-manager", "security-analyst"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index_delivered(root: Path) -> dict[str, list[Path]]:
    """Map content-hash -> paths, for every email file NOT in an outbox/."""
    index: dict[str, list[Path]] = {}
    for role in ROLES:
        base = root / "claude" / role / "email"
        if not base.is_dir():
            continue
        for path in base.rglob("*.md"):
            if path.parent.name == "outbox":
                continue
            index.setdefault(digest(path), []).append(path)
    return index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clean",
        action="store_true",
        help="delete outbox files confirmed to be stale duplicates of delivered mail",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="repository root containing claude/ (default: inferred from script location)",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not (root / "claude").is_dir():
        print(f"ERROR: no claude/ directory under {root}", file=sys.stderr)
        return 2

    delivered = index_delivered(root)

    stale: list[tuple[Path, Path]] = []
    undelivered: list[Path] = []

    for role in ROLES:
        outbox = root / "claude" / role / "email" / "outbox"
        if not outbox.is_dir():
            continue
        for path in sorted(outbox.glob("*.md")):
            matches = delivered.get(digest(path))
            if matches:
                stale.append((path, matches[0]))
            else:
                undelivered.append(path)

    if stale:
        verb = "Deleting" if args.clean else "Stale (already delivered)"
        print(f"## {verb}: {len(stale)}")
        for path, match in stale:
            print(f"  {path.relative_to(root)}")
            print(f"      identical to: {match.relative_to(root)}")
            if args.clean:
                path.unlink()
        print()

    if undelivered:
        print(f"## UNDELIVERED — needs delivery: {len(undelivered)}")
        for path in undelivered:
            print(f"  {path.relative_to(root)}")
        print()
        print("These have no identical copy anywhere else in the email tree.")
        print("Deliver them to the recipient's inbox/, then move to the sender's sent/.")
    else:
        print("## No undelivered mail.")

    return 1 if undelivered else 0


if __name__ == "__main__":
    sys.exit(main())
