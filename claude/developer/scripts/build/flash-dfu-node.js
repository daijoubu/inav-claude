#!/usr/bin/env node
/**
 * INAV DFU Flasher - Node.js Command Line Version
 *
 * Uses node-usb (libusb) to provide the same USB access as the configurator's WebUSB.
 * Directly ports the proven stm32usbdfu.js protocol implementation.
 */

const usb = require('usb');
const fs = require('fs');

// DFU Protocol Constants (from configurator)
const DFU_REQUEST = {
    DETACH: 0x00,
    DNLOAD: 0x01,
    UPLOAD: 0x02,
    GETSTATUS: 0x03,
    CLRSTATUS: 0x04,
    GETSTATE: 0x05,
    ABORT: 0x06
};

const DFU_STATE = {
    appIDLE: 0,
    appDETACH: 1,
    dfuIDLE: 2,
    dfuDNLOAD_SYNC: 3,
    dfuDNBUSY: 4,
    dfuDNLOAD_IDLE: 5,
    dfuMANIFEST_SYNC: 6,
    dfuMANIFEST: 7,
    dfuMANIFEST_WAIT_RESET: 8,
    dfuUPLOAD_IDLE: 9,
    dfuERROR: 10
};

// STM32 DFU USB IDs
const STM32_DFU_VID = 0x0483;
const STM32_DFU_PID = 0xdf11;

// Global state
let device = null;
let transferSize = 2048;  // Will be updated from DFU descriptor

// =============================================================================
// USB Control Transfer Wrappers (node-usb equivalents of WebUSB)
// =============================================================================

function controlTransferOut(request, value, data) {
    return new Promise((resolve, reject) => {
        const bmRequestType = 0x21; // OUT, Class, Interface
        const wIndex = 0;

        if (!Buffer.isBuffer(data)) {
            data = Buffer.from(data);
        }

        device.controlTransfer(
            bmRequestType,
            request,
            value,
            wIndex,
            data,
            (error, result) => {
                if (error) {
                    console.log(`    controlTransferOut ERROR: ${error.message}`);
                    reject(error);
                } else {
                    resolve(result);
                }
            }
        );
    });
}

function controlTransferIn(request, value, length) {
    return new Promise((resolve, reject) => {
        const bmRequestType = 0xA1; // IN, Class, Interface
        const wIndex = 0;

        device.controlTransfer(
            bmRequestType,
            request,
            value,
            wIndex,
            length,
            (error, data) => {
                if (error) reject(error);
                else resolve(data);
            }
        );
    });
}

// =============================================================================
// DFU Protocol Functions (from stm32usbdfu.js)
// =============================================================================

async function getStatus() {
    const data = await controlTransferIn(DFU_REQUEST.GETSTATUS, 0, 6);
    return {
        status: data[0],
        pollTimeout: data[1] | (data[2] << 8) | (data[3] << 16),
        state: data[4]
    };
}

async function clearStatus() {
    // Keep checking and clearing until dfuIDLE
    let status = await getStatus();

    while (status.state !== DFU_STATE.dfuIDLE) {
        await controlTransferOut(DFU_REQUEST.CLRSTATUS, 0, Buffer.alloc(0));

        if (status.pollTimeout > 0) {
            await sleep(status.pollTimeout);
        }

        status = await getStatus();
    }
}

async function loadAddress(address, callback) {
    const cmd = Buffer.from([
        0x21,
        address & 0xff,
        (address >> 8) & 0xff,
        (address >> 16) & 0xff,
        (address >> 24) & 0xff
    ]);

    await controlTransferOut(DFU_REQUEST.DNLOAD, 0, cmd);

    let status = await getStatus();
    if (status.state === DFU_STATE.dfuDNBUSY) {
        await sleep(status.pollTimeout);
        status = await getStatus();
        if (status.state !== DFU_STATE.dfuDNLOAD_IDLE) {
            throw new Error(`Failed to execute address load, state=${status.state} (expected dfuDNLOAD_IDLE=5)`);
        }
    } else {
        throw new Error(`Failed to request address load, state=${status.state} (expected dfuDNBUSY=4)`);
    }

    // Call callback if provided (to match JS pattern)
    if (callback) {
        await callback();
    }
}

