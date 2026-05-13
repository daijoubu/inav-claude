#!/usr/bin/env python3
"""
Set GitHub milestone on PRs merged into a branch after a specific release.

Finds all PRs merged into --branch after the --since-tag release date, then
sets them to --milestone. If a PR already has a different milestone, prompts
before changing it.

Usage:
    # Both repos (firmware + configurator):
    python3 set-pr-milestones.py --branch maintenance-9.x --milestone 9.1 --since-tag 9.0.1

    # Single repo:
    python3 set-pr-milestones.py --branch maintenance-9.x --milestone 9.1 --since-tag 9.0.1 --repo inav
    python3 set-pr-milestones.py --branch maintenance-9.x --milestone 9.1 --since-tag 9.0.1 --repo inav-configurator

    # Use a date instead of a release tag:
    python3 set-pr-milestones.py --branch maintenance-9.x --milestone 9.1 --since-date 2026-02-14

    # Preview without making changes:
    python3 set-pr-milestones.py --branch maintenance-9.x --milestone 9.1 --since-tag 9.0.1 --dry-run

    # Auto-approve all changes including milestone overwrites:
    python3 set-pr-milestones.py --branch maintenance-9.x --milestone 9.1 --since-tag 9.0.1 --yes
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


OWNER = "iNavFlight"
REPOS = ["inav", "inav-configurator"]


def run_gh(args: list[str]) -> dict | list:
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True, text=True, check=True
    )
    # --paginate returns one JSON document per page concatenated; wrap into array
    text = result.stdout.strip()
    if text.startswith("[") and "][" in text:
        # Multiple pages: combine arrays
        import re
        arrays = re.findall(r'\[.*?\](?=\s*\[|\s*$)', text, re.DOTALL)
        combined = []
        for a in arrays:
            combined.extend(json.loads(a))
        return combined
    return json.loads(text)


def get_release_date(repo: str, tag: str) -> datetime:
    """Return the UTC publish datetime for a release tag."""
    try:
        data = run_gh(["release", "view", tag, "--repo", f"{OWNER}/{repo}",
                       "--json", "publishedAt"])
        return datetime.fromisoformat(data["publishedAt"].replace("Z", "+00:00"))
    except subprocess.CalledProcessError:
        print(f"  ERROR: Release tag '{tag}' not found in {OWNER}/{repo}.")
        print(f"  Use --since-date YYYY-MM-DD as an alternative.")
        sys.exit(1)


def get_milestone_number(repo: str, milestone_title: str) -> int:
    """Return the GitHub milestone number for the given title, creating it if needed."""
    # Check open milestones first, then closed
    for state in ("open", "closed"):
        data = run_gh(["api",
                       f"repos/{OWNER}/{repo}/milestones?state={state}&per_page=100",
                       "--paginate"])
        for m in data:
            if m["title"] == milestone_title:
                return m["number"]

    # Milestone doesn't exist — ask whether to create it
    print(f"\n  Milestone '{milestone_title}' not found in {OWNER}/{repo}.")
    choice = input("  Create it? [y/N]: ").strip().lower()
    if choice != "y":
        print("  Aborting.")
        sys.exit(1)

    data = run_gh(["api", "-X", "POST", f"repos/{OWNER}/{repo}/milestones",
                   "-f", f"title={milestone_title}"])
    print(f"  Created milestone '{milestone_title}' (#{data['number']})")
    return data["number"]


def get_merged_prs(repo: str, branch: str, since: datetime) -> list[dict]:
    """Return PRs merged into branch after since, newest first."""
    data = run_gh([
        "pr", "list",
        "--repo", f"{OWNER}/{repo}",
        "--base", branch,
        "--state", "merged",
        "--limit", "500",
        "--json", "number,title,milestone,mergedAt,url",
    ])

    result = []
    for pr in data:
        merged_at = datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
        if merged_at > since:
            pr["mergedAt_dt"] = merged_at
            result.append(pr)

    # Oldest first so the user works through them in chronological order
    result.sort(key=lambda p: p["mergedAt_dt"])
    return result


def set_milestone(repo: str, pr_number: int, milestone_number: int, dry_run: bool) -> bool:
    """Set the milestone on a PR. Returns True on success."""
    if dry_run:
        return True
    try:
        run_gh(["api", "-X", "PATCH",
                f"repos/{OWNER}/{repo}/issues/{pr_number}",
                "-F", f"milestone={milestone_number}"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR setting milestone: {e}")
        return False


def prompt_overwrite(repo: str, pr: dict, current_title: str, new_title: str) -> str:
    """
    Ask the user what to do when a PR already has a different milestone.
    Returns: 'y' (yes), 'n' (no/skip), 'a' (yes to all), 'q' (quit)
    """
    print(f"\n  PR #{pr['number']} already has milestone '{current_title}'")
    print(f"  Title: {pr['title'][:72]}")
    print(f"  URL:   {pr['url']}")
    print(f"  Change '{current_title}' → '{new_title}'?")
    print("  [y] Yes  [n] Skip  [a] Yes to all remaining  [v] View in browser  [q] Quit")
    while True:
        choice = input("  Choice [y/n/a/v/q]: ").strip().lower()
        if choice in ("y", "n", "a", "q"):
            return choice
        if choice == "v":
            subprocess.run(["gh", "pr", "view", str(pr["number"]),
                            "--web", "--repo", f"{OWNER}/{repo}"])


def process_repo(
    repo: str,
    branch: str,
    milestone_title: str,
    since: datetime,
    dry_run: bool,
    auto_yes: bool,
) -> tuple[int, int, int]:
    """
    Process one repo. Returns (set_count, skipped_count, error_count).
    """
    print(f"\n{'=' * 70}")
    print(f"  Repository: {OWNER}/{repo}")
    print(f"  Branch:     {branch}")
    print(f"  Milestone:  {milestone_title}")
    print(f"  Since:      {since.strftime('%Y-%m-%d %H:%M UTC')}")
    if dry_run:
        print("  Mode:       DRY RUN — no changes will be made")
    print(f"{'=' * 70}")

    milestone_number = get_milestone_number(repo, milestone_title)

    print(f"\nFetching merged PRs...")
    prs = get_merged_prs(repo, branch, since)
    print(f"Found {len(prs)} PR(s) merged after the cutoff date.")

    if not prs:
        return 0, 0, 0

    set_count = skipped_count = error_count = 0
    overwrite_all = auto_yes  # tracks "yes to all" for conflict prompts

    for pr in prs:
        number = pr["number"]
        title = pr["title"][:65]
        merged = pr["mergedAt_dt"].strftime("%Y-%m-%d")
        current = pr.get("milestone") or {}
        current_title = current.get("title", "") if current else ""
        current_number = current.get("number") if current else None

        if current_number == milestone_number:
            # Already correct, nothing to do
            print(f"  [OK]   #{number} ({merged}) {title}")
            skipped_count += 1
            continue

        if current_title:
            # Has a different milestone — need confirmation
            if not overwrite_all:
                choice = prompt_overwrite(repo, pr, current_title, milestone_title)
                if choice == "q":
                    print("\nAborted by user.")
                    return set_count, skipped_count, error_count
                if choice == "n":
                    print(f"  [SKIP] #{number} ({merged}) {title}")
                    skipped_count += 1
                    continue
                if choice == "a":
                    overwrite_all = True
            # 'y' or overwrite_all: fall through to set
            action = "DRY-SET" if dry_run else "SET"
            print(f"  [{action}] #{number} ({merged}) {current_title!r} → {milestone_title!r}: {title}")
        else:
            action = "DRY-SET" if dry_run else "SET"
            print(f"  [{action}] #{number} ({merged}) {title}")

        if set_milestone(repo, number, milestone_number, dry_run):
            set_count += 1
        else:
            error_count += 1

    return set_count, skipped_count, error_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set milestone on PRs merged into a branch after a release.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--branch", required=True,
                        help="Branch to search (e.g., maintenance-9.x)")
    parser.add_argument("--milestone", required=True,
                        help="Milestone title to set (e.g., 9.1)")
    parser.add_argument("--repo", choices=REPOS,
                        help="Single repo to process (default: both)")

    since_group = parser.add_mutually_exclusive_group(required=True)
    since_group.add_argument("--since-tag",
                             help="Only include PRs merged after this release tag (e.g., 9.0.1)")
    since_group.add_argument("--since-date",
                             help="Only include PRs merged after this date (YYYY-MM-DD)")

    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without making any API calls")
    parser.add_argument("--yes", action="store_true",
                        help="Auto-approve all changes, including milestone overwrites")
    return parser.parse_args()


def main():
    args = parse_args()
    repos = [args.repo] if args.repo else REPOS

    # Resolve the cutoff date once; for per-repo tags we re-resolve inside the loop
    global_since = None
    if args.since_date:
        try:
            global_since = datetime.strptime(args.since_date, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            print(f"ERROR: --since-date must be YYYY-MM-DD, got: {args.since_date}")
            sys.exit(1)

    total_set = total_skipped = total_errors = 0

    for repo in repos:
        if args.since_tag:
            since = get_release_date(repo, args.since_tag)
        else:
            since = global_since

        s, sk, e = process_repo(
            repo=repo,
            branch=args.branch,
            milestone_title=args.milestone,
            since=since,
            dry_run=args.dry_run,
            auto_yes=args.yes,
        )
        total_set += s
        total_skipped += sk
        total_errors += e

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    if args.dry_run:
        print(f"  Would set:    {total_set}")
    else:
        print(f"  Set:          {total_set}")
    print(f"  Already done: {total_skipped}")
    if total_errors:
        print(f"  Errors:       {total_errors}")
    print()


if __name__ == "__main__":
    main()
