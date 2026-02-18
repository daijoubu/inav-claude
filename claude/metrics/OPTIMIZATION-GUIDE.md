# Token Optimization Guide: General-Purpose Agent

**Date:** 2026-02-16
**Issue:** general-purpose agent consuming 923,334 tokens (41% of total) with inefficient patterns
**Goal:** Reduce token usage by 30-40% while maintaining output quality

---

## 🎯 Executive Summary

The general-purpose agent is being used for tasks better suited to:
1. **Direct tool calls** (Bash, Read, Edit, Glob, Grep)
2. **Specialized agents** (email-manager, inav-architecture, inav-builder, test-engineer)
3. **System tools** (TaskCreate, TaskUpdate for tracking)

**Potential Savings:** 280,000-370,000 tokens (30-40% reduction)
**Implementation:** No output quality loss - just better tool selection

---

## 📊 Inefficiency Breakdown

### Category 1: Git/Cleanup Operations (112K tokens)

**Problem:** Using general-purpose agent for git operations
- Final cleanup and commit: 37,334 tokens (32 tools)
- Final system cleanup: 35,780 tokens (36 tools)

**Current Approach:**
```python
Task tool: subagent_type="general-purpose"
Prompt: "Final cleanup and commit"
```

**Optimized Approach:**
```bash
# Use Bash directly (much cheaper!)
git add -A
git commit -m "..."
git push
```

**Savings:** ~95% token reduction (37K → 500 tokens)

**Why It Works:**
- Git commands are deterministic
- No reasoning needed about what to do
- Direct Bash execution is 50-100x cheaper than agent reasoning

---

### Category 2: Verification/Status Checks (345K tokens)

**Problem:** Using general-purpose to check files, directories, status
- Check developer readiness: 33,193 tokens (15 tools)
- Check assignment history: 33,020 tokens (19 tools)
- Check developer workspace: 31,284 tokens (13 tools)

**Current Approach:**
```python
Task tool: subagent_type="general-purpose"
Prompt: "Check if developer is ready to work"
```

**Optimized Approach:**
```bash
# Use Bash and Read directly
git status --porcelain
ls -la workspace/
cat locks/*.lock 2>/dev/null
```

**Or use specialized tools:**
```python
Glob(pattern="workspace/*/")
Read(file_path="locks/inav.lock")
```

**Savings:** ~90% token reduction (33K → 3K tokens)

**Why It Works:**
- Verification is deterministic - just check facts
- No reasoning loop needed
- Direct tool calls return same data with 90% fewer tokens

---

### Category 3: Search/Investigation (105K tokens)

**Problem:** Using general-purpose for searches that Glob/Grep can do
- Search for specific INAV issues: 31,307 tokens (14 tools)
- Check INAV milestone progress: 18,110 tokens (20 tools)

**Current Approach:**
```python
Task tool: subagent_type="general-purpose"
Prompt: "Search for all issues with label 'DroneCAN'"
```

**Optimized Approach:**
```python
# Use specialized agents for code/architecture:
Task tool: subagent_type="inav-architecture"
Prompt: "Find DroneCAN-related code"

# Use direct tools for simple searches:
Grep(pattern="DroneCAN", type="py")
Glob(pattern="**/dronecan*")
```

**Savings:** ~75% token reduction (31K → 8K tokens)

**Why It Works:**
- inav-architecture is built for code search (45K tokens for complex work)
- Glob/Grep are efficient for simple pattern matching
- Don't pay full general-purpose overhead for simple queries

---

### Category 4: Project Updates (101K tokens)

**Problem:** Using general-purpose to read and update project files
- Update HITL project completion: 31,363 tokens (31 tools)
- Update project index: 21,115 tokens (17 tools)

**Current Approach:**
```python
Task tool: subagent_type="general-purpose"
Prompt: "Update project completion status"
```

**Optimized Approach:**
```python
# Direct file operations:
Read(file_path="claude/projects/active/hitl.../summary.md")
Edit(file_path="claude/projects/active/hitl.../summary.md",
     old_string="Status: TODO",
     new_string="Status: COMPLETED")

# Or use TaskUpdate:
TaskUpdate(taskId="123", status="completed")
```

**Savings:** ~85% token reduction (31K → 4.5K tokens)