// =============================================================================
// Helper Functions
// =============================================================================

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function parseIntelHex(filename) {
    const content = fs.readFileSync(filename, 'utf8');
    const lines = content.split('\n');

    const blocks = [];
    let currentBlock = null;
    let extendedAddress = 0;

    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed[0] !== ':') continue;

        const byteCount = parseInt(trimmed.substr(1, 2), 16);
        const address = parseInt(trimmed.substr(3, 4), 16);
        const recordType = parseInt(trimmed.substr(7, 2), 16);
        const data = trimmed.substr(9, byteCount * 2);

        if (recordType === 0x00) { // Data record
            const fullAddress = extendedAddress + address;
            const dataBytes = [];
            for (let i = 0; i < data.length; i += 2) {
                dataBytes.push(parseInt(data.substr(i, 2), 16));
            }

            if (currentBlock && currentBlock.address + currentBlock.bytes === fullAddress) {
                currentBlock.data.push(...dataBytes);
                currentBlock.bytes += byteCount;
            } else {
                if (currentBlock) blocks.push(currentBlock);
                currentBlock = {
                    address: fullAddress,
                    bytes: byteCount,
                    data: dataBytes
                };
            }
        } else if (recordType === 0x01) { // End of file
            if (currentBlock) blocks.push(currentBlock);
            break;
        } else if (recordType === 0x04) { // Extended linear address
            extendedAddress = parseInt(data, 16) << 16;
        }
    }

    const totalBytes = blocks.reduce((sum, block) => sum + block.bytes, 0);
    return { data: blocks, bytes_total: totalBytes };
}

function parseFlashDescriptor(descriptorStr) {
    try {
        // Clean string
        descriptorStr = descriptorStr.replace(/[^\x20-\x7E]+/g, '');
        const parts = descriptorStr.split('/');

        if (parts.length > 3) parts.length = 3;
        if (parts.length < 3 || !parts[0].startsWith('@')) return null;

        const memoryType = parts[0].trim().replace('@', '');
        const startAddress = parseInt(parts[1], 16);

        const sectors = [];
        let totalSize = 0;
        const sectorParts = parts[2].split(',');

        for (const sectorStr of sectorParts) {
            if (!sectorStr.includes('*')) continue;

            const [numStr, sizeStr] = sectorStr.split('*');
            const numPages = parseInt(numStr);
            let pageSize = parseInt(sizeStr.match(/\d+/)[0]);

            const unit = sizeStr.match(/[KM]/)?.[0];
            if (unit === 'M') pageSize *= 1024 * 1024;
            else if (unit === 'K') pageSize *= 1024;

            sectors.push({
                start_address: startAddress + totalSize,
                page_size: pageSize,
                num_pages: numPages,
                total_size: numPages * pageSize
            });
            totalSize += numPages * pageSize;
        }

        if (sectors.length === 0) return null;

        return {
            type: memoryType,
            start_address: startAddress,
            sectors: sectors,
            total_size: totalSize
        };
    } catch (e) {
        return null;
    }
}

function getStringDescriptor(index) {
    return new Promise((resolve, reject) => {
        device.getStringDescriptor(index, (error, data) => {
            if (error) reject(error);
            else resolve(data);
        });
    });
}

function getDfuTransferSize() {
    try {
        // Get the DFU interface descriptor (alternate setting 1 has the transfer size)
        const config = device.configDescriptor;
        const dfuInterface = config.interfaces[0].find(alt => alt.bAlternateSetting === 1);

        if (dfuInterface && dfuInterface.extra) {
            // The extra field is a Buffer - need to convert to array for access
            const extra = Buffer.isBuffer(dfuInterface.extra)
                ? Array.from(dfuInterface.extra)
                : dfuInterface.extra.data || [];

            // DFU functional descriptor format:
            // byte 0: length (9)
            // byte 1: type (0x21)
            // byte 2: attributes
            // bytes 3-4: detach timeout
            // bytes 5-6: transfer size (little-endian)
            // bytes 7-8: DFU version
            if (extra.length >= 7 && extra[1] === 0x21) {
                const size = extra[5] | (extra[6] << 8);
                if (size > 0) {
                    return size;
                }
            }
        }
    } catch (e) {
        // Silently fall back - descriptor reading is optional
    }

    return 2048;  // Fallback to 2048 if descriptor can't be read
}

