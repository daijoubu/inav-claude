#!/usr/bin/env node

/**
 * Copy WASM SITL binaries from firmware build to configurator resources
 *
 * This script copies the SITL.wasm and SITL.elf files from the INAV firmware
 * build directory to the configurator's resources/sitl/ directory so they can
 * be packaged with the Electron app.
 *
 * Usage:
 *   node scripts/copy-wasm-binaries.js
 *
 * Requirements:
 *   - INAV firmware must be built with: cmake -DTOOLCHAIN=wasm -DSITL=ON
 *   - Build output expected at: ../inav/build_wasm/bin/
 */

import { copyFileSync, mkdirSync, existsSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Paths
const INAV_BUILD_DIR = join(__dirname, '../../inav/build_wasm/bin');
const CONFIGURATOR_RESOURCES_DIR = join(__dirname, '../resources/sitl');

const FILES_TO_COPY = [
    'SITL.wasm',
    'SITL.elf'
];

/**
 * Format file size in human-readable format
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Main copy function
 */
function copyWasmBinaries() {
    console.log('🔧 WASM Binary Copy Script');
    console.log('========================\n');

    // Check if source directory exists
    if (!existsSync(INAV_BUILD_DIR)) {
        console.error('❌ ERROR: INAV build directory not found!');
        console.error(`   Expected: ${INAV_BUILD_DIR}`);
        console.error('');
        console.error('   Please build INAV firmware first:');
        console.error('   $ cd ../inav');
        console.error('   $ mkdir -p build_wasm && cd build_wasm');
        console.error('   $ cmake -DTOOLCHAIN=wasm -DSITL=ON ..');
        console.error('   $ cmake --build . --target SITL');
        console.error('');
        process.exit(1);
    }

    // Create destination directory if it doesn't exist
    if (!existsSync(CONFIGURATOR_RESOURCES_DIR)) {
        console.log(`📁 Creating directory: ${CONFIGURATOR_RESOURCES_DIR}`);
        mkdirSync(CONFIGURATOR_RESOURCES_DIR, { recursive: true });
    }

    // Copy files
    let copiedCount = 0;
    let errorCount = 0;

    for (const filename of FILES_TO_COPY) {
        const sourcePath = join(INAV_BUILD_DIR, filename);
        const destPath = join(CONFIGURATOR_RESOURCES_DIR, filename);

        if (!existsSync(sourcePath)) {
            console.error(`⚠️  WARNING: ${filename} not found in build directory`);
            console.error(`   Expected: ${sourcePath}`);
            errorCount++;
            continue;
        }

        try {
            const stats = statSync(sourcePath);
            copyFileSync(sourcePath, destPath);
            copiedCount++;

            console.log(`✅ Copied ${filename}`);
            console.log(`   Size: ${formatBytes(stats.size)}`);
            console.log(`   From: ${sourcePath}`);
            console.log(`   To:   ${destPath}`);
            console.log('');
        } catch (err) {
            console.error(`❌ ERROR copying ${filename}: ${err.message}`);
            errorCount++;
        }
    }

    // Summary
    console.log('========================');
    console.log(`✅ Successfully copied: ${copiedCount}/${FILES_TO_COPY.length} files`);

    if (errorCount > 0) {
        console.log(`⚠️  Errors/Warnings: ${errorCount}`);
        console.log('');
        console.log('Note: Missing files may indicate WASM build is incomplete.');
        console.log('      The configurator will build, but WASM SITL will not work.');
        process.exit(0); // Don't fail the build for missing WASM files
    } else {
        console.log('🎉 WASM binaries ready for packaging!');
    }
}

// Run the script
copyWasmBinaries();