**Why It Works:**
- Read/Edit/Write are highly optimized for file operations
- No reasoning overhead for simple text replacements
- TaskCreate/TaskUpdate built specifically for tracking

---

### Category 5: Workspace Setup (30K tokens)

**Problem:** Using general-purpose for workspace initialization
- Set up HITL workspace: 30,237 tokens (9 tools)

**Current Approach:**
```python
Task tool: subagent_type="general-purpose"
Prompt: "Set up HITL workspace with test scripts"
```

**Optimized Approach:**
```bash
# Use Bash directly
mkdir -p workspace/hitl/tests
cp scripts/*.py workspace/hitl/
chmod +x workspace/hitl/*.py

# Then use test-engineer for complex test setup
Task tool: subagent_type="test-engineer"
Prompt: "Configure HITL test environment"
```

**Savings:** ~80% token reduction (30K → 6K tokens)

**Why It Works:**
- File/directory setup is deterministic
- Use specialized agents only for actual complexity
- Bash is 5-10x cheaper than general-purpose for setup

---

## 🔄 Decision Tree: When to Use Each Tool

```
Task at hand?
├─ Git operation? (add, commit, push, rebase)
│  └─ Use: Bash directly
│     Savings: 95%+ vs general-purpose
│
├─ Simple file check? (exists, size, contents)
│  └─ Use: Read, Glob, or Bash ls
│     Savings: 90%+ vs general-purpose
│
├─ Text search/pattern matching?
│  ├─ Complex code search?
│  │  └─ Use: inav-architecture agent
│  │     Savings: 70% vs general-purpose
│  └─ Simple pattern?
│     └─ Use: Grep or Bash grep
│        Savings: 90%+ vs general-purpose
│
├─ File edit/update?
│  ├─ Project tracking?
│  │  └─ Use: TaskCreate/TaskUpdate
│  │     Savings: 85%+ vs general-purpose
│  └─ Code/doc file?
│     └─ Use: Read + Edit
│        Savings: 85%+ vs general-purpose
│
├─ Email/message handling?
│  └─ Use: email-manager agent
│     Savings: 50%+ vs general-purpose
│
├─ Build/test execution?
│  ├─ Firmware build?
│  │  └─ Use: inav-builder agent
│  ├─ Testing?
│  │  └─ Use: test-engineer agent
│  └─ Simulator?
│     └─ Use: sitl-operator agent
│
└─ Complex reasoning needed?
   └─ Use: general-purpose (only when truly needed)
      Keep at minimum: 10-15% of operations
```

---

## 📋 Specific Optimization Examples

### Example 1: Status Check
**Before: 33,193 tokens**
```python
Task(subagent_type="general-purpose",
     prompt="Check if developer workspace is ready")
```

**After: ~1,000 tokens**
```python
Bash(command="git status --porcelain")
Bash(command="ls -la claude/developer/workspace/ | head -20")
Bash(command="cat claude/locks/*.lock 2>/dev/null")
```

**Output:** Same information, 97% cheaper

---

### Example 2: Project Update
**Before: 31,363 tokens**
```python
Task(subagent_type="general-purpose",
     prompt="Update project completion status and mark as done")
```

**After: ~2,500 tokens**
```python
Read(file_path="claude/projects/active/hitl-tests/summary.md")
Edit(file_path="claude/projects/active/hitl-tests/summary.md",
     old_string="**Status:** 🚧 IN PROGRESS",
     new_string="**Status:** ✅ COMPLETED")
TaskUpdate(taskId="123", status="completed")
```

**Output:** Same result, 92% cheaper

---

### Example 3: Git Cleanup
**Before: 37,334 tokens**
```python
Task(subagent_type="general-purpose",
     prompt="Final cleanup, add all changes, commit with message, and push")
```

**After: ~1,000 tokens**
```bash
git add -A
git commit -m "$(cat <<'EOF'
Complete HITL testing

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"
git push origin main
```

**Output:** Exact same commit, 97% cheaper

---

### Example 4: Search for Code
**Before: 31,307 tokens (with general-purpose)**
```python
Task(subagent_type="general-purpose",
     prompt="Search for all DroneCAN references in firmware")
```

**After: ~8,000 tokens (with specialized agent)**
```python
Task(subagent_type="inav-architecture",
     prompt="Find DroneCAN code locations")

# Or for simple patterns:
Grep(pattern="DroneCAN", path="inav/src/", type="c")
```

