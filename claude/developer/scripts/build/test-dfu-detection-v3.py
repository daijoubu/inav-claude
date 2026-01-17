#!/usr/bin/env python3
"""
Test DFU Flash Layout Detection - Fixed Version

Properly accesses USB interface alternates
"""

import usb.core
import usb.util

STM32_DFU_VID = 0x0483
STM32_DFU_PID = 0xdf11

def test_detection():
    print("DFU Device Flash Layout Detection")
    print("=" * 40)
    print()

    # Find DFU device
    print("Looking for STM32 DFU device...")
    dev = usb.core.find(idVendor=STM32_DFU_VID, idProduct=STM32_DFU_PID)

    if dev is None:
        print("✗ No STM32 DFU device found")
        return False

    print(f"✓ Found DFU device\n")

    # Claim interface
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)

    dev.set_configuration()
    usb.util.claim_interface(dev, 0)

    try:
        # Get configuration
        cfg = dev.get_active_configuration()
        print(f"Configuration: {cfg.bConfigurationValue}")
        print(f"Interfaces: {cfg.bNumInterfaces}\n")

        # Access interface 0 settings (alternates)
        intf = cfg[(0, 0)]  # Interface 0, first setting
        print(f"Interface 0 has {intf.bNumEndpoints} endpoints")
        print(f"Alternate settings available: checking...\n")

        # Try to access all alternate settings for interface 0
        flash_descriptor = None
        for alt_setting in range(4):  # DFU devices typically have 4 alternates
            try:
                # Access alternate setting
                alt_intf = cfg[(0, alt_setting)]
                print(f"Alternate {alt_setting}:")
                print(f"  iInterface: {alt_intf.iInterface}")

                # Get string descriptor if available
                if alt_intf.iInterface > 0:
                    try:
                        result = dev.ctrl_transfer(0x80, 6, 0x0300 | alt_intf.iInterface, 0, 255, 5000)
                        if len(result) >= 2:
                            length = result[0]
                            desc_str = ""
                            for i in range(2, min(length, len(result)), 2):
                                if i + 1 < len(result):
                                    char_code = result[i] | (result[i + 1] << 8)
                                    desc_str += chr(char_code)

                            print(f"  Descriptor: {desc_str}")

                            # Check if it's internal flash
                            if 'internal flash' in desc_str.lower():
                                print(f"  ★ Found Internal Flash descriptor!\n")
                                flash_descriptor = desc_str

                    except Exception as e:
                        print(f"  (No string descriptor: {e})")
            except:
                break  # No more alternates

        if flash_descriptor:
            print("\n" + "=" * 60)
            print("✓ SUCCESS: Flash Layout Detected")
            print("=" * 60)
            print(f"\nDescriptor string: {flash_descriptor}")

            # Parse the descriptor
            parts = flash_descriptor.split('/')
            if len(parts) >= 3:
                flash_type = parts[0].strip()
                start_addr = parts[1].strip()
                layout = parts[2].strip()

                print(f"\nFlash Type: {flash_type}")
                print(f"Start Address: {start_addr}")
                print(f"Layout: {layout}")

                # Parse layout: "04*016Kg,01*64Kg,03*128Kg"
                print("\nSector breakdown:")
                sectors = layout.split(',')
                total_kb = 0
                for sector in sectors:
                    if '*' in sector:
                        count, size = sector.split('*')
                        size_kb = int(''.join(c for c in size if c.isdigit()))
                        print(f"  {count} sectors × {size_kb}KB = {int(count) * size_kb}KB")
                        total_kb += int(count) * size_kb

                print(f"\nTotal flash: {total_kb}KB")

                # Infer MCU family
                if "04*016Kg,01*64Kg,03*128Kg" in layout or "04*016Kg,01*064Kg,03*128Kg" in layout:
                    print("\n✓ Detected: STM32F7 family (F722/F745)")
                elif "04*016Kg,01*64Kg,07*128Kg" in layout or "04*016Kg,01*064Kg,07*128Kg" in layout:
                    print("\n✓ Detected: STM32F4 family (F405/F407)")
                elif "16*128Kg" in layout:
                    print("\n✓ Detected: STM32H7 family (H743/H750)")
                elif "512*002Kg" in layout:
                    print("\n✓ Detected: AT32F435 family")

                return True

        print("\n✗ No internal flash descriptor found")
        return False

    finally:
        usb.util.release_interface(dev, 0)
        usb.util.dispose_resources(dev)

if __name__ == '__main__':
    try:
        test_detection()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
