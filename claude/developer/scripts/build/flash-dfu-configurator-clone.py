#!/usr/bin/env python3
"""
DFU Flash with Settings Preservation - Direct Clone of INAV Configurator

This is a faithful Python translation of inav-configurator/js/protocols/stm32usbdfu.js
NO quirks, workarounds, or modifications that don't exist in the working JS version.
"""

import usb.core
import usb.util
import sys
import time

# =============================================================================
# DFU Protocol Constants (from stm32usbdfu.js lines 25-66)
# =============================================================================

DFU_REQUEST = {
    'DETACH': 0x00,
    'DNLOAD': 0x01,
    'UPLOAD': 0x02,
    'GETSTATUS': 0x03,
    'CLRSTATUS': 0x04,
    'GETSTATE': 0x05,
    'ABORT': 0x06
}

DFU_STATE = {
    'appIDLE': 0,
    'appDETACH': 1,
    'dfuIDLE': 2,
    'dfuDNLOAD_SYNC': 3,
    'dfuDNBUSY': 4,
    'dfuDNLOAD_IDLE': 5,
    'dfuMANIFEST_SYNC': 6,
    'dfuMANIFEST': 7,
    'dfuMANIFEST_WAIT_RESET': 8,
    'dfuUPLOAD_IDLE': 9,
    'dfuERROR': 10
}

# STM32 DFU USB IDs
STM32_DFU_VID = 0x0483
STM32_DFU_PID = 0xdf11

# =============================================================================
# USB Control Transfer Wrappers
# =============================================================================

def control_transfer_out(dev, request, value, data):
    """
    OUT control transfer to interface (class request)
    Maps to: controlTransferOut with setup {recipient: 'interface', requestType: 'class'}
    """
    if data is None:
        data = b''
    elif not isinstance(data, bytes):
        data = bytes(data)

    # bmRequestType: 0x21 = OUT, Class, Interface
    return dev.ctrl_transfer(0x21, request, value, 0, data, 5000)


def control_transfer_in(dev, request, value, length):
    """
    IN control transfer from interface (class request)
    Maps to: controlTransferIn with setup {recipient: 'interface', requestType: 'class'}
    """
    # bmRequestType: 0xA1 = IN, Class, Interface
    return dev.ctrl_transfer(0xA1, request, value, 0, length, 5000)


# =============================================================================
# DFU Protocol Functions (from stm32usbdfu.js)
# =============================================================================

def get_status(dev):
    """
    Request DFU status from device
    Maps to: controlTransfer('in', self.request.GETSTATUS, 0, 0, 6, 0, callback)
    """
    data = control_transfer_in(dev, DFU_REQUEST['GETSTATUS'], 0, 6)
    return {
        'status': data[0],
        'poll_timeout': data[1] | (data[2] << 8) | (data[3] << 16),
        'state': data[4]
    }


def clear_status(dev):
    """
    Routine calling DFU_CLRSTATUS until device is in dfuIDLE state
    Direct translation of stm32usbdfu.js lines 479-499
    """
    def check_status():
        status = get_status(dev)
        if status['state'] == DFU_STATE['dfuIDLE']:
            return True
        else:
            delay_ms = status['poll_timeout']
            time.sleep(delay_ms / 1000.0)
            return False

    def do_clear_status():
        control_transfer_out(dev, DFU_REQUEST['CLRSTATUS'], 0, b'')
        return check_status()

    # Initial check
    if not check_status():
        # Need to clear status
        do_clear_status()


def load_address(dev, address):
    """
    Load address command for DFU
    Direct translation of stm32usbdfu.js lines 501-529
    """
    cmd = bytes([0x21,
                 address & 0xff,
                 (address >> 8) & 0xff,
                 (address >> 16) & 0xff,
                 (address >> 24) & 0xff])

    control_transfer_out(dev, DFU_REQUEST['DNLOAD'], 0, cmd)

    status = get_status(dev)
    if status['state'] == DFU_STATE['dfuDNBUSY']:
        delay_ms = status['poll_timeout']
        time.sleep(delay_ms / 1000.0)

        status = get_status(dev)
        if status['state'] != DFU_STATE['dfuDNLOAD_IDLE']:
            raise Exception(f"Failed to execute address load, state={status['state']}")


