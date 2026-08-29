#!/usr/bin/env python3
"""
Regression test for .claude/hooks/check-framework-update.sh, formalizing
manual verification of the hook's cadence/throttle logic AND its
remote-selection / "already caught up locally" shortcut logic.

Contract under test:
  - Reads/drains a JSON blob from stdin (must not block / must be consumed).
  - PROJECT_ROOT is computed as two directories up from the script's own
    location, i.e. the script expects to live at
    <root>/.claude/hooks/check-framework-update.sh and reads
    <root>/.git/FETCH_HEAD's mtime as the "days since last fetch/pull" signal.
  - No FETCH_HEAD at all -> silent (no stdout), exit 0.
  - FETCH_HEAD age < 30 days -> silent, exit 0.
  - FETCH_HEAD age >= 30 days (overdue):
      - Picks UPDATE_REMOTE = "upstream" if `git remote get-url upstream`
        succeeds, else "origin".
      - Runs `git rev-list HEAD..$UPDATE_REMOTE/master --count`. If that
        parses as exactly 0, the hook stays SILENT even though FETCH_HEAD is
        stale (local HEAD already has everything the remote-tracking ref
        knows about). If it's nonzero, or the command fails/produces
        unparseable output (e.g. remote-tracking ref doesn't exist locally),
        the hook falls through to the ask/throttle logic below.
      - Checks a marker file last-framework-update-ask.txt (sibling of the
        script, i.e. <root>/.claude/hooks/last-framework-update-ask.txt)
        whose *content* (not mtime) is a plain decimal Unix epoch of when
        the hook last emitted the prompt.
      - If that stored epoch is < 7 days old -> silent, exit 0 (throttled).
      - Otherwise -> emits exactly one line of JSON on stdout:
            {"systemMessage": "<text mentioning day count, the chosen
             remote, and a 'git pull --ff-only <remote> master' command>"}
        and overwrites the marker file with the current epoch.
  - Exit code is 0 in all cases.

ISOLATION NOTE (important, previously a real bug in this test):
This environment sets $TMPDIR to a directory INSIDE this project's own git
working tree. tempfile.mkdtemp() honors $TMPDIR by default, so a naive
"isolated" temp dir actually lives inside the real repo's working tree. If
that temp dir's ".git" is not a genuine, complete git repository (e.g. just
a hand-crafted FETCH_HEAD file with no HEAD/objects/refs/config), git does
NOT treat it as a repo boundary and silently walks UP past it to the real
project repo -- so any `git` subcommand the hook shells out to ends up
operating on the REAL repo instead of the fixture.

Fix applied here, belt-and-suspenders:
  1. Every temp container is created under /tmp explicitly (dir="/tmp"),
     bypassing $TMPDIR entirely.
  2. Every fixture "repo" is a REAL git repository made via `git init` plus
     a real commit, so it has a valid HEAD/objects/refs/config and forms a
     genuine repo boundary that stops git's upward directory walk. This also
     lets us set up real origin/upstream remotes and real remote-tracking
     refs (refs/remotes/<name>/master) via actual `git fetch`, which the new
     hook logic depends on.
  3. .git/FETCH_HEAD's age is still controlled manually via os.utime(), since
     the hook only cares about its mtime, not its content -- but we set that
     mtime LAST, after all real clone/fetch/push setup, so our fetches don't
     stomp the deliberately-aged mtime.

This test NEVER touches the real repo's .git directory or the real
.claude/hooks/last-framework-update-ask.txt.

Usage:
    python3 test_check_framework_update.py

Exit code 0 = all assertions passed. Non-zero = failure (with details printed).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / ".claude" / "hooks").is_dir()
)
REAL_HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"
REAL_SCRIPT = REAL_HOOKS_DIR / "check-framework-update.sh"

UPDATE_INTERVAL_DAYS = 30
REASK_INTERVAL_DAYS = 7
DAY_SECONDS = 86400

STDIN_PAYLOAD = json.dumps(
    {
        "session_id": "test-session",
        "hook_event_name": "SessionStart",
    }
).encode("utf-8")

failures = []


def fail(msg):
    failures.append(msg)
    print(f"FAIL: {msg}")


def ok(msg):
    print(f"OK:   {msg}")


# ---------------------------------------------------------------------------
# Git fixture helpers -- all real git repos, all forced under /tmp.
# ---------------------------------------------------------------------------

def git_cmd(args, cwd, check=True):
    proc = subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=15,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} (cwd={cwd}) failed rc={proc.returncode}\n"
            f"stdout={proc.stdout.decode(errors='replace')!r}\n"
            f"stderr={proc.stderr.decode(errors='replace')!r}"
        )
    return proc


def new_container():
    """A fresh scratch dir under /tmp (never under $TMPDIR) to hold one
    test case's repo + any bare remotes + scratch clones."""
    return Path(tempfile.mkdtemp(prefix="check-framework-update-test-", dir="/tmp"))


