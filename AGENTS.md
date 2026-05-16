# INAV Project - OpenCode Configuration

This project uses OpenCode for AI-assisted development.

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