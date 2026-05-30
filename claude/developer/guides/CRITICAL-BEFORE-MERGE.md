# ⚠️ CRITICAL CHECKLIST - Read Before Resolving Merge Conflicts

**STOP! Read this entire guide before touching any merge conflict.**

The most expensive mistake in merge work is taking a whole file or whole function
from one branch instead of applying only the *changes* that branch made.
This silently drops everything the other branch added — bugs that are invisible
in diffs and burn enormous debugging time to trace.

---

## MERGE, Not Rebase

> **Always resolve conflicts with `git merge`, never `git rebase`.**

**Why this matters:**
- Rebase rewrites the PR author's commit history (new SHAs) and requires `--force-with-lease` to push — which is blocked by project rules.
- A merge commit adds a *new* commit on top of the PR branch, preserving the author's commits exactly and pushing normally without force.

**The workflow:**
```bash
# Start from the PR branch (not from base)
git checkout -b resolve-conflict-pr-XXXX shota3527/their-branch

# Merge the base branch INTO the PR branch (creates a new merge commit)
git merge upstream/maintenance-9.x --no-ff -m "Merge upstream/maintenance-9.x to resolve conflicts with PR #XXXX"
# Resolve conflicts, then:
git add <files>
git commit --no-edit

# Push normally — no force needed
git push shota3527 HEAD:their-branch
```

**Never do this:**
```bash
# ❌ This rewrites history and requires force push
git rebase upstream/maintenance-9.x
```

---

## The Core Rule: Apply Changes, Not Files

> **Always apply a branch's DIFF to the other branch's files.
> Never replace a file (or a function) wholesale with a version from another branch.**

This applies at every level of granularity:
- ❌ `git show pr-branch:file.js > file.js` — copies entire file
- ❌ Copy-pasting an entire function from the PR into the base file
- ✅ Identify the specific lines the PR added/changed, apply only those edits

Copy-pasting a whole function has the exact same problem as copying a whole file:
it silently loses whatever the base branch added to that function after the PR diverged.

---

## Before Starting Any Merge

### 1. Identify the correct base and incoming branches

```bash
# Base = the branch being merged INTO (e.g. maintenance-9.x)
# Incoming = the PR branch (e.g. scavanger/tab-modules)
git log --oneline base-branch..incoming-branch  # What the PR adds
git log --oneline incoming-branch..base-branch  # What base added since divergence
```

### 2. Find the common ancestor

```bash
git merge-base incoming-branch base-branch
# This is the point where both branches diverged — the "before" state
```

### 3. For each conflicting file, understand BOTH sides

```bash
# What the PR changed in this file:
git diff $(git merge-base incoming base):path/to/file incoming-branch:path/to/file

# What the base added in this file since divergence:
git diff $(git merge-base incoming base):path/to/file base-branch:path/to/file
```

---

## Resolving Each Conflict

### For simple rename/refactor files (e.g. TABS.foo → fooTab)

1. Take the BASE BRANCH version of the file
2. Apply only the rename transformation (sed, python, or manual)
3. Do NOT copy the PR's version — it may be missing base-branch additions

```bash
# RIGHT: start from base, apply rename
git show base-branch:tabs/foo.js > tabs/foo.js
sed -i 's/TABS\.foo\./fooTab\./g' tabs/foo.js
```

### For files with logic additions on both sides

1. Take the BASE BRANCH version of the file as the starting point
2. Diff the PR to find exactly what it changed:
   ```bash
   git diff <common-ancestor> incoming-branch -- path/to/file
   ```
3. Apply only those specific hunks to the base file using Edit tool
4. Do NOT replace entire functions — find the specific lines that changed

### For conflict markers (<<<< ==== >>>>)

When merging base INTO the PR branch (the correct approach):
- `HEAD` = PR branch (the author's code)
- `Incoming` = base branch (maintenance-9.x)
- Resolution = base content + the PR's additions applied on top

---

## After Resolving

### Verify no features were silently dropped

```bash
# For each resolved file, diff against the base branch
# Lines starting with '-' are base-branch features we may have dropped
git diff base-branch HEAD -- path/to/file | grep "^-[^-]" | head -30

# A large number of '-' lines (beyond expected renames) is a red flag
```

### Check for missing imports/functions

```bash
# Find all function calls in the resolved files
# Verify each called function actually exists somewhere
grep -rn "GUI\.\|someModule\." tabs/ js/ --include="*.js" | \
  grep -v "node_modules" | \
  awk '{print $2}' | sort -u
```

### Run a syntax check before committing

```bash
for f in tabs/*.js js/*.js; do
  node --input-type=module < "$f" 2>&1 | grep "SyntaxError" && echo "ERROR in $f"
done
```

---

## Common Mistakes and Their Symptoms

| Mistake | Symptom |
|---------|---------|
| Used `git rebase` instead of `git merge` | Force push required — blocked by project rules; author's commits rewritten |
| Replaced entire file with PR version | Runtime errors for functions added by base branch after divergence |
| Replaced entire function | Same — missing logic added to that function by base branch |
| Resolved conflict by taking PR side only | Missing base-branch features in that code block |
| Kept conflict markers (`>>>>>>>`) | Parse/syntax error from bundler |
| Forgot to check `js/` files (not just `tabs/`) | `is not a function` errors for helper functions defined in main JS files |

---

## Checklist

Before marking a merge complete:

- [ ] Every resolved file diffed against base branch — no unexpected `-` lines
- [ ] Syntax check passed on all modified JS files
- [ ] No remaining `<<<<<<<`, `=======`, `>>>>>>>` markers in any file
- [ ] All function calls resolve to actual definitions (no "is not a function" errors)
- [ ] App loads and all tabs render without console errors
- [ ] Connected FC: key new PR features tested manually