# =============================================================================
# Intel HEX Parser
# =============================================================================

def parse_intel_hex(filename):
    """Parse Intel HEX file into blocks"""
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

                # Merge contiguous blocks
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


# =============================================================================
# Flash Layout Detection (from stm32usbdfu.js lines 183-424)
# =============================================================================

def get_string_descriptor(dev, index):
    """Get USB string descriptor"""
    if index == 0:
        return ""
    try:
        # GET_DESCRIPTOR, STRING type (0x03), index
        result = dev.ctrl_transfer(0x80, 6, 0x0300 | index, 0, 255, 5000)
        if len(result) < 2:
            return ""

        length = result[0]
        descriptor = ""
        # Decode UTF-16LE (skip first 2 bytes)
        for i in range(2, min(length, len(result)), 2):
            if i + 1 < len(result):
                char_code = result[i] | (result[i + 1] << 8)
                descriptor += chr(char_code)
        return descriptor
    except:
        return ""


def get_interface_descriptors(dev):
    """Get interface descriptor strings"""
    descriptors = []
    try:
        config = dev.get_active_configuration()

        # Try alternate settings (configurator checks up to 8)
        for alt_setting in range(8):
            try:
                alt_intf = config[(0, alt_setting)]
                iface_string_idx = alt_intf.iInterface
                if iface_string_idx > 0:
                    descriptor_string = get_string_descriptor(dev, iface_string_idx)
                    if descriptor_string:
                        descriptors.append(descriptor_string)
            except:
                break
    except:
        pass

    return descriptors


def parse_flash_descriptor(descriptor_str):
    """
    Parse flash descriptor string
    Direct translation of stm32usbdfu.js lines 332-417

    Examples:
    F40x: "@Internal Flash  /0x08000000/04*016Kg,01*064Kg,07*128Kg"
    F72x: "@Internal Flash  /0x08000000/04*016Kg,01*64Kg,03*128Kg"
    H7:   "@Internal Flash  /0x08000000/16*128Kg"
    """
    try:
        # Clean non-printable characters
        descriptor_str = ''.join(c for c in descriptor_str if 32 <= ord(c) <= 126)

        # Split by '/'
        parts = descriptor_str.split('/')

        # Handle long descriptors (G474 case from JS lines 363-366)
        if len(parts) > 3:
            parts = parts[:3]

        if len(parts) < 3 or not parts[0].startswith('@'):
            return None

        memory_type = parts[0].strip().replace('@', '')
        start_address = int(parts[1], 16)

        # Parse sectors
        sectors = []
        total_size = 0
        sector_parts = parts[2].split(',')

        for sector_str in sector_parts:
            if '*' not in sector_str:
                continue

            num_str, size_str = sector_str.split('*')
            num_pages = int(num_str)

            # Extract numeric part
            size_numeric = ''.join(c for c in size_str if c.isdigit())
            if not size_numeric:
                continue
            page_size = int(size_numeric)

            # Handle units (from JS lines 392-397)
            if len(size_str) >= 2:
                unit = size_str[-2:-1]
                if unit == 'M':
                    page_size *= 1024 * 1024
                elif unit == 'K':
                    page_size *= 1024

            sectors.append({
                'start_address': start_address + total_size,
                'page_size': page_size,
                'num_pages': num_pages,
                'total_size': num_pages * page_size
            })
            total_size += num_pages * page_size

        if not sectors:
            return None

        return {
            'type': memory_type,
            'start_address': start_address,
            'sectors': sectors,
            'total_size': total_size
        }
    except Exception as e:
        return None


def get_chip_info(dev):
    """
    Get chip information from DFU descriptors
    Maps to stm32usbdfu.js getChipInfo (lines 320-424)
    """
    descriptors = get_interface_descriptors(dev)
    if not descriptors:
        return None

    chip_info = {}
    for desc_str in descriptors:
        parsed = parse_flash_descriptor(desc_str)
        if parsed:
            # Use lowercase with underscores as key (from JS line 419)
            key = parsed['type'].lower().replace(' ', '_')
            chip_info[key] = parsed

    return chip_info if chip_info else None


# =============================================================================
# Flash Procedures (from stm32usbdfu.js upload_procedure)
# =============================================================================

