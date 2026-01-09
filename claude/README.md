# Claude Workspace

This directory contains organizational structures, communication channels, and documentation for Claude Code when working on the INAV codebase.

## Your Role

**Which role are you taking on?**

### 🎯 Development Manager

**You coordinate, track, and assign work.**

📖 **Read your guide:** [`claude/manager/README.md`](manager/README.md)

**Quick actions:**
- Check inbox: `ls claude/manager/email/inbox/`
- View active projects: `cat claude/projects/INDEX.md`
- Assign tasks: Create in `manager/email/sent/`, copy to `developer/email/inbox/`

---

### 💻 Developer

**You implement code based on manager assignments.**

📖 **Read your guide:** [`claude/developer/README.md`](developer/README.md)

**Quick actions:**
- Check inbox: `ls claude/developer/email/inbox/`
- Build firmware: `cd inav && ./build.sh TARGETNAME`
- Build configurator: `cd inav-configurator && npm start`
- Report completion: Create in `developer/email/sent/`, copy to `manager/email/inbox/`

---

### 📦 Release Manager

**You handle tagging, building, and publishing releases.**

📖 **Read your guide:** [`claude/release-manager/README.md`](release-manager/README.md)

**Quick actions:**
- Check latest tags: `git tag --sort=-v:refname | head -5`
- List PRs since tag: `gh pr list --state merged --limit 50`
- Create draft release: `gh release create X.Y.Z --draft`
- Build firmware: `cd inav && mkdir build && cd build && cmake .. && make`
- Build configurator: `cd inav-configurator && npm run dist`

---

## Directory Structure

```
claude/
├── manager/              - Development manager files
│   ├── README.md        - Manager role guide ⭐ START HERE if you're the manager
│   └── email/           - Email communication
│       ├── inbox/       - Reports from developer
│       ├── inbox-archive/ - Archived reports
│       ├── outbox/      - Draft messages
│       └── sent/        - Tasks sent to developer
│
├── developer/            - Developer files
│   ├── README.md        - Developer role guide ⭐ START HERE if you're the developer
│   ├── workspace/       - Active task working directories (gitignored)
│   └── email/           - Email communication
│       ├── inbox/       - Tasks from manager
│       ├── inbox-archive/ - Archived assignments
│       ├── outbox/      - Draft messages
│       └── sent/        - Reports to manager
│
├── release-manager/      - Release manager files
│   ├── README.md        - Release manager guide ⭐ START HERE if you're releasing
│   ├── releases/        - Release notes and changelogs
│   └── email/           - Email communication
│       ├── inbox/       - Incoming messages
│       ├── inbox-archive/ - Archived messages
│       ├── outbox/      - Draft messages
│       └── sent/        - Outgoing messages
│
├── projects/             - Active project tracking (manager-owned)
│   ├── INDEX.md         - Master project tracking
│   └── <project-name>/  - Individual project directories
│       ├── summary.md
│       └── todo.md
│
├── archived_projects/    - Completed/cancelled projects
│
└── README.md            - This file
```

## Communication Flow

```
Manager creates task
    ↓
manager/email/sent/ → copy → developer/email/inbox/
                            ↓
                    Developer reads & implements
                            ↓
developer/email/sent/ → copy → manager/email/inbox/
    ↓
Manager reviews & archives
```

## Project Tracking

All projects are tracked in **`claude/projects/INDEX.md`**

- View active projects: `grep "^### 🚧" claude/projects/INDEX.md`
- View completed: `grep "^### ✅" claude/projects/INDEX.md`
- View backburner: `grep "^### ⏸️" claude/projects/INDEX.md`

## Key Principles

### Role Separation

**Manager:**
- ✅ Creates projects and tracks progress
- ✅ Assigns tasks via email
- ✅ Updates INDEX.md
- ✅ Archives completed work
- ❌ Never edits source code

**Developer:**
- ✅ Implements assigned tasks
- ✅ Writes and tests code
- ✅ Reports completion
- ✅ Asks questions when unclear
- ❌ Never directly updates INDEX.md or project tracking

**Release Manager:**
- ✅ Creates version tags in both repos
- ✅ Generates changelogs from merged PRs
- ✅ Builds firmware and configurator
- ✅ Creates and publishes GitHub releases
- ❌ Never modifies source code (only builds it)

### Communication Protocol

1. **Assignments flow:** manager → developer
2. **Reports flow:** developer → manager
3. **All communication** uses the email system (sent/inbox folders)
4. **Archive processed messages** to keep inboxes clean

### Project Lifecycle

```
TODO → IN PROGRESS → COMPLETED → Archived
             ↓
          BACKBURNER (paused)
             ↓
        CANCELLED (abandoned)
```

## Quick Reference

### Manager Commands

```bash
# Check for completion reports
ls -lt claude/manager/email/inbox/

# View active projects
grep "Status: IN PROGRESS" claude/projects/*/summary.md

# Archive completed project
mv claude/projects/<name> claude/archived_projects/

# Archive completion report
mv claude/manager/email/inbox/<report>.md claude/manager/email/inbox-archive/
```

### Developer Commands

```bash
# Check for new assignments
ls -lt claude/developer/email/inbox/

# Send completion report
cp claude/developer/email/sent/<report>.md claude/manager/email/inbox/

# Archive processed assignment
mv claude/developer/email/inbox/<task>.md claude/developer/email/inbox-archive/

# Build & test
cd inav && ./build.sh TARGETNAME
cd inav-configurator && npm test
```

## Initial Setup

After cloning this repository, you need to update the settings files with your actual home directory path.

**Required:** Replace `/home/user/` with your actual home directory in these files:
- `.claude/settings.json` - Hook script paths
- `.claude/settings.local.json` - Permission rules (if it exists)

```bash
# Example for Linux/macOS:
sed -i "s|/home/user/|$HOME/|g" .claude/settings.json
sed -i "s|/home/user/|$HOME/|g" .claude/settings.local.json 2>/dev/null || true
```

The hook scripts need absolute paths to work correctly with Claude Code.

---

## Getting Started

1. **Determine your role** (Manager, Developer, or Release Manager)
2. **Read your role-specific README:**
   - Manager: [`claude/manager/README.md`](manager/README.md)
   - Developer: [`claude/developer/README.md`](developer/README.md)
   - Release Manager: [`claude/release-manager/README.md`](release-manager/README.md)
3. Tell your human which role you have detected and ask them if you should read your inbox now
4. **Start working** according to your role

---

## Need Help?

- **Manager guide:** `claude/manager/README.md` - Project management, task assignment, tracking
- **Developer guide:** `claude/developer/README.md` - Building, testing, coding standards, architecture
- **Release Manager guide:** `claude/release-manager/README.md` - Tagging, building, publishing releases
- **Project index:** `claude/projects/INDEX.md` - All project status and tracking

**Remember:** Read your role-specific README for detailed instructions!
