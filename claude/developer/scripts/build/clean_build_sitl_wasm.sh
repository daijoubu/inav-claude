#!/bin/bash
# Clean rebuild of WASM SITL firmware
# Needed when EM_ASM blocks change to regenerate JS glue code

set -e

INAV_ROOT="/home/raymorris/Documents/planes/inavflight/inav"
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
