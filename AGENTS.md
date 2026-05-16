# INAV Project - OpenCode Configuration

<!-- First action required -->
Ask the user: "Which role should I take on today - Manager, Developer, Release Manager, or Security Analyst?"

After they respond, read:
- Manager: `claude/manager/README.md`
- Developer: `claude/developer/README.md`
- Release Manager: `claude/release-manager/README.md`
- Security Analyst: `claude/security-analyst/README.md`

---

## Project Overview

## Project Structure

- **inav/** - Flight controller firmware (C/C99, embedded systems)
- **inav-configurator/** - Desktop configuration GUI (JavaScript/Electron)
- **inavwiki/** - Documentation wiki (Markdown)
- **PrivacyLRS/** - Privacy-focused Long Range System

## Custom Agents

This project has custom agents for specialized tasks. Use `@agent-name` to invoke:

- `@inav-architecture` - Find INAV firmware code locations
- `@msp-expert` - MSP protocol expertise
- `@inav-builder` - Build firmware and configurator
- `@test-engineer` - Testing and bug reproduction
- `@fc-flasher` - Flash firmware to flight controllers
- `@sitl-operator` - SITL operations
- `@inav-code-review` - Code review before PRs
- `@check-pr-bots` - Check PR status and CI
- `@settings-lookup` - CLI settings lookup
- `@target-developer` - Target-specific fixes

## Available Skills

Use `/skill-name` to invoke:

- `/start-task` - Lock acquisition, branch setup
- `/git-workflow` - Branch management
- `/create-pr` - Create pull requests
- `/finish-task` - Complete tasks
- `/build-sitl` - Build SITL
- `/build-inav-target` - Build specific target

## Role System

This project uses a role-based workflow:

- **Manager** - Project tracking and task assignment
- **Developer** - Code implementation
- **Release Manager** - Release artifacts
- **Security Analyst** - Security review

See `claude/*/README.md` for role-specific workflows.

## Documentation

- `claude/docs/MIGRATION.md` - Guide for porting from Claude Code
- `claude/developer/README.md` - Developer workflow

## Key Files

- `.claude/` - Claude Code configuration (upstream)
- `.opencode/` - OpenCode configuration (this project)
- `opencode.json` - Root OpenCode settings

## Code Navigation with ctags

Both codebases have ctags indexes for quick symbol lookup.

**Using the /find-symbol command:**
```
/find-symbol pidController
/find-symbol navConfig
```

**Manual ctags lookup:**
```bash
# Find a C function in firmware
grep "^functionName\b" inav/tags

# Find a JS symbol in configurator
grep "^symbolName\b" inav-configurator/tags
```

**Regenerating indexes when source files change:**
```bash
# Firmware (C code)
cd inav && ctags -R --fields=+niazS --extras=+q --exclude=lib --exclude=build --exclude=tools --exclude=.git -f tags .

# Configurator (JS code)
cd inav-configurator && ctags -R --fields=+niazS --extras=+q --exclude=node_modules --exclude=.git --exclude=out --exclude=.vite --exclude=dist -f tags .
```

## Main Documentation

- `claude/projects/INDEX.md` - Active project tracking
- `claude/projects/completed/INDEX.md` - Completed projects
- Role-specific guides: `claude/*/README.md`