def init_real_repo(path: Path):
    """git init a REAL repo at `path` with one commit on branch 'master',
    so it has a genuine HEAD/objects/refs/config (a real repo boundary)."""
    path.mkdir(parents=True, exist_ok=True)
    git_cmd(["init", "-q", "-b", "master"], path)
    git_cmd(["config", "user.email", "test@test"], path)
    git_cmd(["config", "user.name", "test"], path)
    git_cmd(["config", "commit.gpgsign", "false"], path)
    (path / "README.md").write_text("init\n")
    git_cmd(["add", "."], path)
    git_cmd(["commit", "-q", "-m", "initial commit"], path)


def setup_local_repo(container: Path):
    """Build the <root>/.claude/hooks/check-framework-update.sh layout on
    top of a real git repo. Returns (tmp_root, tmp_script, fetch_head, marker)."""
    tmp_root = container / "repo"
    tmp_hooks_dir = tmp_root / ".claude" / "hooks"
    tmp_hooks_dir.mkdir(parents=True, exist_ok=True)
    init_real_repo(tmp_root)

    tmp_script = tmp_hooks_dir / "check-framework-update.sh"
    shutil.copy2(REAL_SCRIPT, tmp_script)
    tmp_script.chmod(0o755)

    fetch_head = tmp_root / ".git" / "FETCH_HEAD"
    marker = tmp_hooks_dir / "last-framework-update-ask.txt"
    return tmp_root, tmp_script, fetch_head, marker


def make_bare_from(src_repo: Path, dest_bare: Path):
    """Create a bare repo at dest_bare whose master tip == src_repo's
    current HEAD (a stand-in 'remote')."""
    git_cmd(["clone", "-q", "--bare", str(src_repo), str(dest_bare)], src_repo.parent)


def add_remote_and_fetch(repo: Path, name: str, url: Path, fetch=True):
    git_cmd(["remote", "add", name, str(url)], repo)
    if fetch:
        git_cmd(["fetch", "-q", name], repo)


def add_commit_to_bare(bare: Path, container: Path, tag: str):
    """Advance a bare 'remote' repo's master by one commit, via a throwaway
    working clone + push (you can't commit directly into a bare repo)."""
    scratch = container / f"scratch-{tag}"
    git_cmd(["clone", "-q", str(bare), str(scratch)], container)
    git_cmd(["config", "user.email", "test@test"], scratch)
    git_cmd(["config", "user.name", "test"], scratch)
    git_cmd(["config", "commit.gpgsign", "false"], scratch)
    (scratch / f"{tag}.txt").write_text(f"{tag} update\n")
    git_cmd(["add", "."], scratch)
    git_cmd(["commit", "-q", "-m", f"extra commit {tag}"], scratch)
    git_cmd(["push", "-q", "origin", "HEAD:master"], scratch)
    shutil.rmtree(scratch, ignore_errors=True)


def set_fetch_head_age_days(fetch_head: Path, age_days: float):
    """Set (creating if necessary) FETCH_HEAD's mtime to simulate staleness.
    Must be called AFTER any real `git fetch` setup, since fetch itself
    rewrites FETCH_HEAD with the current time."""
    fetch_head.parent.mkdir(parents=True, exist_ok=True)
    fetch_head.write_text("fake fetch head content\n", encoding="utf-8")
    mtime = time.time() - (age_days * DAY_SECONDS)
    os.utime(fetch_head, (mtime, mtime))


