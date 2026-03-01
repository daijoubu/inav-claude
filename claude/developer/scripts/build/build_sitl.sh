#!/bin/bash
# Build INAV SITL (Software In The Loop)
# Usage: ./build_sitl.sh [clean]
#
# This script builds SITL in a separate build_sitl directory to avoid
# conflicts with hardware target builds.

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
BUILD_DIR="${INAV_DIR}/build_sitl"

echo "INAV directory: ${INAV_DIR}"
echo "Build directory: ${BUILD_DIR}"

# Check for clean option
if [ "$1" = "clean" ]; then
    echo "Cleaning SITL build directory..."
    rm -rf "${BUILD_DIR}"
fi

# Create build directory
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

# Check if we need to run cmake
if [ ! -f "Makefile" ] || [ "$1" = "clean" ]; then
    echo "Configuring SITL build..."

    cmake -DSITL=ON ..
fi

echo "Building SITL..."
make SITL.elf -j$(nproc)

if [ -f "bin/SITL.elf" ]; then
    echo ""
    echo "========================================="
    echo "Build successful!"
    echo "Binary: ${BUILD_DIR}/bin/SITL.elf"
    echo "========================================="
    echo ""
    echo "To run: cd ${BUILD_DIR} && ./bin/SITL.elf"
else
    echo "Build failed - SITL.elf not found"
    exit 1
fi
