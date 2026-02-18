#!/bin/bash
# Build INAV SITL WebAssembly (WASM) target
# Usage: ./build_sitl_wasm.sh [clean]
#
# This script builds SITL for WebAssembly in a separate build_sitl_wasm directory
# to avoid conflicts with native SITL and hardware target builds.
#
# Requirements:
#   - Emscripten SDK (emsdk) installed and activated
#   - Must be run with: source ~/emsdk/emsdk_env.sh && ./build_sitl_wasm.sh

set -e

# Find inav directory - script is in claude/developer/scripts/build/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go up 4 levels from scripts/build to inavflight, then into inav
PROJECT_ROOT="${SCRIPT_DIR}/../../../.."
INAV_DIR="${PROJECT_ROOT}/inav"

if [ ! -d "$INAV_DIR" ]; then
    echo "Error: Cannot find inav directory at $INAV_DIR"
    echo "Script dir: $SCRIPT_DIR"
    exit 1
fi

INAV_DIR="$(cd "$INAV_DIR" && pwd)"
BUILD_DIR="${INAV_DIR}/build_sitl_wasm"

echo "INAV directory: ${INAV_DIR}"
echo "Build directory: ${BUILD_DIR}"

# Check for Emscripten - try to auto-activate if not found
if ! command -v emcc &> /dev/null; then
    echo "emcc not found in PATH, attempting to activate emsdk..."
    
    # Try to find and source emsdk
    if [ -f "$HOME/emsdk/emsdk_env.sh" ]; then
        echo "Found emsdk at $HOME/emsdk, activating..."
        source "$HOME/emsdk/emsdk_env.sh"
    else
        echo "Error: emcc not found and cannot locate emsdk."
        echo "Please install and activate Emscripten SDK:"
        echo ""
        echo "  git clone https://github.com/emscripten-core/emsdk.git"
        echo "  cd emsdk"
        echo "  ./emsdk install latest"
        echo "  ./emsdk activate latest"
        echo "  source ./emsdk_env.sh"
        echo ""
        echo "Then run this script again."
        exit 1
    fi
    
    # Check again after sourcing
    if ! command -v emcc &> /dev/null; then
        echo "Error: Failed to activate emcc"
        exit 1
    fi
fi

echo "Emscripten version: $(emcc --version | head -n1)"

# Check for clean option
if [ "$1" = "clean" ]; then
    echo "Cleaning WASM build directory..."
    rm -rf "${BUILD_DIR}"
fi

# Create build directory
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

# Check if we need to run cmake
if [ ! -f "Makefile" ] || [ "$1" = "clean" ]; then
    echo "Configuring WASM SITL build..."
    echo "CMake flags: -DTOOLCHAIN=wasm -DSITL=ON"
    
    # Configure with WASM toolchain and SITL enabled
    cmake -DTOOLCHAIN=wasm -DSITL=ON ..
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "========================================="
        echo "CMake configuration failed!"
        echo "========================================="
        exit 1
    fi
fi

echo ""
echo "Building SITL WASM target..."
echo "This may take several minutes..."

# Build the SITL target (produces .wasm file and .elf JS wrapper)
make SITL.elf -j4

# Check build result
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================="
    echo "Build failed!"
    echo "Check the error messages above."
    echo "========================================="
    exit 1
fi

# Verify output files exist
# Note: SITL.elf is actually the JavaScript wrapper file
# SITL.wasm is the WebAssembly binary
WASM_FILE="${BUILD_DIR}/bin/SITL.wasm"
JS_FILE="${BUILD_DIR}/bin/SITL.elf"
MAP_FILE="${BUILD_DIR}/bin/SITL.wasm.map"

if [ -f "$WASM_FILE" ] && [ -f "$JS_FILE" ]; then
    echo ""
    echo "========================================="
    echo "Build successful!"
    echo "========================================="
    echo ""
    echo "Output files:"
    echo "  WebAssembly: ${WASM_FILE}"
    echo "  JavaScript:  ${JS_FILE} (named .elf but is actually JS)"
    if [ -f "$MAP_FILE" ]; then
        echo "  Source map:  ${MAP_FILE}"
    fi
    echo ""
    
    # Show file sizes
    WASM_SIZE=$(du -h "$WASM_FILE" | cut -f1)
    JS_SIZE=$(du -h "$JS_FILE" | cut -f1)
    echo "File sizes:"
    echo "  SITL.wasm: ${WASM_SIZE}"
    echo "  SITL.elf:  ${JS_SIZE} (JavaScript wrapper)"
    echo ""
    
    echo "To use in configurator:"
    echo "  1. Rename SITL.elf to SITL.js"
    echo "  2. Copy SITL.js and SITL.wasm to inav-configurator/resources/sitl/"
    echo ""
    echo "Quick copy command:"
    echo "  cp ${WASM_FILE} inav-configurator/resources/sitl/"
    echo "  cp ${JS_FILE} inav-configurator/resources/sitl/SITL.js"
    echo ""
else
    echo ""
    echo "========================================="
    echo "Build failed - output files not found"
    echo "========================================="
    echo ""
    echo "Expected files:"
    echo "  ${WASM_FILE}"
    echo "  ${JS_FILE}"
    echo ""
    exit 1
fi
