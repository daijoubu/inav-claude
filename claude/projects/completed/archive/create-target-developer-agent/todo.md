# Todo: Create Target Developer Agent with Documentation

## Phase 1: Research Target System

- [ ] Explore target directory structure
- [ ] Study 3-4 representative targets (F4, F7, minimal)
- [ ] Read target.h, target.cmake, config.c from examples
- [ ] Document target file purposes and relationships
- [ ] Mine git history for target-related commits (100+ commits)
- [ ] Search for "fix" + "target" commits
- [ ] Search for "flash" + "size" commits
- [ ] Examine 10-15 interesting fix commits in detail
- [ ] Categorize problems found: flash, pins, features, timers, etc.
- [ ] Document fix patterns for each problem type

## Phase 2: Write Documentation

### Create Documentation Directory
- [ ] Create `claude/developer/docs/targets/` directory
- [ ] Create `claude/developer/docs/targets/knowledge-base/` directory

### Core Documentation Files
- [ ] Write `overview.md` - Target system architecture
- [ ] Write `common-issues.md` - Problem catalog with git examples
- [ ] Write `creating-targets.md` - Step-by-step new target guide
- [ ] Write `troubleshooting-guide.md` - Debugging techniques
- [ ] Write `examples.md` - 5-10 real fixes from git history

### Knowledge Base Files
- [ ] Create `knowledge-base/mcu-families/` subdirectory
- [ ] Write `stm32f4.md`, `stm32f7.md`, `stm32h7.md`
- [ ] Create `knowledge-base/peripherals/` subdirectory
- [ ] Write peripheral config docs (timers, uart, spi, i2c)
- [ ] Create `knowledge-base/common-sensors/` subdirectory
- [ ] Write sensor config docs (gyro, baro, mag)
- [ ] Create `knowledge-base/git-fixes/` subdirectory
- [ ] Write `historical-fixes.md` with extracted commit analysis

## Phase 3: Create Target Developer Agent

- [ ] Plan agent capabilities and knowledge base access
- [ ] Use create-agent agent to generate target-developer agent
- [ ] Specify tools: Read, Grep, Glob, Bash (git commands)
- [ ] Configure agent to access docs/targets/ knowledge base
- [ ] Add instructions for comparing targets
- [ ] Add instructions for diagnosing flash issues
- [ ] Add instructions for fixing pin conflicts
- [ ] Add instructions for feature optimization
- [ ] Review generated agent file
- [ ] Test agent with sample problem

## Phase 4: Test and Validate

- [ ] Test agent: ask it to analyze a target configuration
- [ ] Test agent: ask it to troubleshoot a flash overflow
- [ ] Test agent: ask it to compare two targets
- [ ] Test agent: ask it to create new target boilerplate
- [ ] Verify agent can access all documentation
- [ ] Verify agent uses git history effectively
- [ ] Make adjustments to agent based on testing

## Phase 5: Completion

- [ ] Verify all documentation files created
- [ ] Verify knowledge base is complete
- [ ] Verify agent file exists in `.claude/agents/`
- [ ] Create summary of capabilities
- [ ] Send completion report to manager
