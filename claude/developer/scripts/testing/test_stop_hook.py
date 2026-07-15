#!/usr/bin/env python3
"""
Acceptance test for .claude/hooks/stop-hook.sh (TDD - written before the hook
script is restored/implemented).

Contract under test:
  - Reads a JSON blob from stdin (must not block / must be consumed).
  - Maintains a plain-text integer counter at
    .claude/hooks/session-turn-count.txt (relative to repo root / hook dir,
    shared across the whole repo, NOT session-keyed -- that's intentional).
  - Increments the counter by 1 on every invocation.
  - On turns where count % 10 == 0, emits exactly one line of JSON on stdout:
        {"systemMessage": "\U0001F4A1 <tip text>"}
    where <tip text> is a line pulled (at random) from the non-comment,
    non-blank lines of framework-tips.txt.
  - On all other turns, produces NO stdout output and exits 0.

This test NEVER touches the real repo's counter file. It copies stop-hook.sh
and framework-tips.txt into an isolated temp directory (preserving the
.claude/hooks/ relative layout, in case the script locates its sibling files
via $(dirname "$0")) and runs the script from there, with the temp directory
as cwd, so any counter file the script creates lands only in the temp tree.

Usage:
    python3 test_stop_hook.py

Exit code 0 = all assertions passed. Non-zero = failure (with details printed).
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path("/home/raymorris/Documents/planes/inavflight")
REAL_HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"
REAL_SCRIPT = REAL_HOOKS_DIR / "stop-hook.sh"
REAL_TIPS = REAL_HOOKS_DIR / "framework-tips.txt"

STDIN_PAYLOAD = json.dumps(
    {
        "transcript_path": "/tmp/fake.jsonl",
        "session_id": "test-session",
        "hook_event_name": "Stop",
    }
).encode("utf-8")

TURN_INTERVAL = 10
TOTAL_TURNS_TO_EXERCISE = 20  # covers two full cycles (turn 10 and turn 20)

failures = []


def fail(msg):
    failures.append(msg)
    print(f"FAIL: {msg}")


def ok(msg):
    print(f"OK:   {msg}")


def load_tip_lines(tips_path: Path):
    lines = []
    for raw in tips_path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return lines


def main():
    # --- Pre-flight: confirm the real script exists before we even try the
    # isolated run. This gives a crisp, explicit failure mode when the hook
    # has been deleted (the expected state at the start of this TDD cycle).
    if not REAL_SCRIPT.exists():
        print(
            f"FAIL: script not found at {REAL_SCRIPT} "
            "(expected during TDD red phase -- implement stop-hook.sh to make this pass)"
        )
        sys.exit(1)

    if not REAL_TIPS.exists():
        print(f"FAIL: tips file not found at {REAL_TIPS}")
        sys.exit(1)

    tip_lines = load_tip_lines(REAL_TIPS)
    if not tip_lines:
        print(f"FAIL: no usable (non-comment, non-blank) tip lines found in {REAL_TIPS}")
        sys.exit(1)
    ok(f"real stop-hook.sh found at {REAL_SCRIPT}")
    ok(f"loaded {len(tip_lines)} candidate tip lines from framework-tips.txt")

    # --- Build isolated temp copy, preserving .claude/hooks/ relative layout.
    with tempfile.TemporaryDirectory(prefix="stop-hook-test-") as tmp:
        tmp_root = Path(tmp)
        tmp_hooks_dir = tmp_root / ".claude" / "hooks"
        tmp_hooks_dir.mkdir(parents=True, exist_ok=True)

        tmp_script = tmp_hooks_dir / "stop-hook.sh"
        tmp_tips = tmp_hooks_dir / "framework-tips.txt"
        shutil.copy2(REAL_SCRIPT, tmp_script)
        shutil.copy2(REAL_TIPS, tmp_tips)
        tmp_script.chmod(0o755)

        counter_file = tmp_hooks_dir / "session-turn-count.txt"
        if counter_file.exists():
            fail(f"counter file already present in fresh temp dir: {counter_file}")

        ok(f"isolated copy created at {tmp_hooks_dir} (cwd will be {tmp_root})")

        for turn in range(1, TOTAL_TURNS_TO_EXERCISE + 1):
            try:
                proc = subprocess.run(
                    [str(tmp_script)],
                    input=STDIN_PAYLOAD,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(tmp_root),
                    timeout=10,
                )
            except subprocess.TimeoutExpired:
                fail(f"turn {turn}: script timed out (did not consume stdin / hung)")
                continue
            except FileNotFoundError as e:
                fail(f"turn {turn}: script not found / not executable: {e}")
                continue

            stdout_text = proc.stdout.decode("utf-8", errors="replace")
            stderr_text = proc.stderr.decode("utf-8", errors="replace")

            if proc.returncode != 0:
                fail(
                    f"turn {turn}: expected exit code 0, got {proc.returncode} "
                    f"(stderr: {stderr_text!r})"
                )

            should_fire = (turn % TURN_INTERVAL) == 0

            if should_fire:
                if not stdout_text.strip():
                    fail(f"turn {turn}: expected a tip (multiple of {TURN_INTERVAL}) but got no stdout output")
                    continue
                try:
                    payload = json.loads(stdout_text.strip())
                except json.JSONDecodeError as e:
                    fail(f"turn {turn}: stdout was not valid JSON: {stdout_text!r} ({e})")
                    continue

                if "systemMessage" not in payload:
                    fail(f"turn {turn}: JSON output missing 'systemMessage' key: {payload!r}")
                    continue

                msg = payload["systemMessage"]
                if not isinstance(msg, str) or not msg.startswith("\U0001F4A1 "):
                    fail(
                        f"turn {turn}: systemMessage does not start with the tip "
                        f"emoji prefix '\U0001F4A1 ': {msg!r}"
                    )
                    continue

                tip_text = msg[len("\U0001F4A1 "):]
                if tip_text not in tip_lines:
                    fail(
                        f"turn {turn}: tip text not found among framework-tips.txt "
                        f"lines: {tip_text!r}"
                    )
                    continue

                ok(f"turn {turn}: fired tip correctly -> {msg!r}")
            else:
                if stdout_text.strip():
                    fail(
                        f"turn {turn}: expected NO stdout output (not a multiple of "
                        f"{TURN_INTERVAL}) but got: {stdout_text!r}"
                    )
                    continue
                ok(f"turn {turn}: silent as expected")

        # Sanity check: counter file should exist and equal TOTAL_TURNS_TO_EXERCISE.
        if counter_file.exists():
            content = counter_file.read_text(encoding="utf-8").strip()
            try:
                count_val = int(content)
            except ValueError:
                fail(f"counter file content is not an integer: {content!r}")
            else:
                if count_val != TOTAL_TURNS_TO_EXERCISE:
                    fail(
                        f"counter file value {count_val} != expected "
                        f"{TOTAL_TURNS_TO_EXERCISE} after {TOTAL_TURNS_TO_EXERCISE} invocations"
                    )
                else:
                    ok(f"counter file correctly reads {count_val} after {TOTAL_TURNS_TO_EXERCISE} turns")
        else:
            fail(f"counter file was never created at {counter_file}")

    # --- Final verdict.
    print()
    if failures:
        print(f"RESULT: FAILED ({len(failures)} assertion(s) failed)")
        sys.exit(1)
    else:
        print("RESULT: PASSED (all assertions succeeded)")
        sys.exit(0)


if __name__ == "__main__":
    main()