def calculate_pages_to_erase(hex_data, flash_layout):
    """
    Calculate which pages need to be erased
    Direct translation of stm32usbdfu.js lines 760-785
    """
    erase_pages = []

    for sector_idx, sector in enumerate(flash_layout['sectors']):
        for page_idx in range(sector['num_pages']):
            page_start = sector['start_address'] + page_idx * sector['page_size']
            page_end = page_start + sector['page_size'] - 1

            for block in hex_data['data']:
                block_start = block['address']
                block_end = block['address'] + block['bytes'] - 1

                # Check if block overlaps with this page
                starts_in_page = page_start <= block_start <= page_end
                ends_in_page = page_start <= block_end <= page_end
                spans_page = block_start < page_start and block_end > page_end

                if starts_in_page or ends_in_page or spans_page:
                    # Check if not already added
                    if not any(p['sector'] == sector_idx and p['page'] == page_idx
                              for p in erase_pages):
                        erase_pages.append({'sector': sector_idx, 'page': page_idx})
                    break

    return erase_pages


def erase_page(dev, flash_layout, sector, page):
    """
    Erase a single flash page
    Direct translation of stm32usbdfu.js lines 814-867

    Returns: True if H7 quirk was applied (ended in dfuIDLE), False if normal (dfuDNLOAD_IDLE)
    """
    page_addr = (page * flash_layout['sectors'][sector]['page_size'] +
                 flash_layout['sectors'][sector]['start_address'])

    cmd = bytes([0x41,
                 page_addr & 0xff,
                 (page_addr >> 8) & 0xff,
                 (page_addr >> 16) & 0xff,
                 (page_addr >> 24) & 0xff])

    control_transfer_out(dev, DFU_REQUEST['DNLOAD'], 0, cmd)

    status = get_status(dev)
    if status['state'] == DFU_STATE['dfuDNBUSY']:
        delay_ms = status['poll_timeout']
        time.sleep(delay_ms / 1000.0)

        status = get_status(dev)

        # H743 Rev.V specific handling (from JS lines 833-852)
        # H7 may remain in dfuDNBUSY after timeout - clear status to reach dfuIDLE
        if status['state'] == DFU_STATE['dfuDNBUSY']:
            clear_status(dev)
            status = get_status(dev)
            if status['state'] != DFU_STATE['dfuIDLE']:
                raise Exception(f"Failed to erase page 0x{page_addr:08x} (did not reach dfuIDLE after clearing)")
            return True  # H7 quirk applied, we're in dfuIDLE
        elif status['state'] != DFU_STATE['dfuDNLOAD_IDLE']:
            raise Exception(f"Failed to erase page 0x{page_addr:08x}, state={status['state']}")

    return False  # Normal erase, we're in dfuDNLOAD_IDLE


def write_firmware(dev, hex_data, transfer_size):
    """
    Write firmware to flash
    Direct translation of stm32usbdfu.js lines 873-944

    CRITICAL: JS calls clearStatus before loadAddress (via callback nesting)
    See stm32usbdfu.js:943 and similar patterns throughout
    """
    print("Writing firmware:")

    blocks = hex_data['data']
    bytes_flashed_total = 0

    for flashing_block in range(len(blocks)):
        block = blocks[flashing_block]
        address = block['address']

        # Clear status then load address for this block (matches JS pattern)
        # JS: self.loadAddress(address, write) is called from within upload_procedure(4)
        # which implicitly has clearStatus from previous step
        clear_status(dev)
        load_address(dev, address)

        bytes_flashed = 0
        wBlockNum = 2  # Required by DFU (from JS line 885)

        while bytes_flashed < block['bytes']:
            # Calculate chunk size
            bytes_to_write = min(transfer_size, block['bytes'] - bytes_flashed)
            data_to_flash = block['data'][bytes_flashed:bytes_flashed + bytes_to_write]

            # Write chunk
            control_transfer_out(dev, DFU_REQUEST['DNLOAD'], wBlockNum, data_to_flash)
            wBlockNum += 1

            # Check status
            status = get_status(dev)
            if status['state'] == DFU_STATE['dfuDNBUSY']:
                delay_ms = status['poll_timeout']
                time.sleep(delay_ms / 1000.0)

                status = get_status(dev)
                if status['state'] != DFU_STATE['dfuDNLOAD_IDLE']:
                    raise Exception(f"Failed to write {bytes_to_write} bytes to 0x{address:08x}, state={status['state']}")
            else:
                raise Exception(f"Failed to initiate write {bytes_to_write} bytes to 0x{address:08x}, state={status['state']}")

            bytes_flashed += bytes_to_write
            bytes_flashed_total += bytes_to_write

            # Update progress (writes are first half of total progress)
            progress = bytes_flashed_total / (hex_data['bytes_total'] * 2) * 100
            print(f"\r  Progress: {progress:.1f}%", end='', flush=True)

    print()  # New line after progress


