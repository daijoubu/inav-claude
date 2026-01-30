# DFU Flasher Documentation Update Summary

## Overview

All DFU flashing documentation has been updated to prefer the Node.js flasher (`flash-dfu-node.js`), especially for H7 targets, and to include sandbox permission warnings.

## Key Changes

### 1. Node.js Flasher Enhanced (`flash-dfu-node.js`)

**Added sandbox detection and helpful error messages:**

- **No DFU device found**: Shows possible causes including sandbox restrictions
- **Permission errors**: Explains USB access issues and provides fixes
- **Serial device check**: After flash, checks if FC reconnected and warns about sandbox blocking `/dev/ttyACM*`

**Error messages now include:**
- Sandbox detection warnings
- Permission fix instructions
- udev rules reminder
- Alternative troubleshooting steps

### 2. Agent Documentation Updated

#### fc-flasher Agent (`/.claude/agents/fc-flasher.md`)

**Changes:**
- **Primary script**: Changed from Python to Node.js (`flash-dfu-node.js`)
- **Python marked as fallback**: Explicitly noted "Don't use for H7"
- **Transfer size detection**: Explained why Node.js version is more reliable
- **Added lessons learned**: H7 transfer size requirements, preference for Node.js flasher

**Key sections updated:**
- "CRITICAL: Use the Correct Flashing Script" - Node.js now preferred
- "Available Scripts and Tools" - Node.js listed first with advantages
- "Flashing Workflow" - Updated example to use Node.js version
- "Complete Example Workflow" - Shows Node.js as primary, Python commented as alternative
- "Important Notes" - Added transfer size auto-detection note
- "Related Documentation" - Node.js flasher listed first
- "Lessons" - Added H7 transfer size lesson

#### inav-builder Agent (`/.claude/agents/inav-builder.md`)

**Changes:**
- Updated build-and-flash section to mention fc-flasher agent uses Node.js flasher
- Added note about transfer size auto-detection for H7

### 3. Skill Documentation Updated

#### flash-firmware-dfu Skill (`/.claude/skills/flash-firmware-dfu/SKILL.md`)

**Changes:**
- **IMPORTANT section**: Added sandbox permissions reminder
- **Automated Scripts section**: Complete rewrite
  - Node.js flasher documented first as "Recommended"
  - Python flasher marked as "Alternative (Don't Use for H7)"
  - Legacy shell script marked as "DO NOT USE"
- **Added critical sandbox warning**: All USB/serial operations require `dangerouslyDisableSandbox: true`

**New sections:**
- "CRITICAL: Sandbox Permissions" - Explains when to disable sandbox
- Lists all operations that need sandbox disabled
- Examples of correct vs incorrect Bash tool usage

### 4. New Documentation Created

#### README-node-flasher.md

**Location**: `claude/developer/scripts/build/README-node-flasher.md`

**Contents:**
- Why Node.js version exists
- Installation instructions
- Usage examples
- Expected output
- Settings preservation explanation
- Troubleshooting section
- Advantages over Python version
- Technical details
- Comparison table with configurator

#### FLASH-DFU-NODE-SUMMARY.md

**Location**: `claude/developer/scripts/build/FLASH-DFU-NODE-SUMMARY.md`

**Contents:**
- Problem solved (H7 69.5% failure)
- Root cause analysis (transfer size detection)
- Solution explanation
- Key features list
- DFU functional descriptor format
- Why transfer size matters
- Implementation approach
- Usage instructions
- When to use which flasher
- Testing verification
- Lessons learned
- Future improvements

## Technical Improvements

### Transfer Size Auto-Detection

**How it works:**
1. Reads DFU functional descriptor from USB interface (alternate setting 1)
2. Extracts bytes 5-6 (little-endian) = transfer size
3. Uses detected size for all data transfers
4. Falls back to 2048 bytes if descriptor can't be read

**Why it matters:**
- H7 targets: Require 1024-byte transfers (not 2048)
- Python version: Hardcoded 2048, failed at ~69.5% on H7
- Node.js version: Auto-detects, works on all targets

### Sandbox Detection

**Added checks for:**
1. **No DFU device** - Could be sandbox blocking USB
2. **Permission errors** - Could be sandbox or udev rules
3. **No serial after flash** - Could be sandbox blocking /dev/ttyACM*

**Error messages include:**
- Clear explanation of what went wrong
- Multiple possible causes listed
- Specific sandbox warnings
- Step-by-step fixes
- Alternative troubleshooting commands

## File Locations

### Updated Files
```
/.claude/agents/fc-flasher.md
/.claude/agents/inav-builder.md
/.claude/skills/flash-firmware-dfu/SKILL.md
claude/developer/scripts/build/flash-dfu-node.js
claude/developer/scripts/build/README-node-flasher.md
```

### New Files
```
claude/developer/scripts/build/FLASH-DFU-NODE-SUMMARY.md
claude/developer/scripts/build/DOCUMENTATION-UPDATE-SUMMARY.md (this file)
```

### Unchanged but Referenced
```
claude/developer/scripts/build/flash-dfu-preserve-settings.py (marked as fallback)
claude/developer/scripts/build/package.json
claude/developer/scripts/build/node_modules/ (dependencies)
```

## When to Use Which Flasher

### Always Use Node.js (`flash-dfu-node.js`)
- ✅ **H7 targets** (CRITICAL - Python fails)
- ✅ **All targets** (preferred - most reliable)
- ✅ **New development** (proven implementation)
- ✅ **When available** (requires Node.js and npm)

### Python Acceptable (`flash-dfu-preserve-settings.py`)
- ✅ F4/F7/AT32 targets if Node.js unavailable
- ❌ **NEVER for H7**

### Never Use
- ❌ `build-and-flash.sh` with dfu-util (doesn't preserve settings)
- ❌ Direct `dfu-util` commands (doesn't preserve settings)

## Testing Performed

✅ H7 target flash successful (DAKEFPVH743PRO)
✅ Transfer size auto-detection (1024 bytes detected)
✅ Settings preservation (only 7 firmware pages erased)
✅ Verification after write
✅ Clean progress output (1% increments)
✅ Proper DFU exit and reboot
✅ Sandbox warning messages display correctly
✅ Serial device reconnection check works
✅ Error messages are helpful and actionable

## User Benefits

1. **Reliability**: H7 flashing now works (was failing at 69.5%)
2. **Consistency**: Same behavior across all MCU types
3. **Better errors**: Clear sandbox warnings and troubleshooting steps
4. **Settings preserved**: Both flashers use selective page erase
5. **Verification**: Node.js version verifies firmware after writing
6. **Clean output**: Progress updates every 1% instead of every chunk
7. **Proven code**: Direct port of working configurator implementation

## Developer Benefits

1. **Clear documentation**: Know which flasher to use when
2. **Sandbox awareness**: Understand permission requirements
3. **Troubleshooting**: Helpful error messages guide debugging
4. **Maintenance**: Single preferred implementation to maintain
5. **Understanding**: Summary documents explain the "why" not just "how"

## Conclusion

All documentation now consistently recommends the Node.js flasher as the primary method, with clear explanations of why it's preferred (especially for H7), when to use alternatives, and how to handle sandbox restrictions. The flasher itself now provides helpful error messages that guide users through common issues including sandbox detection.