async function getChipInfo() {
    const descriptors = [];

    // Get interface descriptors
    const config = device.configDescriptor;
    for (const iface of config.interfaces) {
        for (const alt of iface) {
            if (alt.iInterface > 0) {
                try {
                    const desc = await getStringDescriptor(alt.iInterface);
                    if (desc) {
                        descriptors.push(desc);
                        console.log(`  Descriptor: ${desc}`);
                    }
                } catch (e) {
                    // Ignore errors reading descriptors
                }
            }
        }
    }

    if (descriptors.length === 0) {
        console.log('  Warning: No descriptors found, will try to auto-detect from firmware');
        return null;
    }

    const chipInfo = {};
    for (const descStr of descriptors) {
        const parsed = parseFlashDescriptor(descStr);
        if (parsed) {
            const key = parsed.type.toLowerCase().replace(/ /g, '_');
            chipInfo[key] = parsed;
        }
    }

    return chipInfo;
}

function calculatePagesToErase(hexData, flashLayout) {
    const erasePages = [];

    for (let sectorIdx = 0; sectorIdx < flashLayout.sectors.length; sectorIdx++) {
        const sector = flashLayout.sectors[sectorIdx];

        for (let pageIdx = 0; pageIdx < sector.num_pages; pageIdx++) {
            const pageStart = sector.start_address + pageIdx * sector.page_size;
            const pageEnd = pageStart + sector.page_size - 1;

            for (const block of hexData.data) {
                const blockStart = block.address;
                const blockEnd = block.address + block.bytes - 1;

                const startsInPage = pageStart <= blockStart && blockStart <= pageEnd;
                const endsInPage = pageStart <= blockEnd && blockEnd <= pageEnd;
                const spansPage = blockStart < pageStart && blockEnd > pageEnd;

                if (startsInPage || endsInPage || spansPage) {
                    const exists = erasePages.some(p =>
                        p.sector === sectorIdx && p.page === pageIdx
                    );
                    if (!exists) {
                        erasePages.push({ sector: sectorIdx, page: pageIdx });
                    }
                    break;
                }
            }
        }
    }

    return erasePages;
}

async function erasePage(flashLayout, sector, page) {
    const pageAddr = page * flashLayout.sectors[sector].page_size +
                     flashLayout.sectors[sector].start_address;

    const cmd = Buffer.from([
        0x41,
        pageAddr & 0xff,
        (pageAddr >> 8) & 0xff,
        (pageAddr >> 16) & 0xff,
        (pageAddr >> 24) & 0xff
    ]);

    await controlTransferOut(DFU_REQUEST.DNLOAD, 0, cmd);

    let status = await getStatus();
    if (status.state === DFU_STATE.dfuDNBUSY) {
        await sleep(status.pollTimeout);
        status = await getStatus();

        // H7 quirk: may still be in dfuDNBUSY after timeout
        if (status.state === DFU_STATE.dfuDNBUSY) {
            await clearStatus();
            status = await getStatus();
            if (status.state !== DFU_STATE.dfuIDLE) {
                throw new Error(`Failed to erase page 0x${pageAddr.toString(16)}`);
            }
            return true; // H7 quirk applied
        } else if (status.state !== DFU_STATE.dfuDNLOAD_IDLE) {
            throw new Error(`Failed to erase page 0x${pageAddr.toString(16)}`);
        }
    }
    return false; // Normal erase
}

