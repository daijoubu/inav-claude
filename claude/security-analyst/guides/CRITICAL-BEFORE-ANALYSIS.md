# CRITICAL: Read Before Starting Any Security Analysis

**STOP!** Before beginning any security analysis task, complete this checklist.

---

## Pre-Analysis Checklist

### 1. Check Your Inbox

Use the **email-manager** agent to check for new assignments:

```
Task tool with subagent_type="email-manager"
Prompt: "Read my inbox. Current role: security-analyst"
```

**Look for:**
- New security analysis requests
- Clarification from manager
- Updates from developer about fixes

### 2. Read and Understand the Assignment

**Key questions to answer:**
- What is the scope of this analysis? (specific files, components, or full codebase?)
- What type of analysis is requested?
  - Code security review
  - Cryptographic protocol analysis
  - Threat modeling
  - Vulnerability assessment
  - Performance/security tradeoff analysis
- Are there specific concerns or attack vectors to investigate?
- What is the expected deliverable? (findings report, threat model, crypto review?)
- What is the priority/urgency?

**If unclear, ask the manager for clarification immediately.**

### 3. Review Previous Analysis (If Applicable)

Check if this is a follow-up or related to previous work:

```bash
# Search for related findings
grep -r "ComponentName" claude/security-analyst/docs/vulnerabilities/
grep -r "related-issue" claude/security-analyst/email/inbox-archive/
```

**Look for:**
- Previous findings in this component
- Known vulnerability patterns
- Existing threat models
- Related security issues

### 4. Check for Existing Knowledge Assets

Before starting, check if you have reusable assets:

```bash
# Check for relevant scripts
ls claude/security-analyst/scripts/scanning/
ls claude/security-analyst/scripts/analysis/

# Check for documented patterns
ls claude/security-analyst/docs/vulnerabilities/
ls claude/security-analyst/docs/checklists/
```

**Use existing tools to accelerate your analysis!**

### 5. Set Up Your Workspace

Create a workspace directory for this analysis:

```bash
# Use descriptive naming
mkdir -p claude/security-analyst/workspace/YYYY-MM-DD-component-name/

# Organize your work
cd claude/security-analyst/workspace/YYYY-MM-DD-component-name/
touch notes.md
touch findings.md
mkdir test-data/
```

**Workspace structure suggestion:**
```
workspace/2026-01-18-chacha20-analysis/
├── notes.md              # Investigation notes
├── findings.md           # Draft findings (before formal report)
├── test-scripts/         # Test harnesses
├── test-data/            # Sample inputs/outputs
└── references/           # Copied relevant code snippets
```

### 6. Review Relevant Documentation

Read the cryptography textbook if analyzing crypto:
- `/home/raymorris/Documents/planes/inavflight/claude/developer/docs/encryption/applied_cryptography-BonehShoup_0_4.pdf`

**Also review:**
- Project documentation for the component
- Relevant RFCs or specifications
- Security guidelines for the technology

---

## Ready to Begin

Once you've completed this checklist:

1. ✅ Assignment understood
2. ✅ Previous work reviewed
3. ✅ Workspace set up
4. ✅ Relevant knowledge assets identified
5. ✅ Git branch checked (if doing code changes)

**Now proceed to the analysis phase.**

Refer to:
- `guides/security-analysis-methods.md` - For code review procedures
- `guides/threat-modeling-guide.md` - For threat modeling
- `guides/crypto-review-guide.md` - For cryptographic analysis
