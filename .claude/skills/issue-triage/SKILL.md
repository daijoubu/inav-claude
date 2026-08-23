---
description: Triage and analyze GitHub issues from iNavFlight/inav and iNavFlight/inav-configurator
triggers:
  - triage issues
  - analyze issues
  - github issues
  - look at issues
  - review issues
  - readily solvable
  - fetch issues
---

# GitHub Issue Triage Skill

Systematically analyze and categorize GitHub issues from the iNavFlight/inav and
iNavFlight/inav-configurator repositories. Category files are shared across both
repos — issue numbers alone don't disambiguate, so each entry in INDEX.md and the
category files should note the repo (e.g. `inav #11710` vs `inav-configurator #2701`).

## File Structure

```
claude/manager/issue-triage/
  INDEX.md              # Quick lookup: issue# -> category file
  fetch_issues.py       # Script to fetch and search issues
  issues.json           # Cached issues data from GitHub
  readily-solvable.md   # Issues ready to fix
  needs-investigation.md
  documentation.md
  enhancement-simple.md
  enhancement-complex.md
  hardware-dependent.md
  no-action.md          # Won't fix, duplicates, already fixed
```

## Quick Commands

### Fetch Recent Issues Across Both Repos (preferred for periodic triage)

Uses GitHub's Search API to filter by creation date server-side — much cheaper
than paging through the entire open-issue backlog when you only care about a
recent window (e.g. "what's new in the last 90 days").

```bash
cd claude/manager/issue-triage
python3 fetch_issues.py --repo inav,inav-configurator --days 90 --refresh
```

### Refresh Issue Cache (single repo, all open issues)

```bash
python3 fetch_issues.py --refresh
python3 fetch_issues.py --repo inav-configurator --refresh
```

### Fetch More Issues

```bash
python3 fetch_issues.py --pages 5 --refresh
```

### View Specific Issue

```bash
python3 fetch_issues.py --issue 11156
python3 fetch_issues.py --issue 2701 --repo inav-configurator
```

### Search Issues

```bash
python3 fetch_issues.py --search "GPS"
python3 fetch_issues.py --search "overflow"
```

### List Cached Issues

```bash
python3 fetch_issues.py
```

`--repo` accepts a comma-separated list; each entry is either shorthand
(`inav`, `inav-configurator`, expanded to `iNavFlight/<name>`) or a full
`owner/name`. Default is `inav`.

## Categories

| Category | File | Description |
|----------|------|-------------|
| Readily Solvable | `readily-solvable.md` | Clear problem, known solution |
| Needs Investigation | `needs-investigation.md` | Promising, needs analysis |
| Documentation | `documentation.md` | Docs fixes/improvements |
| Enhancement (Simple) | `enhancement-simple.md` | Small feature additions |
| Enhancement (Complex) | `enhancement-complex.md` | Major feature work |
| Hardware Dependent | `hardware-dependent.md` | Needs specific hardware |
| No Action | `no-action.md` | Won't fix, duplicates, etc. |

## Workflow

1. **Refresh cache:** `python3 fetch_issues.py --refresh`
2. **Review list** for promising issues
3. **View details:** `python3 fetch_issues.py --issue XXXXX`
4. **Add to INDEX.md** with category link
5. **Add details** to appropriate category file

## Finding Readily Solvable Issues

Look for:
- Clear reproduction steps
- Isolated, specific problem
- No special hardware required
- Community consensus on behavior
- Small code changes

Avoid:
- Architecture changes needed
- Hardware-specific (can't test)
- Unclear requirements
