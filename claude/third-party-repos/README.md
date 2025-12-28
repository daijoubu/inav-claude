# Third-Party Repository Context Files

This directory contains CLAUDE.md files that provide context to Claude Code when working in third-party repositories.

## Why These Files Exist

Claude Code automatically reads `CLAUDE.md` files in the current directory to get context. However, the third-party repos (`inav/`, `inav-configurator/`, `mspapi2/`) are separate git repositories that users clone independently. We can't commit files directly into those repos from this parent repo.

**Solution:** These files live here in the parent repo and are symlinked into the third-party repos.

## Setup Instructions

After cloning the third-party repositories, create symlinks so Claude Code can find these context files:

```bash
# From the repository root directory:

# INAV firmware context
ln -s ../claude/third-party-repos/inav-CLAUDE.md inav/CLAUDE.md

# INAV Configurator context
ln -s ../claude/third-party-repos/inav-configurator-CLAUDE.md inav-configurator/CLAUDE.md

# INAV Configurator transpiler context
ln -s ../../../claude/third-party-repos/inav-configurator-transpiler-CLAUDE.md inav-configurator/js/transpiler/CLAUDE.md
```

## Verifying Symlinks

Check that symlinks were created correctly:

```bash
ls -la inav/CLAUDE.md
ls -la inav-configurator/CLAUDE.md
ls -la inav-configurator/js/transpiler/CLAUDE.md
```

You should see symlinks (indicated by `->`) pointing to files in `claude/third-party-repos/`.

## Files in This Directory

- `inav-CLAUDE.md` - Context for INAV firmware development
- `inav-configurator-CLAUDE.md` - Context for configurator development
- `inav-configurator-transpiler-CLAUDE.md` - Context for transpiler work
