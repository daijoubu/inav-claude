#!/usr/bin/env python3
"""
Test DFU Flash Layout Detection - Debug Version

Shows detailed USB descriptor information
"""

import usb.core
import usb.util

STM32_DFU_VID = 0x0483
STM32_DFU_PID = 0xdf11

def test_detection():
    print("DFU Device Debug Test")
    print("=" * 40)
    print()

    # Find DFU device
    print("Looking for STM32 DFU device...")
    dev = usb.core.find(idVendor=STM32_DFU_VID, idProduct=STM32_DFU_PID)

    if dev is None:
        print("✗ No STM32 DFU device found")
        return False

    print(f"✓ Found DFU device")
    print(f"  Vendor ID: 0x{dev.idVendor:04X}")
    print(f"  Product ID: 0x{dev.idProduct:04X}")
    print()

    # Claim interface
    if dev.is_kernel_driver_active(0):
        print("Detaching kernel driver...")
        dev.detach_kernel_driver(0)

    print("Setting configuration...")
    dev.set_configuration()

    print("Claiming interface 0...")
    usb.util.claim_interface(dev, 0)

    try:
        # Get configuration
        print("\nGetting device configuration...")
        cfg = dev.get_active_configuration()
        print(f"Configuration value: {cfg.bConfigurationValue}")
        print(f"Number of interfaces: {len(cfg.interfaces())}")
        print()

        # Iterate through interfaces
        print("Interface details:")
        for intf_idx, intf in enumerate(cfg.interfaces()):
            print(f"\n  Interface {intf_idx}:")
            print(f"    bInterfaceNumber: {intf.bInterfaceNumber}")
            print(f"    Number of alternates: {len(list(intf))}")

            for alt_idx, alt in enumerate(intf):
                print(f"\n    Alternate {alt_idx}:")
                print(f"      bAlternateSetting: {alt.bAlternateSetting}")
                print(f"      bInterfaceClass: {alt.bInterfaceClass}")
                print(f"      bInterfaceSubClass: {alt.bInterfaceSubClass}")
                print(f"      bInterfaceProtocol: {alt.bInterfaceProtocol}")
                print(f"      iInterface: {alt.iInterface}")

                # Try to get string descriptor
                if alt.iInterface > 0:
                    try:
                        # Get string descriptor
                        result = dev.ctrl_transfer(0x80, 6, 0x0300 | alt.iInterface, 0, 255, 5000)
                        if len(result) >= 2:
                            length = result[0]
                            desc_str = ""
                            for i in range(2, min(length, len(result)), 2):
                                if i + 1 < len(result):
                                    char_code = result[i] | (result[i + 1] << 8)
                                    desc_str += chr(char_code)
                            print(f"      String descriptor: {desc_str}")

                            # Check if it's internal flash
                            if 'internal flash' in desc_str.lower():
                                print(f"      ★ This is the internal flash descriptor!")
                    except Exception as e:
                        print(f"      Failed to get string descriptor: {e}")

        return True

    finally:
        print("\n\nCleaning up...")
        usb.util.release_interface(dev, 0)
        usb.util.dispose_resources(dev)

if __name__ == '__main__':
    try:
        test_detection()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