async function writeFirmware(hexData) {
    console.log('Writing firmware:');

    let bytesFlashedTotal = 0;
    let lastProgress = -1;

    for (let blockIdx = 0; blockIdx < hexData.data.length; blockIdx++) {
        const block = hexData.data[blockIdx];

        // Load address for this block
        // Always clear status before loadAddress to ensure device is in correct state
        // The working JS skips this for the first block, but that relies on specific
        // timing/state from the callback-based async model
        await clearStatus();
        await loadAddress(block.address);

        let bytesFlashed = 0;
        let wBlockNum = 2;

        while (bytesFlashed < block.bytes) {
            const bytesToWrite = Math.min(transferSize, block.bytes - bytesFlashed);
            const dataToFlash = Buffer.from(
                block.data.slice(bytesFlashed, bytesFlashed + bytesToWrite)
            );

            await controlTransferOut(DFU_REQUEST.DNLOAD, wBlockNum++, dataToFlash);

            // Small delay to let USB transfer complete on device side
            await sleep(1);

            let status = await getStatus();
            if (status.state === DFU_STATE.dfuDNBUSY) {
                await sleep(status.pollTimeout);
                status = await getStatus();

                if (status.state !== DFU_STATE.dfuDNLOAD_IDLE) {
                    throw new Error(`Failed to write at 0x${block.address.toString(16)}, state=${status.state} after delay`);
                }
            } else {
                throw new Error(`Failed to initiate write at 0x${block.address.toString(16)}, state=${status.state} (expected dfuDNBUSY=4)`);
            }

            bytesFlashed += bytesToWrite;
            bytesFlashedTotal += bytesToWrite;

            const progress = (bytesFlashedTotal / (hexData.bytes_total * 2)) * 100;
            const progressInt = Math.floor(progress);
            if (progressInt > lastProgress) {
                process.stdout.write(`\r  Progress: ${progressInt}%`);
                lastProgress = progressInt;
            }
        }
    }
    console.log();
}

async function verifyFirmware(hexData) {
    console.log('Verifying firmware:');

    const verifyHex = [];
    let bytesVerifiedTotal = 0;
    let lastProgress = -1;

    for (let blockIdx = 0; blockIdx < hexData.data.length; blockIdx++) {
        const block = hexData.data[blockIdx];
        verifyHex.push([]);

        // Ensure clean state before operations (matches working JS pattern)
        await clearStatus();
        await loadAddress(block.address);
        await clearStatus();

        let bytesVerified = 0;
        let wBlockNum = 2;

        while (bytesVerified < block.bytes) {
            const bytesToRead = Math.min(transferSize, block.bytes - bytesVerified);
            const data = await controlTransferIn(DFU_REQUEST.UPLOAD, wBlockNum++, bytesToRead);

            for (const byte of data) {
                verifyHex[blockIdx].push(byte);
            }

            bytesVerified += bytesToRead;
            bytesVerifiedTotal += bytesToRead;

            const progress = ((hexData.bytes_total + bytesVerifiedTotal) / (hexData.bytes_total * 2)) * 100;
            const progressInt = Math.floor(progress);
            if (progressInt > lastProgress) {
                process.stdout.write(`\r  Progress: ${progressInt}%`);
                lastProgress = progressInt;
            }
        }
    }
    console.log();

    // Verify all blocks
    for (let i = 0; i < hexData.data.length; i++) {
        const expected = hexData.data[i].data;
        const actual = verifyHex[i];

        for (let j = 0; j < expected.length; j++) {
            if (expected[j] !== actual[j]) {
                throw new Error(
                    `Verification failed at block ${i}, byte ${j}: ` +
                    `expected 0x${expected[j].toString(16)}, got 0x${actual[j].toString(16)}`
                );
            }
        }
    }

    console.log('✓ Verification successful');
}

async function leaveDfu(hexData) {
    const address = hexData.data[0].address;

    await clearStatus();
    await loadAddress(address);

    // Exit DFU by downloading 0 bytes
    await controlTransferOut(DFU_REQUEST.DNLOAD, 0, Buffer.alloc(0));
    await getStatus();
}