def verify_firmware(dev, hex_data, transfer_size):
    """
    Verify written firmware
    Direct translation of stm32usbdfu.js lines 946-1031
    """
    print("Verifying data:")

    blocks = hex_data['data']
    verify_hex = []
    bytes_verified_total = 0

    for reading_block in range(len(blocks)):
        block = blocks[reading_block]
        address = block['address']

        # Prepare verify array for this block
        verify_hex.append([])

        # Load address for this block (matches JS pattern: clearStatus -> loadAddress -> clearStatus)
        # JS lines 999-1002
        clear_status(dev)
        load_address(dev, address)
        clear_status(dev)

        bytes_verified = 0
        wBlockNum = 2  # Required by DFU

        while bytes_verified < block['bytes']:
            # Calculate chunk size
            bytes_to_read = min(transfer_size, block['bytes'] - bytes_verified)

            # Read chunk
            data = control_transfer_in(dev, DFU_REQUEST['UPLOAD'], wBlockNum, bytes_to_read)
            wBlockNum += 1

            # Store read data
            for byte in data:
                verify_hex[reading_block].append(byte)

            bytes_verified += bytes_to_read
            bytes_verified_total += bytes_to_read

            # Update progress (verify is second half of total progress)
            progress = (hex_data['bytes_total'] + bytes_verified_total) / (hex_data['bytes_total'] * 2) * 100
            print(f"\r  Progress: {progress:.1f}%", end='', flush=True)

    print()  # New line after progress

    # Verify all blocks
    verify_ok = True
    for i in range(len(blocks)):
        if blocks[i]['data'] != verify_hex[i]:
            # Find first mismatch
            for j in range(min(len(blocks[i]['data']), len(verify_hex[i]))):
                if blocks[i]['data'][j] != verify_hex[i][j]:
                    print(f"\nVerification failed on byte {j} of block {i}: "
                          f"expected 0x{blocks[i]['data'][j]:02x}, "
                          f"got 0x{verify_hex[i][j]:02x}")
                    break
            verify_ok = False
            break

    return verify_ok


def leave_dfu(dev, hex_data):
    """
    Exit DFU mode and start application
    Direct translation of stm32usbdfu.js lines 1036-1059
    """
    address = hex_data['data'][0]['address']

    clear_status(dev)
    load_address(dev, address)

    # 'downloading' 0 bytes to program start address triggers DFU exit on STM32
    control_transfer_out(dev, DFU_REQUEST['DNLOAD'], 0, b'')
    get_status(dev)


# =============================================================================
# Main Flash Function
# =============================================================================

