#!/bin/bash
# Replay Blackbox Skill - Replay sensor data to FC (SITL/HITL)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
REPLAY_TOOL="$PROJECT_ROOT/claude/test_tools/inav/gps/replay_blackbox_to_fc.py"

# Check if replay tool exists
if [ ! -f "$REPLAY_TOOL" ]; then
    echo "ERROR: Replay tool not found: $REPLAY_TOOL"
    exit 1
fi

# Make sure it's executable
chmod +x "$REPLAY_TOOL"

# Check for mspapi2
if ! python3 -c "import mspapi2" 2>/dev/null; then
    echo "WARNING: mspapi2 not installed"
    echo "Install with: cd $PROJECT_ROOT/mspapi2 && pip install ."
    echo ""
fi

# Run the replay tool with all arguments
cd "$PROJECT_ROOT"
python3 "$REPLAY_TOOL" "$@"