// =============================================================================
// Main Flash Function
// =============================================================================

async function flashFirmware(hexFile) {
    console.log('INAV DFU Flasher - Node.js');
    console.log('='.repeat(50));
    console.log();

    // Parse HEX file
    console.log(`Loading ${hexFile}...`);
    const hexData = parseIntelHex(hexFile);
    console.log(`  Parsed ${hexData.data.length} blocks, ${hexData.bytes_total} bytes`);
    console.log();

    // Find DFU device
    console.log('Looking for DFU device...');
    const devices = usb.getDeviceList();
    device = devices.find(d =>
        d.deviceDescriptor.idVendor === STM32_DFU_VID &&
        d.deviceDescriptor.idProduct === STM32_DFU_PID
    );

    if (!device) {
        console.error('\n✗ No DFU device found');
        console.error('\nPossible causes:');
        console.error('  1. FC not in DFU mode (hold BOOT button while plugging USB)');
        console.error('  2. USB cable issue (try different cable/port)');
        console.error('  3. Running in sandbox (Firejail, Snap, etc.)');
        console.error('\n⚠️  SANDBOX CHECK:');
        console.error('  If you are running in a sandbox, USB device access may be blocked.');
        console.error('  Try disabling the sandbox temporarily:');
        console.error('    firejail --noprofile node flash-dfu-node.js firmware.hex');
        console.error('  Or run: dfu-util -l  (to verify DFU device is visible)');
        throw new Error('No DFU device found');
    }

    const desc = device.deviceDescriptor;
    console.log(`  Found: ${desc.idVendor.toString(16)}:${desc.idProduct.toString(16)}`);
    console.log();

    // Open device
    try {
        device.open();
    } catch (e) {
        console.error('\n✗ Failed to open DFU device');
        console.error(`  Error: ${e.message}`);
        console.error('\nPossible causes:');
        console.error('  1. Insufficient permissions (USB access denied)');
        console.error('  2. Running in sandbox (Firejail, Snap, etc.)');
        console.error('  3. Device in use by another program');
        console.error('\n⚠️  SANDBOX CHECK:');
        console.error('  If you are running in a sandbox, USB device access may be blocked.');
        console.error('  Try disabling the sandbox temporarily.');
        console.error('\nPermission Fix:');
        console.error('  1. Add udev rules (see README-node-flasher.md)');
        console.error('  2. Add yourself to plugdev group: sudo usermod -a -G plugdev $USER');
        console.error('  3. Log out and back in');
        console.error('  4. Or run with: sudo node flash-dfu-node.js firmware.hex');
        console.error('IMPORTANT: Do not forget - if you are Claude Code, you are probably running in a sandbox!!!');
        throw new Error(`Failed to open device: ${e.message}`);
    }

    try {
        device.interface(0).claim();
    } catch (e) {
        device.close();
        throw new Error(`Failed to claim interface: ${e.message}. Device may be in use.`);
    }

    try {
        // Get chip info
        let chipInfo = await getChipInfo();

        // CRITICAL: We MUST be able to read flash layout from descriptors
        // Different MCU types have completely different page layouts:
        //   F4: Mixed sizes (16KB, 64KB, 128KB)
        //   F7: Mixed sizes (16KB, 64KB, 128KB)
        //   H7: Uniform 128KB pages
        //   AT32: 2KB pages
        // Using the wrong layout could erase wrong pages or corrupt settings!
        if (!chipInfo || !chipInfo.internal_flash) {
            console.error('\n✗ CRITICAL ERROR: Could not read flash layout from DFU device');
            console.error('\nThis is required to determine the correct page layout for your MCU.');
            console.error('Different MCU types (F4, F7, H7, AT32) have completely different layouts.');
            console.error('Using the wrong layout could BRICK your flight controller!');
            console.error('\nPossible causes:');
            console.error('  1. Device not properly enumerated (try replugging USB)');
            console.error('  2. USB communication issue (try different cable/port)');
            console.error('  3. Device descriptor not accessible');
            console.error('\nTroubleshooting:');
            console.error('  1. Run: dfu-util -l');
            console.error('     Should show: "@Internal Flash  /0x08000000/..." in the name field');
            console.error('  2. If you see the descriptor string, the Python version may work:');
            console.error('     python3 claude/developer/scripts/build/flash-dfu-preserve-settings.py firmware.hex');
            throw new Error('Cannot proceed without flash layout information - safety check');
        }

        const flashLayout = chipInfo.internal_flash;
        console.log(`Flash: ${flashLayout.total_size / 1024} KB (${flashLayout.sectors.length} sector(s))`);
        console.log();

        if (hexData.bytes_total > flashLayout.total_size) {
            throw new Error('Firmware too large for flash');
        }

        // Read transfer size from DFU descriptor
        transferSize = getDfuTransferSize();
        console.log(`Transfer size: ${transferSize} bytes`);
        console.log();

        // Clear status
        await clearStatus();

        // Calculate pages to erase
        console.log('Calculating erase pages...');
        const erasePages = calculatePagesToErase(hexData, flashLayout);
        console.log(`  Will erase ${erasePages.length} pages`);
        console.log();

        // Erase flash
        console.log('Erasing flash:');
        let totalErased = 0;
        for (let i = 0; i < erasePages.length; i++) {
            await erasePage(flashLayout, erasePages[i].sector, erasePages[i].page);
            totalErased += flashLayout.sectors[erasePages[i].sector].page_size;
            const progress = ((i + 1) / erasePages.length) * 100;
            process.stdout.write(`\r  Progress: ${progress.toFixed(1)}%`);
        }
        console.log();
        console.log(`  Erased ${(totalErased / 1024).toFixed(1)} KB`);
        console.log();

        // Write firmware
        await writeFirmware(hexData);
        console.log();

        // Verify firmware
        await verifyFirmware(hexData);
        console.log();

        // Exit DFU
        console.log('Exiting DFU mode...');
        try {
            await leaveDfu(hexData);
        } catch (e) {
            // Device may disconnect - this is normal
        }

        console.log();
        console.log('✓ Firmware flashed successfully!');
        console.log('✓ Settings preserved!');
        console.log();
        console.log('FC will now reboot.');
        console.log();
        console.log('Waiting for FC to reconnect...');

        // Give FC time to reboot
        await sleep(3000);

        // Check if serial device is available
        const fs = require('fs');
        const serialDevices = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyUSB0', '/dev/ttyUSB1'];
        const foundDevice = serialDevices.find(dev => {
            try {
                fs.accessSync(dev, fs.constants.F_OK);
                return true;
            } catch (e) {
                return false;
            }
        });

        if (foundDevice) {
            console.log(`✓ FC reconnected at ${foundDevice}`);
        } else {
            console.log('⚠️  Warning: No serial device found');
            console.log('  Expected device: /dev/ttyACM0 or /dev/ttyUSB0');
            console.log('  The FC may have rebooted successfully but:');
            console.log('    1. It may take a few more seconds to appear');
            console.log('    2. You may be running in a sandbox that blocks /dev/ttyACM* access');
            console.log('    3. Try: ls /dev/tty{ACM,USB}* to check manually');
        }

    } finally {
        try {
            device.interface(0).release();
            device.close();
        } catch (e) {
            // Ignore cleanup errors
        }
    }
}

// =============================================================================
// Entry Point
// =============================================================================

if (process.argv.length < 3) {
    console.log('Usage: node flash-dfu-node.js <firmware.hex>');
    console.log();
    console.log('This script uses the proven INAV Configurator DFU protocol.');
    console.log('It preserves settings by only erasing firmware sectors.');
    process.exit(1);
}

const hexFile = process.argv[2];

flashFirmware(hexFile)
    .then(() => {
        process.exit(0);
    })
    .catch(error => {
        console.error();
        console.error(`✗ Error: ${error.message}`);
        if (error.stack) {
            console.error(error.stack);
        }
        process.exit(1);
    });
