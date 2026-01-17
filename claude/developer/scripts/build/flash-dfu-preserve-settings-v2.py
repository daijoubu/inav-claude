#!/usr/bin/env python3
"""
DFU Flash with Settings Preservation - Direct Translation from Configurator

This is a direct translation of inav-configurator/js/protocols/stm32usbdfu.js
"""

import usb.core
import usb.util
import sys
import time

# DFU Protocol Constants (from configurator)
DFU_REQUEST = {
    'DNLOAD': 0x01,
    'GETSTATUS': 0x03,
    'CLRSTATUS': 0x04,
}

DFU_STATE = {
    'dfuIDLE': 2,
    'dfuDNLOAD_SYNC': 3,
    'dfuDNBUSY': 4,
    'dfuDNLOAD_IDLE': 5,
    'dfuERROR': 10
}

# STM32 DFU Device IDs
STM32_DFU_VID = 0x0483
STM32_DFU_PID = 0xdf11

# Flash layout for STM32F7
FLASH_LAYOUT_F7 = {
    'start_address': 0x08000000,
    'sectors': [
        {'start_address': 0x08000000, 'page_size': 16384, 'num_pages': 4},
        {'start_address': 0x08010000, 'page_size': 65536, 'num_pages': 1},
        {'start_address': 0x08020000, 'page_size': 131072, 'num_pages': 3}
    ]
}

def parse_intel_hex(filename):
    """Parse Intel HEX file"""
    blocks = []
    current_block = None
    extended_address = 0

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line[0] != ':':
                continue

            byte_count = int(line[1:3], 16)
            address = int(line[3:7], 16)
            record_type = int(line[7:9], 16)
            data = line[9:9+byte_count*2]

            if record_type == 0x00:  # Data record
                full_address = extended_address + address
                data_bytes = [int(data[i:i+2], 16) for i in range(0, len(data), 2)]

                if current_block and current_block['address'] + current_block['bytes'] == full_address:
                    current_block['data'].extend(data_bytes)
                    current_block['bytes'] += byte_count
                else:
                    if current_block:
                        blocks.append(current_block)
                    current_block = {
                        'address': full_address,
                        'bytes': byte_count,
                        'data': data_bytes
                    }

            elif record_type == 0x01:  # End of file
                if current_block:
                    blocks.append(current_block)
                break

            elif record_type == 0x04:  # Extended linear address
                extended_address = int(data, 16) << 16

    total_bytes = sum(block['bytes'] for block in blocks)
    return {'data': blocks, 'bytes_total': total_bytes}

def calculate_pages_to_erase(hex_data, flash_layout):
    """Calculate which flash pages need to be erased"""
    pages = []

    for sector_idx, sector in enumerate(flash_layout['sectors']):
        for page_idx in range(sector['num_pages']):
            page_start = sector['start_address'] + page_idx * sector['page_size']
            page_end = page_start + sector['page_size'] - 1

            for block in hex_data['data']:
                block_start = block['address']
                block_end = block['address'] + block['bytes'] - 1

                starts_in_page = page_start <= block_start <= page_end
                ends_in_page = page_start <= block_end <= page_end
                spans_page = block_start < page_start and block_end > page_end

                if starts_in_page or ends_in_page or spans_page:
                    pages.append({'sector': sector_idx, 'page': page_idx})
                    break

    return pages

def control_transfer_out(dev, request, value, data):
    """OUT control transfer"""
    return dev.ctrl_transfer(0x21, request, value, 0, data, 5000)

def control_transfer_in(dev, request, length):
    """IN control transfer"""
    return dev.ctrl_transfer(0xA1, request, 0, 0, length, 5000)

def get_status(dev):
    """Get DFU status"""
    data = control_transfer_in(dev, DFU_REQUEST['GETSTATUS'], 6)
    return {
        'status': data[0],
        'poll_timeout': data[1] | (data[2] << 8) | (data[3] << 16),
        'state': data[4]
    }

def clear_status(dev):
    """Clear DFU status"""
    control_transfer_out(dev, DFU_REQUEST['CLRSTATUS'], 0, b'')

def load_address(dev, address):
    """Load address pointer - direct translation from configurator"""
    cmd = bytes([0x21, address & 0xff, (address >> 8) & 0xff, (address >> 16) & 0xff, (address >> 24) & 0xff])

    control_transfer_out(dev, DFU_REQUEST['DNLOAD'], 0, cmd)
    status = get_status(dev)

    if status['state'] == DFU_STATE['dfuDNBUSY']:
        delay = status['poll_timeout'] / 1000.0
        time.sleep(delay)
        status = get_status(dev)

        if status['state'] != DFU_STATE['dfuDNLOAD_IDLE']:
            raise Exception(f"Failed to load address 0x{address:08x}")

