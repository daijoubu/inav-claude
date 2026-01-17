#!/usr/bin/env python3
"""
Test DFU Flash Layout Detection

This script tests the automatic flash layout detection without actually flashing.
Just connects to DFU device, reads descriptors, and shows what it detects.
"""

import usb.core
import usb.util
import sys

# STM32 DFU Device IDs
STM32_DFU_VID = 0x0483
STM32_DFU_PID = 0xdf11

def get_string_descriptor(dev, index):
    """Get USB string descriptor"""
    if index == 0:
        return ""
    try:
        result = dev.ctrl_transfer(0x80, 6, 0x0300 | index, 0, 255, 5000)
        if len(result) < 2:
            return ""
        length = result[0]
        descriptor = ""
        for i in range(2, min(length, len(result)), 2):
            if i + 1 < len(result):
                char_code = result[i] | (result[i + 1] << 8)
                descriptor += chr(char_code)
        return descriptor
    except Exception as e:
        print(f"  Warning: Failed to get string descriptor {index}: {e}")
        return ""

def get_interface_descriptors(dev):
    """Get interface descriptor strings"""
    descriptors = []
    try:
        config = dev.get_active_configuration()
        for interface in config:
            for alternate in interface:
                iface_string_idx = alternate.iInterface
                if iface_string_idx > 0:
                    descriptor_string = get_string_descriptor(dev, iface_string_idx)
                    if descriptor_string:
                        descriptors.append(descriptor_string)
    except Exception as e:
        print(f"  Warning: Failed to get interface descriptors: {e}")
    return descriptors

def parse_flash_descriptor(descriptor_str):
    """Parse DFU flash descriptor string"""
    try:
        descriptor_str = ''.join(c for c in descriptor_str if 32 <= ord(c) <= 126)
        if descriptor_str == "@External Flash /0x90000000/1001*128Kg,3*128Kg,20*128Ka":
            descriptor_str = "@External Flash /0x90000000/998*128Kg,1*128Kg,4*128Kg,21*128Ka"

        parts = descriptor_str.split('/')
        if len(parts) > 3:
            parts = parts[:3]
        if len(parts) < 3 or not parts[0].startswith('@'):
            return None

        memory_type = parts[0].strip().replace('@', '')
        start_address = int(parts[1], 16)

        sectors = []
        total_size = 0
        sector_parts = parts[2].split(',')

        for sector_str in sector_parts:
            if '*' not in sector_str:
                continue
            num_str, size_str = sector_str.split('*')
            num_pages = int(num_str)
            size_numeric = ''.join(c for c in size_str if c.isdigit())
            if not size_numeric:
                continue
            page_size = int(size_numeric)

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
        print(f"  Warning: Failed to parse descriptor '{descriptor_str}': {e}")
        return None

def detect_flash_layout(dev):
    """Detect flash layout from DFU device descriptors"""
    print("Detecting flash layout from device...")
    descriptors = get_interface_descriptors(dev)

    if not descriptors:
        print("  Warning: No interface descriptors found")
        return None

    print(f"  Found {len(descriptors)} interface descriptor(s)")

    for desc_str in descriptors:
        print(f"  Descriptor: {desc_str}")
        parsed = parse_flash_descriptor(desc_str)

        if parsed and 'internal_flash' in parsed['type'].lower():
            print(f"  ✓ Detected {parsed['type']}: {parsed['total_size'] / 1024:.0f}KB")
            print(f"    {len(parsed['sectors'])} sector(s)")
            for i, sector in enumerate(parsed['sectors']):
                print(f"    Sector {i}: {sector['num_pages']} x {sector['page_size'] / 1024:.0f}KB")
            return parsed

    print("  Warning: No internal flash descriptor found")
    return None

def infer_mcu_family_from_layout(flash_layout):
    """Infer MCU family from detected flash layout"""
    if not flash_layout or 'sectors' not in flash_layout:
        return None

    sectors = flash_layout['sectors']

    if len(sectors) == 1 and sectors[0]['page_size'] == 2048 and sectors[0]['num_pages'] == 512:
        return 'AT32F435'
    if len(sectors) == 1 and sectors[0]['page_size'] == 131072:
        return 'H7'
    if len(sectors) >= 3 and sectors[0]['page_size'] == 16384 and sectors[1]['page_size'] == 65536:
        if len(sectors) > 2 and sectors[2]['page_size'] == 131072 and sectors[2]['num_pages'] >= 7:
            return 'F4'
        elif len(sectors) > 2 and sectors[2]['page_size'] == 131072 and sectors[2]['num_pages'] == 3:
            return 'F7'
    return None

def test_detection():
    """Test flash layout detection from DFU device"""
    print("DFU Flash Layout Detection Test")
    print("=" * 40)
    print()

    # Find DFU device
    print("Looking for STM32 DFU device...")
    dev = usb.core.find(idVendor=STM32_DFU_VID, idProduct=STM32_DFU_PID)

    if dev is None:
        print("✗ No STM32 DFU device found")
        print()
        print("Put FC into DFU mode:")
        print("  .claude/skills/flash-firmware-dfu/reboot-to-dfu.py /dev/ttyACM0")
        return False

    print(f"✓ Found DFU device\n")

    # Claim interface
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)

    dev.set_configuration()
    usb.util.claim_interface(dev, 0)

    try:
        # Detect flash layout
        flash_layout = detect_flash_layout(dev)

        if flash_layout:
            print()
            print("=" * 40)
            print("✓ DETECTION SUCCESSFUL")
            print("=" * 40)

            # Infer MCU family
            mcu_family = infer_mcu_family_from_layout(flash_layout)
            if mcu_family:
                print(f"Inferred MCU family: {mcu_family}")

            print()
            print("Flash layout details:")
            print(f"  Start address: 0x{flash_layout['start_address']:08X}")
            print(f"  Total size: {flash_layout['total_size'] / 1024:.0f}KB")
            print(f"  Number of sectors: {len(flash_layout['sectors'])}")
            print()
            print("Sector breakdown:")
            for i, sector in enumerate(flash_layout['sectors']):
                print(f"  Sector {i}:")
                print(f"    Start: 0x{sector['start_address']:08X}")
                print(f"    Pages: {sector['num_pages']}")
                print(f"    Page size: {sector['page_size'] / 1024:.0f}KB")
                print(f"    Total: {sector['total_size'] / 1024:.0f}KB")

            return True
        else:
            print()
            print("✗ Detection failed")
            return False

    finally:
        usb.util.release_interface(dev, 0)
        usb.util.dispose_resources(dev)

if __name__ == '__main__':
    try:
        success = test_detection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