**Output:** Better results (inav-architecture understands structure), 75% cheaper

---

## 🛠️ Implementation Strategy

### Phase 1: Low-hanging Fruit (1-2 hours)
Replace these patterns in future work:

1. **Git operations** (37K tokens → 1K tokens)
   - Use Bash directly for add, commit, push

2. **Simple checks** (30K tokens → 3K tokens)
   - Use Read, Bash, Glob for verification

3. **File updates** (21K tokens → 2.5K tokens)
   - Use Edit tool directly

**Expected Savings:** 100K+ tokens per set of similar tasks

---

### Phase 2: Medium Refactoring (2-3 hours)
Implement systematic improvements:

1. **Create tool use patterns** for common tasks
   - Git workflow procedures
   - File check procedures
   - Project update procedures

2. **Task tracking system** (TaskCreate/TaskUpdate)
   - Replace general-purpose status tracking
   - Use for complex projects

3. **Agent selection guidelines**
   - Document when to use each agent
   - Reduce general-purpose usage to <15%

**Expected Savings:** 50K+ tokens per week

---

### Phase 3: Ongoing Optimization
Maintain efficiency going forward:

1. **Code review focus:** Check for general-purpose overuse
2. **Alternative-first approach:** Always consider direct tools first
3. **Monitor token usage:** Track general-purpose percentage

**Expected Savings:** 30-40% ongoing reduction

---

## 📈 Expected Impact

### Current State
- general-purpose: 923K tokens (41% of total)
- Total: 2.23M tokens

### Optimized State (30% reduction)
- general-purpose: 650K tokens (29% of total)
- Total: 1.85M tokens
- **Savings: 280K tokens per project cycle**

### Optimized State (40% reduction)
- general-purpose: 550K tokens (24% of total)
- Total: 1.68M tokens
- **Savings: 370K tokens per project cycle**

### Cost Equivalent
At typical pricing:
- 280K tokens = $2.80 per project cycle
- 370K tokens = $3.70 per project cycle
- **Annual savings: $100-150+ (assuming 30-40 cycles/year)**

---

## ⚠️ Important Notes

### Don't Replace When:
1. **Complex reasoning needed** → Keep general-purpose
2. **Multi-step investigation** → Keep inav-architecture
3. **Uncertain outcome** → Use specialized agent first
4. **Novel problem** → general-purpose is appropriate

### Do Replace When:
1. ✅ Deterministic operation (git, file I/O)
2. ✅ Simple verification (check if file exists)
3. ✅ Pattern matching (grep, glob)
4. ✅ Known procedure (update project status)
5. ✅ Repetitive task (same check multiple times)

---

## 🎓 Learning Outcomes

This analysis reveals:

1. **Specialized tools are crucial** for efficiency
   - Bash: 5-100x cheaper for specific tasks
   - Grep/Glob: 90%+ savings vs agent reasoning

2. **Agents are for complexity, not simplicity**
   - Use agents for: code analysis, testing, building
   - Use tools for: file I/O, execution, patterns

3. **Context overhead is real**
   - Every agent call loads full conversation context
   - Direct tools avoid this overhead

4. **Token efficiency vs flexibility trade-off**
   - general-purpose is very flexible but expensive
   - Specialized tools are cheaper but narrower

---

## 📝 Recommendations

### For Current Project
Already optimized well - good mix of tool selection on recent work

### For Future Projects
1. Adopt "tool-first" mentality
2. Use agents only for complex reasoning
3. Maintain <20% general-purpose usage
4. Document patterns in CLAUDE.md

### For Tool Development
Consider creating focused agent/skill for:
- Project tracking (replaces general-purpose update tasks)
- Workspace setup (replaces general-purpose setup)
- Status verification (replaces general-purpose checks)

---

## Summary

**General-Purpose Agent:** Best for novel, complex tasks requiring reasoning
**Direct Tools:** Best for deterministic, repetitive, simple operations

**Current Inefficiency:** Using reasoning engine for deterministic tasks
**Optimization:** Match tool complexity to task complexity

**Result:** 30-40% token savings, same output quality ✨

---

*This analysis suggests a simple principle: Use the least powerful tool that solves the problem. Save the heavy reasoning for when it's actually needed.*
