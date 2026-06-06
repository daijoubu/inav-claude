# OpenCode Startup - READ FIRST

**First:** Ask the user: "Which role should I take on today - Manager, Developer, Release Manager, or Security Analyst?"

Then read the role-specific README.md:
- Manager: `claude/manager/README.md`
- Developer: `claude/developer/README.md`
- Release Manager: `claude/release-manager/README.md`
- Security Analyst: `claude/security-analyst/README.md`

---

## Repository Overview

This is the INAV-Claude project - an AI-assisted development setup for INAV flight controller firmware.

**Components:**
1. **inav/** - Flight controller firmware (C/C99, embedded)
2. **inav-configurator/** - Desktop config GUI (JavaScript/Electron)
3. **inavwiki/** - Documentation wiki (Markdown)
4. **PrivacyLRS/** - Privacy-focused Long Range System

## Quick Reference

| Role | Workspace | Guide |
|------|-----------|-------|
| Manager | `claude/manager/` | `claude/manager/README.md` |
| Developer | `claude/developer/` | `claude/developer/README.md` |
| Release Manager | `claude/release-manager/` | `claude/release-manager/README.md` |
| Security Analyst | `claude/security-analyst/` | `claude/security-analyst/README.md` |

## Available Agents

Use `@agent-name` or Task tool with `subagent_type`:

- `@email-manager` - Internal email system
- `@inav-architecture` - Find firmware code locations
- `@msp-expert` - MSP protocol expertise
- `@inav-builder` - Build firmware/configurator
- `@test-engineer` - Testing and bug reproduction
- `@fc-flasher` - Flash firmware to hardware
- `@sitl-operator` - SITL operations
- `@check-pr-bots` - Check PR CI status
- `@inav-code-review` - Code review before PR
- `@target-developer` - Target-specific fixes
- `@settings-lookup` - CLI settings lookup
- `@aerodynamics-expert` - Aerodynamics expertise

## Available Skills

Use `/skill-name`:

- `/start-task` - Begin task with lock acquisition
- `/git-workflow` - Branch management
- `/create-pr` - Create pull requests
- `/finish-task` - Complete tasks
- `/build-sitl` - Build SITL firmware
- `/build-inav-target` - Build hardware target
- `/email` - Read internal messages
- And many more - see `.opencode/skills/`

## Project Tracking

Active projects: `claude/projects/INDEX.md`
Completed projects: `claude/projects/completed/INDEX.md`

## Lock Files

Before modifying code, check:
- `claude/locks/inav.lock`
- `claude/locks/inav-configurator.lock`