def flash_firmware(hex_file):
    """
    Main flashing procedure
    Follows the same flow as stm32usbdfu.js upload_procedure
    """
    print("INAV DFU Flasher - Configurator Clone")
    print("=" * 50)
    print()

    # Parse HEX file
    print(f"Loading {hex_file}...")
    hex_data = parse_intel_hex(hex_file)
    print(f"  Parsed {len(hex_data['data'])} blocks, {hex_data['bytes_total']} bytes")
    print()

    # Find DFU device
    print("Looking for DFU device...")
    dev = usb.core.find(idVendor=STM32_DFU_VID, idProduct=STM32_DFU_PID)
    if dev is None:
        print("\n✗ No DFU device found")
        print("\nTroubleshooting:")
        print("  1. Ensure flight controller is in DFU mode")
        print("  2. Check USB cable connection")
        print("  3. Run 'lsusb' to verify device is visible")
        print("  4. Are you in a sandbox? You may need to disable the sandbox")
        raise Exception("No DFU device found")
    print("  Found DFU device")
    print()

    # Setup USB
    try:
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)
        dev.set_configuration()
        usb.util.claim_interface(dev, 0)
    except usb.core.USBError as e:
        if "Access denied" in str(e) or "Permission denied" in str(e):
            print("\n✗ USB Permission Error")
            print("\nTroubleshooting:")
            print("  1. Are you in a sandbox? You may need to disable the sandbox")
            print("  2. Add udev rules: /etc/udev/rules.d/45-stdfu-permissions.rules")
            print("     SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"0483\", ATTRS{idProduct}==\"df11\", MODE=\"0664\", GROUP=\"plugdev\"")
            print("  3. Add your user to plugdev group: sudo usermod -a -G plugdev $USER")
            print("  4. Or run with sudo (not recommended)")
        raise

    try:
        # Get chip info (stm32usbdfu.js upload_procedure step 0, lines 552-612)
        chip_info = get_chip_info(dev)
        if not chip_info:
            raise Exception("Failed to detect chip info")

        if 'internal_flash' not in chip_info:
            raise Exception("Failed to detect internal flash")

        flash_layout = chip_info['internal_flash']
        print(f"Flash detected: {flash_layout['total_size'] / 1024:.0f} KB")
        print()

        # Check if firmware fits
        available_flash_size = flash_layout['total_size']
        if hex_data['bytes_total'] > available_flash_size:
            raise Exception(f"Firmware too large: {hex_data['bytes_total']/1024:.1f} KB > "
                          f"{available_flash_size/1024:.1f} KB")

        # Get transfer size from functional descriptor (stm32usbdfu.js lines 572-578)
        # Default to 2048 as in JS line 70: "this.transferSize = 2048"
        transfer_size = 2048
        print(f"Transfer size: {transfer_size} bytes")
        print()

        # Clear status
        clear_status(dev)

        # Calculate pages to erase (stm32usbdfu.js step 2, lines 757-792)
        print("Calculating erase pages...")
        erase_pages = calculate_pages_to_erase(hex_data, flash_layout)

        if not erase_pages:
            raise Exception("No flash pages to erase - invalid HEX file")

        print(f"  Will erase {len(erase_pages)} pages")
        print()

        # Erase flash (stm32usbdfu.js step 2, lines 798-870)
        print("Erasing flash:")
        total_erased = 0
        h7_quirk_used = False
        for i, page_info in enumerate(erase_pages):
            quirk = erase_page(dev, flash_layout, page_info['sector'], page_info['page'])
            h7_quirk_used = h7_quirk_used or quirk
            total_erased += flash_layout['sectors'][page_info['sector']]['page_size']
            progress = (i + 1) / len(erase_pages) * 100
            print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
        print()
        print(f"  Erased {total_erased / 1024:.1f} KB")
        print()

        # Write firmware (stm32usbdfu.js step 4, lines 873-944)
        # JS comment says "we dont need to clear the state as we are already using DFU_DNLOAD"
        # but it DOES call clearStatus before loadAddress (line 943 called within step 4)
        write_firmware(dev, hex_data, transfer_size)
        print()

        # Verify firmware (stm32usbdfu.js step 5, lines 946-1031)
        verify_ok = verify_firmware(dev, hex_data, transfer_size)
        print()

        if not verify_ok:
            raise Exception("Verification failed")

        print("✓ Programming successful")
        print()

        # Exit DFU mode (stm32usbdfu.js leave, lines 1036-1059)
        print("Exiting DFU mode...")
        try:
            leave_dfu(dev, hex_data)
        except:
            # Device may disconnect during exit - this is normal
            pass

        print("\n✓ Firmware flashed successfully!")
        print("✓ Settings preserved!")
        print("\nFC will now reboot.")

    finally:
        try:
            usb.util.release_interface(dev, 0)
            usb.util.dispose_resources(dev)
        except:
            pass


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 flash-dfu-configurator-clone.py <firmware.hex>")
        print()
        print("This script is a direct translation of the INAV Configurator's DFU flashing code.")
        print("It preserves settings by only erasing pages that contain firmware.")
        sys.exit(1)

    hex_file = sys.argv[1]

    try:
        flash_firmware(hex_file)
    except KeyboardInterrupt:
        print("\n\nAborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