def run_hook(tmp_root: Path, tmp_script: Path):
    try:
        proc = subprocess.run(
            [str(tmp_script)],
            input=STDIN_PAYLOAD,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(tmp_root),
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return None
    return proc


def assert_silent(proc, case_label):
    if proc is None:
        fail(f"{case_label}: script timed out (did not consume stdin / hung)")
        return False
    passed = True
    if proc.returncode != 0:
        fail(f"{case_label}: expected exit code 0, got {proc.returncode} (stderr: {proc.stderr!r})")
        passed = False
    stdout_text = proc.stdout.decode("utf-8", errors="replace")
    if stdout_text.strip():
        fail(f"{case_label}: expected NO stdout output but got: {stdout_text!r}")
        passed = False
    if passed:
        ok(f"{case_label}: silent as expected, exit 0")
    return passed


def assert_fires(proc, case_label, must_contain=None):
    if proc is None:
        fail(f"{case_label}: script timed out (did not consume stdin / hung)")
        return None
    if proc.returncode != 0:
        fail(f"{case_label}: expected exit code 0, got {proc.returncode} (stderr: {proc.stderr!r})")
        return None
    stdout_text = proc.stdout.decode("utf-8", errors="replace")
    if not stdout_text.strip():
        fail(f"{case_label}: expected a systemMessage prompt but got no stdout output "
             f"(stderr: {proc.stderr.decode(errors='replace')!r})")
        return None
    try:
        payload = json.loads(stdout_text.strip())
    except json.JSONDecodeError as e:
        fail(f"{case_label}: stdout was not valid JSON: {stdout_text!r} ({e})")
        return None
    if "systemMessage" not in payload:
        fail(f"{case_label}: JSON output missing 'systemMessage' key: {payload!r}")
        return None
    msg = payload["systemMessage"]
    if not isinstance(msg, str) or not msg.strip():
        fail(f"{case_label}: systemMessage is not a non-empty string: {msg!r}")
        return None
    if must_contain:
        for needle in must_contain:
            if needle not in msg:
                fail(f"{case_label}: expected systemMessage to contain {needle!r}, got: {msg!r}")
                return None
    ok(f"{case_label}: fired correctly -> {msg!r}")
    return msg


def main():
    if not REAL_SCRIPT.exists():
        fail(f"real script not found at {REAL_SCRIPT}")
        print()
        print("RESULT: FAILED (1 assertion(s) failed)")
        sys.exit(1)
    ok(f"real check-framework-update.sh found at {REAL_SCRIPT}")

    # =======================================================================
    # Original 7 cases: age/marker gating, no remotes configured at all.
    # With a real (remoteless) repo, `git remote get-url upstream` fails ->
    # UPDATE_REMOTE=origin -> `git rev-list HEAD..origin/master` fails (no
    # such remote) -> shortcut doesn't apply -> falls through exactly like
    # the pre-existing ask/throttle logic these cases were written for.
    # =======================================================================

    # --- Case 1: no FETCH_HEAD at all -> silent, exit 0 (fresh-clone case).
    container = new_container()
    try:
        tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
        if fetch_head.exists():
            fail("case1: FETCH_HEAD unexpectedly present in fresh repo")
        proc = run_hook(tmp_root, tmp_script)
        assert_silent(proc, "case1 (no FETCH_HEAD)")
        if marker.exists():
            fail("case1: marker file should not have been created")
    finally:
        shutil.rmtree(container, ignore_errors=True)

    # --- Case 2: FETCH_HEAD mtime = now (0 days old) -> silent, exit 0.
    container = new_container()
    try:
        tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
        set_fetch_head_age_days(fetch_head, 0)
        proc = run_hook(tmp_root, tmp_script)
        assert_silent(proc, "case2 (FETCH_HEAD 0 days old)")
        if marker.exists():
            fail("case2: marker file should not have been created")
    finally:
        shutil.rmtree(container, ignore_errors=True)

    # --- Case 3: FETCH_HEAD 35 days old, no marker yet -> fires; marker
    # created afterward with a plausible recent epoch. (container kept alive
    # for case 4, which continues from here.)
    container = new_container()
    case3_container = container
    tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
    try:
        set_fetch_head_age_days(fetch_head, 35)
        before = time.time()
        proc = run_hook(tmp_root, tmp_script)
        after = time.time()
        assert_fires(proc, "case3 (35 days old, no marker)")
        if not marker.exists():
            fail("case3: marker file was not created after firing")
        else:
            content = marker.read_text(encoding="utf-8").strip()
            try:
                stored_epoch = int(content)
            except ValueError:
                fail(f"case3: marker content is not a plain integer epoch: {content!r}")
            else:
                if not (before - 5 <= stored_epoch <= after + 5):
                    fail(
                        f"case3: marker epoch {stored_epoch} not within a few seconds "
                        f"of now (window {before:.0f}-{after:.0f})"
                    )
                else:
                    ok(f"case3: marker file created with plausible recent epoch {stored_epoch}")
    except Exception:
        shutil.rmtree(container, ignore_errors=True)
        raise

    # --- Case 4: same overdue FETCH_HEAD, run again immediately (marker now
    # says "just now") -> silent, exit 0 (throttled). Reuses case 3's repo/
    # marker on purpose, to exercise the "just asked" throttle state.
    try:
        proc = run_hook(tmp_root, tmp_script)
        assert_silent(proc, "case4 (immediate re-run, marker fresh)")
    finally:
        shutil.rmtree(case3_container, ignore_errors=True)

    # --- Case 5: overdue FETCH_HEAD, marker pre-written to 8 days in the
    # past -> fires again, exit 0.
    container = new_container()
    try:
        tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
        set_fetch_head_age_days(fetch_head, 35)
        marker_epoch = int(time.time() - 8 * DAY_SECONDS)
        marker.write_text(str(marker_epoch), encoding="utf-8")
        proc = run_hook(tmp_root, tmp_script)
        assert_fires(proc, "case5 (marker 8 days old, over reask threshold)")
    finally:
        shutil.rmtree(container, ignore_errors=True)

    # --- Case 6: overdue FETCH_HEAD, marker pre-written to 3 days in the
    # past -> silent, exit 0 (still within 7-day throttle window).
    container = new_container()
    try:
        tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
        set_fetch_head_age_days(fetch_head, 35)
        marker_epoch = int(time.time() - 3 * DAY_SECONDS)
        marker.write_text(str(marker_epoch), encoding="utf-8")
        proc = run_hook(tmp_root, tmp_script)
        assert_silent(proc, "case6 (marker 3 days old, under reask threshold)")
    finally:
        shutil.rmtree(container, ignore_errors=True)

    # --- Case 7: FETCH_HEAD exactly 29 days old (just under threshold) ->
    # silent, exit 0.
    container = new_container()
    try:
        tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
        set_fetch_head_age_days(fetch_head, UPDATE_INTERVAL_DAYS - 1)
        proc = run_hook(tmp_root, tmp_script)
        assert_silent(proc, "case7 (FETCH_HEAD 29 days old, just under threshold)")
        if marker.exists():
            fail("case7: marker file should not have been created")
    finally:
        shutil.rmtree(container, ignore_errors=True)

    # =======================================================================
    # New cases A-E: remote-selection (origin vs upstream) and the "0 behind
    # locally" shortcut that can suppress the ask despite stale FETCH_HEAD.
    # =======================================================================

    # --- Case A: only 'origin' configured, local HEAD == origin/master
    # (0 behind). FETCH_HEAD stale (35d), no marker.
    # Expect: SILENT -- the new shortcut overrides the stale-FETCH_HEAD ask.
    container = new_container()
    try:
        tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
        origin_bare = container / "origin.git"
        make_bare_from(tmp_root, origin_bare)
        add_remote_and_fetch(tmp_root, "origin", origin_bare)  # origin/master == HEAD
        set_fetch_head_age_days(fetch_head, 35)
        proc = run_hook(tmp_root, tmp_script)
        assert_silent(proc, "caseA (origin only, 0 behind origin/master)")
        if marker.exists():
            fail("caseA: marker file should not have been created (shortcut should suppress ask)")
    finally:
        shutil.rmtree(container, ignore_errors=True)

    # --- Case B: only 'origin' configured, origin/master (local tracking
    # ref) has a commit local HEAD lacks. FETCH_HEAD stale, no marker.
    # Expect: FIRES, systemMessage mentions "origin".
    container = new_container()
    try:
        tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
        origin_bare = container / "origin.git"
        make_bare_from(tmp_root, origin_bare)
        add_remote_and_fetch(tmp_root, "origin", origin_bare)
        add_commit_to_bare(origin_bare, container, "origin")  # origin now ahead by 1
        git_cmd(["fetch", "-q", "origin"], tmp_root)  # advance local tracking ref
        set_fetch_head_age_days(fetch_head, 35)
        proc = run_hook(tmp_root, tmp_script)
        msg = assert_fires(proc, "caseB (origin ahead by 1 commit)", must_contain=["origin"])
        if msg and "git pull --ff-only origin master" not in msg:
            fail(f"caseB: expected pull command to reference origin, got: {msg!r}")
        if not marker.exists():
            fail("caseB: marker file was not created after firing")
    finally:
        shutil.rmtree(container, ignore_errors=True)

    # --- Case C: BOTH 'origin' and 'upstream' configured. origin/master is
    # caught up (irrelevant), upstream/master has a commit local HEAD lacks.
    # Expect: FIRES, systemMessage mentions "upstream" (not origin), since
    # upstream takes priority over origin entirely.
    container = new_container()
    try:
        tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
        origin_bare = container / "origin.git"
        make_bare_from(tmp_root, origin_bare)
        add_remote_and_fetch(tmp_root, "origin", origin_bare)  # 0 behind, should be ignored

        upstream_bare = container / "upstream.git"
        make_bare_from(tmp_root, upstream_bare)
        add_remote_and_fetch(tmp_root, "upstream", upstream_bare)
        add_commit_to_bare(upstream_bare, container, "upstream")  # upstream ahead by 1
        git_cmd(["fetch", "-q", "upstream"], tmp_root)

        set_fetch_head_age_days(fetch_head, 35)
        proc = run_hook(tmp_root, tmp_script)
        msg = assert_fires(
            proc, "caseC (origin+upstream, upstream ahead)", must_contain=["upstream"]
        )
        if msg and "git pull --ff-only upstream master" not in msg:
            fail(f"caseC: expected pull command to reference upstream, got: {msg!r}")
    finally:
        shutil.rmtree(container, ignore_errors=True)

    # --- Case D: same as C but upstream/master is fully caught up (0
    # behind), while origin is deliberately made ahead to prove origin is
    # ignored entirely once upstream exists.
    # Expect: SILENT.
    container = new_container()
    try:
        tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
        origin_bare = container / "origin.git"
        make_bare_from(tmp_root, origin_bare)
        add_remote_and_fetch(tmp_root, "origin", origin_bare)
        add_commit_to_bare(origin_bare, container, "origin_d")  # origin ahead (should be ignored)
        git_cmd(["fetch", "-q", "origin"], tmp_root)

        upstream_bare = container / "upstream.git"
        make_bare_from(tmp_root, upstream_bare)  # tip == local HEAD still (unchanged)
        add_remote_and_fetch(tmp_root, "upstream", upstream_bare)  # 0 behind

        set_fetch_head_age_days(fetch_head, 35)
        proc = run_hook(tmp_root, tmp_script)
        assert_silent(proc, "caseD (upstream 0 behind, origin ahead but ignored)")
        if marker.exists():
            fail("caseD: marker file should not have been created (upstream shortcut should apply)")
    finally:
        shutil.rmtree(container, ignore_errors=True)

    # --- Case E: 'upstream' remote configured but NEVER fetched, so
    # refs/remotes/upstream/master doesn't exist locally. rev-list should
    # fail/produce unparseable output, so the shortcut must NOT apply, and
    # the hook must safely fall through to firing normally (no crash, no
    # wrongly-suppressed ask).
    container = new_container()
    try:
        tmp_root, tmp_script, fetch_head, marker = setup_local_repo(container)
        upstream_bare = container / "upstream.git"
        make_bare_from(tmp_root, upstream_bare)
        git_cmd(["remote", "add", "upstream", str(upstream_bare)], tmp_root)  # no fetch
        set_fetch_head_age_days(fetch_head, 35)
        proc = run_hook(tmp_root, tmp_script)
        assert_fires(
            proc,
            "caseE (upstream configured but never fetched, no remote-tracking ref)",
            must_contain=["upstream"],
        )
    finally:
        shutil.rmtree(container, ignore_errors=True)

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
