#!/bin/bash
# Clean rebuild of WASM SITL firmware
# Needed when EM_ASM blocks change to regenerate JS glue code

set -e

# Resolve the inav source root. Lookup order:
#   1. $INAV_ROOT env var (canonical override)
#   2. Sibling checkout: <inav-claude-parent>/inav
#   3. Legacy: ~/Documents/planes/inavflight/inav
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -n "${INAV_ROOT:-}" ] && [ -d "$INAV_ROOT" ]; then
    :
elif [ -d "$SCRIPT_DIR/../../../../inav" ]; then
    INAV_ROOT="$(cd "$SCRIPT_DIR/../../../../inav" && pwd)"
elif [ -d "$HOME/Documents/planes/inavflight/inav" ]; then
    INAV_ROOT="$HOME/Documents/planes/inavflight/inav"
else
    echo "ERROR: cannot locate inav source root. Set \$INAV_ROOT or place inav/ as a sibling of inav-claude/." >&2
    exit 1
fi

BUILD_DIR="$INAV_ROOT/build_sitl_wasm"

echo "=== Clean WASM SITL Build ==="

# Remove old build directory
if [ -d "$BUILD_DIR" ]; then
    echo "Removing old build directory..."
    rm -rf "$BUILD_DIR"
fi

# Create fresh build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Source Emscripten environment
echo "Setting up Emscripten..."
source ~/emsdk/emsdk_env.sh

# Configure with CMake - explicitly set TOOLCHAIN to wasm
echo "Configuring with CMake..."
emcmake cmake -DSITL=ON -DTOOLCHAIN=wasm -GNinja ..

# Build
echo "Building WASM SITL..."
ninja SITL.elf

echo "=== Build Complete ==="
echo "Output files:"
ls -la "$BUILD_DIR/bin/"
