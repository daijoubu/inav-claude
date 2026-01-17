/**
 * DFU Flash with Settings Preservation
 *
 * This script flashes INAV firmware via DFU while preserving settings.
 * It performs selective page erase (only erases pages containing firmware data).
 *
 * Based on INAV Configurator's stm32usbdfu.js implementation.
 *
 * Usage: node flash-dfu-preserve-settings.js <firmware.hex>
 */

import usb from 'usb';
import fs from 'fs';

// DFU Protocol Constants
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

// STM32 DFU Device IDs
const STM32_DFU = {
    vendorId: 0x0483,
    productId: 0xdf11
};

// Flash layout for STM32F7 (VANTAC_RF007 uses STM32F722)
const FLASH_LAYOUT_F7 = {
    start_address: 0x08000000,
    sectors: [
        { start_address: 0x08000000, page_size: 16384, num_pages: 4 },   // 4x16KB  = 64KB
        { start_address: 0x08010000, page_size: 65536, num_pages: 1 },   // 1x64KB  = 64KB
        { start_address: 0x08020000, page_size: 131072, num_pages: 3 }   // 3x128KB = 384KB
    ]
};

/**
 * Parse Intel HEX file
 */
function parseIntelHex(hexContent) {
    const lines = hexContent.split('\n');
    const blocks = [];
    let currentBlock = null;
    let extendedAddress = 0;

    for (const line of lines) {
        const trimmed = line.trim();
        if (\!trimmed || trimmed[0] \!== ':') continue;

        const byteCount = parseInt(trimmed.substr(1, 2), 16);
        const address = parseInt(trimmed.substr(3, 4), 16);
        const recordType = parseInt(trimmed.substr(7, 2), 16);
        const data = trimmed.substr(9, byteCount * 2);

        switch (recordType) {
            case 0x00: // Data record
                const fullAddress = extendedAddress + address;
                const dataBytes = [];
                for (let i = 0; i < byteCount; i++) {
                    dataBytes.push(parseInt(data.substr(i * 2, 2), 16));
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
                break;

            case 0x01: // End of file
                if (currentBlock) blocks.push(currentBlock);
                break;

            case 0x04: // Extended linear address
                extendedAddress = parseInt(data, 16) << 16;
                break;
        }
    }

    const totalBytes = blocks.reduce((sum, block) => sum + block.bytes, 0);
    return { data: blocks, bytes_total: totalBytes };
}

/**
 * Calculate which flash pages need to be erased
 */
function calculatePagesToErase(hexData, flashLayout) {
    const pages = [];

    for (let sectorIdx = 0; sectorIdx < flashLayout.sectors.length; sectorIdx++) {
        const sector = flashLayout.sectors[sectorIdx];

        for (let pageIdx = 0; pageIdx < sector.num_pages; pageIdx++) {
            const pageStart = sector.start_address + pageIdx * sector.page_size;
            const pageEnd = pageStart + sector.page_size - 1;

            for (const block of hexData.data) {
                const blockStart = block.address;
                const blockEnd = block.address + block.bytes - 1;

                const startsInPage = blockStart >= pageStart && blockStart <= pageEnd;
                const endsInPage = blockEnd >= pageStart && blockEnd <= pageEnd;
                const spansPage = blockStart < pageStart && blockEnd > pageEnd;

                if (startsInPage || endsInPage || spansPage) {
                    pages.push({ sector: sectorIdx, page: pageIdx });
                    break;
                }
            }
        }
    }

    return pages;
}

/**
 * DFU control transfer wrapper
 */
function dfuControlTransfer(device, direction, request, value, index, dataOrLength) {
    const bmRequestType = direction === 'out' ? 0x21 : 0xA1;
    
    return new Promise((resolve, reject) => {
        if (direction === 'out') {
            const buffer = Buffer.isBuffer(dataOrLength) ? dataOrLength : Buffer.from(dataOrLength);
            device.controlTransfer(bmRequestType, request, value, index, buffer, (error) => {
                if (error) reject(error);
                else resolve();
            });
        } else {
            device.controlTransfer(bmRequestType, request, value, index, dataOrLength, (error, data) => {
                if (error) reject(error);
                else resolve(Buffer.from(data));
            });
        }
    });
}

/**
 * Get DFU status
 */
async function getDfuStatus(device) {
    const data = await dfuControlTransfer(device, 'in', DFU_REQUEST.GETSTATUS, 0, 0, 6);
    return {
        status: data[0],
        pollTimeout: data[1] | (data[2] << 8) | (data[3] << 16),
        state: data[4]
    };
}

/**
 * Clear DFU status
 */
async function clearDfuStatus(device) {
    await dfuControlTransfer(device, 'out', DFU_REQUEST.CLRSTATUS, 0, 0, Buffer.alloc(0));
}

/**
 * Erase a single flash page
 */
async function erasePage(device, flashLayout, sector, page) {
    const pageAddr = page * flashLayout.sectors[sector].page_size + flashLayout.sectors[sector].start_address;
    const cmd = Buffer.from([
        0x41,
        pageAddr & 0xff,
        (pageAddr >> 8) & 0xff,
        (pageAddr >> 16) & 0xff,
        (pageAddr >> 24) & 0xff
    ]);

    console.log(`  Erasing sector ${sector}, page ${page} @ 0x${pageAddr.toString(16)}`);

    await dfuControlTransfer(device, 'out', DFU_REQUEST.DNLOAD, 0, 0, cmd);
    
    let status = await getDfuStatus(device);
    if (status.state === DFU_STATE.dfuDNBUSY) {
        await new Promise(resolve => setTimeout(resolve, status.pollTimeout));
        status = await getDfuStatus(device);

        if (status.state === DFU_STATE.dfuDNBUSY) {
            console.log('  Clearing status (H7 workaround)');
            await clearDfuStatus(device);
            status = await getDfuStatus(device);
        }
    }

    if (status.state \!== DFU_STATE.dfuDNLOAD_IDLE && status.state \!== DFU_STATE.dfuIDLE) {
        throw new Error(`Failed to erase page @ 0x${pageAddr.toString(16)}, state=${status.state}`);
    }
}

/**
 * Set address pointer
 */
async function setAddress(device, address) {
    const cmd = Buffer.from([
        0x21,
        address & 0xff,
        (address >> 8) & 0xff,
        (address >> 16) & 0xff,
        (address >> 24) & 0xff
    ]);

    await dfuControlTransfer(device, 'out', DFU_REQUEST.DNLOAD, 0, 0, cmd);
    let status = await getDfuStatus(device);
    if (status.state === DFU_STATE.dfuDNLOAD_SYNC) {
        status = await getDfuStatus(device);
    }
}

/**
 * Write data block to flash
 */
async function writeBlock(device, blockNum, data) {
    await dfuControlTransfer(device, 'out', DFU_REQUEST.DNLOAD, blockNum, 0, Buffer.from(data));
    
    let status = await getDfuStatus(device);
    if (status.state === DFU_STATE.dfuDNLOAD_SYNC) {
        await new Promise(resolve => setTimeout(resolve, 10));
        status = await getDfuStatus(device);
    }

    if (status.state \!== DFU_STATE.dfuDNLOAD_IDLE) {
        throw new Error(`Write failed, state=${status.state}`);
    }
}

/**
 * Exit DFU mode
 */
async function exitDfu(device) {
    await dfuControlTransfer(device, 'out', DFU_REQUEST.DNLOAD, 0, 0, Buffer.alloc(0));
    await getDfuStatus(device);
}

/**
 * Main flashing function
 */
async function flashFirmware(hexFile) {
    console.log('INAV DFU Flasher with Settings Preservation');
    console.log('============================================\n');

    // Parse hex file
    console.log(`Reading ${hexFile}...`);
    const hexContent = fs.readFileSync(hexFile, 'utf8');
    const hexData = parseIntelHex(hexContent);
    console.log(`Parsed ${hexData.data.length} blocks, ${hexData.bytes_total} bytes total\n`);

    // Find DFU device
    console.log('Looking for STM32 DFU device...');
    const devices = usb.getDeviceList();
    const dfuDevice = devices.find(d =>
        d.deviceDescriptor.idVendor === STM32_DFU.vendorId &&
        d.deviceDescriptor.idProduct === STM32_DFU.productId
    );

    if (\!dfuDevice) {
        throw new Error('No STM32 DFU device found. Put FC into DFU mode first.');
    }

    console.log(`Found DFU device\n`);

    // Open device
    dfuDevice.open();
    dfuDevice.timeout = 30000;
    
    const iface = dfuDevice.interface(0);
    if (process.platform \!== 'win32') {
        try {
            if (iface.isKernelDriverActive()) {
                iface.detachKernelDriver();
            }
        } catch (e) {
            // Ignore if already detached
        }
    }
    iface.claim();

    try {
        // Clear any error state
        await clearDfuStatus(dfuDevice);

        // Calculate pages to erase
        console.log('Calculating pages to erase...');
        const flashLayout = FLASH_LAYOUT_F7;
        const pagesToErase = calculatePagesToErase(hexData, flashLayout);
        console.log(`Will erase ${pagesToErase.length} pages (preserving config area)\n`);

        // Erase pages
        console.log('Erasing flash pages:');
        for (let i = 0; i < pagesToErase.length; i++) {
            const { sector, page } = pagesToErase[i];
            await erasePage(dfuDevice, flashLayout, sector, page);
            process.stdout.write(`\r  Progress: ${((i + 1) / pagesToErase.length * 100).toFixed(1)}%`);
        }
        console.log('\n');

        // Write firmware
        console.log('Writing firmware:');
        const TRANSFER_SIZE = 2048;
        let blockNum = 2;
        let totalWritten = 0;

        for (const block of hexData.data) {
            // Set address
            await setAddress(dfuDevice, block.address);
            blockNum++;

            // Write data in chunks
            for (let offset = 0; offset < block.bytes; offset += TRANSFER_SIZE) {
                const chunkSize = Math.min(TRANSFER_SIZE, block.bytes - offset);
                const chunk = block.data.slice(offset, offset + chunkSize);

                await writeBlock(dfuDevice, blockNum++, chunk);
                totalWritten += chunkSize;

                process.stdout.write(`\r  Progress: ${(totalWritten / hexData.bytes_total * 100).toFixed(1)}%`);
            }
        }
        console.log('\n');

        // Exit DFU mode
        console.log('Exiting DFU mode...');
        await exitDfu(dfuDevice);

        console.log('\n✓ Firmware flashed successfully\!');
        console.log('✓ Settings preserved\!');
        console.log('\nFC will now reboot with new firmware.');

    } finally {
        try {
            iface.release();
        } catch (e) {}
        try {
            dfuDevice.close();
        } catch (e) {}
    }
}

// Main
const args = process.argv.slice(2);
if (args.length === 0) {
    console.log('Usage: node flash-dfu-preserve-settings.js <firmware.hex>');
    process.exit(1);
}

const hexFile = args[0];
if (\!fs.existsSync(hexFile)) {
    console.error(`Error: File not found: ${hexFile}`);
    process.exit(1);
}

flashFirmware(hexFile).catch(err => {
    console.error(`\n✗ Error: ${err.message}`);
    process.exit(1);
});
