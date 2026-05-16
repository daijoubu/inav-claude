# OpenCode Agents

This file documents the custom agents available for INAV project tasks.

## Invoking Agents

Use the Task tool with the appropriate subagent_type:

```
Task tool with subagent_type="agent-name"
Prompt: "Your task description here"
```

## Available Agents

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **email-manager** | Internal email system | Email, inbox, messages |
| **inav-architecture** | Find firmware code locations | Code navigation, architecture |
| **msp-expert** | MSP protocol expertise | MSP commands, packets |
| **inav-builder** | Build firmware/configurator | Build tasks, compilation |
| **test-engineer** | Testing and bug reproduction | Testing, reproducing issues |
| **fc-flasher** | Flash firmware to hardware | Flashing FC, DFU |
| **sitl-operator** | SITL operations | SITL simulation |
| **check-pr-bots** | Check PR CI status | PR checks, bot comments |
| **inav-code-review** | Code review | Review code before PR |
| **target-developer** | Target-specific fixes | Flash overflow, DMA, gyro |
| **settings-lookup** | CLI settings lookup | Setting values, parameters |
| **aerodynamics-expert** | Aerodynamics expertise | Lift, drag, stall, airspeed |
| **permissions-manager** | Permission rules | Allow/deny commands |
| **create-agent** | Create new agents | Making new agents |
| **create-pr** | Create pull requests | PR creation (also a skill) |

## Agent Configuration

Agents are defined in `.opencode/agents/*.md` with:
- YAML frontmatter with `name`, `description`, `mode: subagent`
- Permission settings for each agent
- Full documentation in the agent file

## Skills vs Agents

- **Skills** (`.opencode/skills/`) - Lightweight, triggered by keywords
- **Agents** - More capable, invoked via Task tool with subagent_type

Use skills for simple repetitive tasks. Use agents for complex multi-step operations.