def erase_page(dev, flash_layout, sector, page):
    """Erase a single flash page - direct translation from configurator"""
    page_addr = page * flash_layout['sectors'][sector]['page_size'] + flash_layout['sectors'][sector]['start_address']
    cmd = bytes([0x41, page_addr & 0xff, (page_addr >> 8) & 0xff, (page_addr >> 16) & 0xff, (page_addr >> 24) & 0xff])

    print(f"  Erasing sector {sector}, page {page} @ 0x{page_addr:08x}")

    control_transfer_out(dev, DFU_REQUEST['DNLOAD'], 0, cmd)
    status = get_status(dev)

    if status['state'] == DFU_STATE['dfuDNBUSY']:
        delay = status['poll_timeout'] / 1000.0
        time.sleep(delay)
        status = get_status(dev)

        # H7 workaround
        if status['state'] == DFU_STATE['dfuDNBUSY']:
            clear_status(dev)
            status = get_status(dev)

    if status['state'] not in [DFU_STATE['dfuDNLOAD_IDLE'], DFU_STATE['dfuIDLE']]:
        raise Exception(f"Failed to erase page @ 0x{page_addr:08x}, state={status['state']}")

def write_data(dev, block_num, data):
    """Write data block - direct translation from configurator"""
    control_transfer_out(dev, DFU_REQUEST['DNLOAD'], block_num, bytes(data))
    status = get_status(dev)

    if status['state'] == DFU_STATE['dfuDNBUSY']:
        delay = status['poll_timeout'] / 1000.0
        time.sleep(delay)
        status = get_status(dev)

        if status['state'] != DFU_STATE['dfuDNLOAD_IDLE']:
            raise Exception(f"Write failed, state={status['state']}")
    else:
        raise Exception(f"Failed to initiate write, state={status['state']}")

def flash_firmware(hex_file):
    """Main flashing function - structure from configurator"""
    print("INAV DFU Flasher with Settings Preservation")
    print("=" * 44)
    print()

    # Parse hex file
    print(f"Reading {hex_file}...")
    hex_data = parse_intel_hex(hex_file)
    print(f"Parsed {len(hex_data['data'])} blocks, {hex_data['bytes_total']} bytes total\n")

    # Find DFU device
    print("Looking for STM32 DFU device...")
    dev = usb.core.find(idVendor=STM32_DFU_VID, idProduct=STM32_DFU_PID)

    if dev is None:
        raise Exception("No STM32 DFU device found. Put FC into DFU mode first.")

    print(f"Found DFU device\n")

    # Claim interface
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)

    dev.set_configuration()
    usb.util.claim_interface(dev, 0)

    try:
        # Clear any error state
        clear_status(dev)

        # Calculate pages to erase
        print("Calculating pages to erase...")
        flash_layout = FLASH_LAYOUT_F7
        pages_to_erase = calculate_pages_to_erase(hex_data, flash_layout)
        print(f"Will erase {len(pages_to_erase)} pages (preserving config area)\n")

        # Erase pages (case 3 in configurator)
        print("Erasing flash pages:")
        for i, page_info in enumerate(pages_to_erase):
            erase_page(dev, flash_layout, page_info['sector'], page_info['page'])
            progress = (i + 1) / len(pages_to_erase) * 100
            print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
        print("\n")

        # Write firmware (case 4 in configurator)
        # "we dont need to clear the state as we are already using DFU_DNLOAD"
        print("Writing firmware:")
        TRANSFER_SIZE = 2048
        total_written = 0

        for block_idx, block in enumerate(hex_data['data']):
            # Load address first (like configurator line 943)
            load_address(dev, block['address'])

            # Write data in chunks
            wBlockNum = 2  # Required by DFU
            offset = 0
            while offset < block['bytes']:
                chunk_size = min(TRANSFER_SIZE, block['bytes'] - offset)
                chunk = block['data'][offset:offset + chunk_size]

                write_data(dev, wBlockNum, chunk)
                wBlockNum += 1
                total_written += chunk_size
                offset += chunk_size

                progress = total_written / hex_data['bytes_total'] * 100
                print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
        print("\n")

        # Exit DFU mode (like configurator's leave() function)
        print("Exiting DFU mode...")
        try:
            clear_status(dev)
            load_address(dev, hex_data['data'][0]['address'])
            control_transfer_out(dev, DFU_REQUEST['DNLOAD'], 0, b'')
            get_status(dev)
        except:
            # Expected - device reboots and disconnects
            pass

        print("\n✓ Firmware flashed successfully!")
        print("✓ Settings preserved!")
        print("\nFC will now reboot with new firmware.")

    finally:
        usb.util.release_interface(dev, 0)
        usb.util.dispose_resources(dev)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 flash-dfu-preserve-settings-v2.py <firmware.hex>")
        sys.exit(1)

    hex_file = sys.argv[1]

    try:
        flash_firmware(hex_file)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
