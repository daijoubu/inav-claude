// INAV-Claude Permission Filter Plugin
// Ported from Claude Code hooks system
// Handles: dangerous commands, git safety, path safety, read/write tools

export default () => ({
  "session.start": async () => {
    // Prompt for role on session start
    return {
      rolePrompt: "Which role should I take on today - Manager, Developer, Release Manager, or Security Analyst?"
    };
  },
  "tool.execute.before": async (input, output) => {
    // =====================================================================
    // TOOL: BASH
    // =====================================================================
    if (input.tool === "bash") {
      const command = (output.args.command || "").trim();
      const cwd = output.args.workdir || "";

      // --- Dangerous Patterns (Deny) ---
      const dangerousPatterns = [
        { pattern: /^rm\s+-rf\s+\//, message: "Blocked: rm -rf on root" },
        { pattern: /^dd\s+if=.*of=\/dev/, message: "Blocked: dd to block device" },
        { pattern: /^mkfs\./, message: "Blocked: mkfs command" },
        { pattern: /^curl.*\|\s*sh/, message: "Blocked: curl | sh (insecure install)" },
        { pattern: /^wget.*\|\s*sh/, message: "Blocked: wget | sh (insecure install)" },
        { pattern: /^:\s*\|/ , message: "Blocked: Fork bomb pattern" },
        { pattern: /^\s*>\s*\/dev\/sda/, message: "Blocked: writing to block device" },
      ];

      for (const { pattern, message } of dangerousPatterns) {
        if (pattern.test(command)) {
          throw new Error(message);
        }
      }

      // --- Git Safety Rules ---
      // Block git add -A
      if (/^git\s+add\s+-A/.test(command)) {
        throw new Error("STOP! Do NOT run 'git add -A'. Add the specific files you actually want.");
      }

      // Block git force push
      if (/^git\s+.*push.*force/.test(command)) {
        throw new Error("STOP! Do NOT force push! That will break public history!");
      }

      // Block git push to master/main in sub-repos
      const subRepoPaths = ['/inav/', '/inav-configurator/', '/PrivacyLRS/', '/mspapi2/', '/inavwiki/'];
      const isSubRepo = subRepoPaths.some(p => cwd.includes(p));
      if (/^git\s+.*push.*(master|main)/.test(command) && isSubRepo) {
        throw new Error("Do NOT push to master/main in sub-repos. Use feature branches.");
      }

      // Block git branch creation in root repo
      const isRootRepo = !subRepoPaths.some(p => cwd.includes(p)) && cwd.includes('inav-claude');
      if (isRootRepo && /git\s+(checkout\s+-b|branch\s+[^-]|switch\s+-c)/.test(command)) {
        throw new Error("Branch creation blocked in root repo. Create branches in sub-repos instead.");
      }

      // --- Path Safety Rules ---
      // Block operations targeting wrong claude paths
      const wrongClaudePaths = ['inav/claude', 'inav-configurator/claude', 'inavwiki/claude', 'PrivacyLRS/claude'];
      if (wrongClaudePaths.some(p => command.includes(p))) {
        throw new Error("STOP! The claude/ directory is at project-root/claude/, NOT inside inav/, inav-configurator/, etc.");
      }

      // --- Allow Safe Commands (Read-only) ---
      const safeReadCommands = [
        'git status', 'git diff', 'git log', 'git show', 'git branch', 'git remote',
        'git describe', 'git rev-parse', 'git rev-list', 'git cat-file', 'git ls-tree',
        'git ls-files', 'git grep', 'git merge-base', 'git blame', 'git tag', 'git fetch',
        'git pull',
        'ls', 'pwd', 'echo', 'cat', 'grep', 'egrep', 'find', 'head', 'tail', 'less', 'more',
        'wc', 'sort', 'uniq', 'diff', 'stat', 'file', 'du', 'df', 'awk', 'sed', 'cut', 'xargs',
        'printf', 'whoami', 'md5sum', 'lsusb', 'sleep', 'ss', 'date', 'ld', 'rg', 'fd',
        'pdfgrep', 'jq', 'readelf', 'objdump', 'nm', 'size', 'objcopy', 'git status --porcelain',
      ];

      const isSafeRead = safeReadCommands.some(safe => 
        command === safe || command.startsWith(safe + " ")
      );

      if (isSafeRead) {
        return; // Allow
      }

      // --- Safe Write Commands (Allow) ---
      const safeWriteCommands = [
        'git add', 'git commit', 'git push origin', 'git push -u',
        'git checkout', 'git stash', 'git cherry-pick', 'git restore',
        'rm -f', 'rm -rf /tmp/', 'touch', 'mkdir', 'chmod', 'chown',
        'cmake', 'make', 'ninja', 'dfu-util', 'npm', 'pip', 'pio',
        'python3', 'node', 'bash',
      ];

      const isSafeWrite = safeWriteCommands.some(safe => 
        command.startsWith(safe + " ") || command === safe
      );

      if (isSafeWrite) {
        return; // Allow
      }

      // For git commit, add reminder about not mentioning Claude
      if (/^git\s+commit/.test(command)) {
        // This would be handled by additional_context in the original hook
        // OpenCode doesn't have equivalent, but the warning is in START.md
        return;
      }

      // Default: let OpenCode's permission system handle it
      return;
    }

    // =====================================================================
    // TOOL: Read/Glob/Grep (Read operations - Allow)
    // =====================================================================
    if (["Read", "Glob", "Grep", "WebSearch", "WebFetch"].includes(input.tool)) {
      return; // Allow read operations
    }

    // =====================================================================
    // TOOL: Write/Edit (Write operations - Ask via OpenCode) 
    // =====================================================================
    if (["Write", "Edit", "NotebookEdit"].includes(input.tool)) {
      // Block writes to wrong claude paths
      const filePath = output.args.filePath || "";
      const wrongPaths = ['inav/claude', 'inav-configurator/claude', 'inavwiki/claude', 'PrivacyLRS/claude'];
      
      if (wrongPaths.some(p => filePath.includes(p))) {
        throw new Error("STOP! The claude/ directory is at project-root/claude/, NOT inside inav/, inav-configurator/, etc.");
      }

      // Allow writes to project directories
      const allowedPaths = [
        '/inav/src/',
        '/inav-configurator/',
        '/tmp/',
        '/claude/developer/workspace/',
        '/claude/manager/email/',
        '/claude/projects/',
      ];

      const isAllowed = allowedPaths.some(p => filePath.includes(p));
      if (isAllowed) {
        return; // Allow
      }

      // Default: let OpenCode permission system handle it (ask user)
      return;
    }

    // =====================================================================
    // TOOL: Task (Allow agent invocations)
    // =====================================================================
    if (["Task", "TaskCreate", "TaskList", "TaskUpdate", "TodoWrite"].includes(input.tool)) {
      return; // Allow task management tools
    }

    // =====================================================================
    // TOOL: Skill (Allow skills)
    // =====================================================================
    if (input.tool === "Skill") {
      return; // Allow skill invocations
    }

    // Default: Allow
    return;
  }
});