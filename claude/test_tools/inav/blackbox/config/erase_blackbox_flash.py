#!/usr/bin/env python3
"""
Erase blackbox flash ONLY (preserves FC settings and calibration).

Uses MSP_DATAFLASH_ERASE (code 72) which erases only the blackbox flash chip,
not the configuration flash.

Usage:
    ./erase_blackbox_flash.py [port]

Example:
    ./erase_blackbox_flash.py /dev/ttyACM0
"""

import sys
import time
from mspapi2 import MSPApi

def erase_blackbox_flash(port='/dev/ttyACM0'):
    """Erase blackbox flash only using MSP command."""

    print(f"Connecting to FC on {port}...")
    api = MSPApi(port=port, baudrate=115200)
    api.open()
    time.sleep(0.5)

    MSP_DATAFLASH_ERASE = 72
    MSP_DATAFLASH_SUMMARY = 70

    print("\nErasing blackbox flash...")
    print("⚠️  This erases ONLY blackbox data, NOT FC settings")

    try:
        # Send erase command
        api._serial.request(MSP_DATAFLASH_ERASE)
        print("✓ Blackbox flash erase command sent")

        # Poll for completion using MSP_DATAFLASH_SUMMARY
        print("Polling for erase completion...")
        start_time = time.time()
        max_wait = 60  # Maximum 60 seconds timeout
        poll_interval = 1  # Poll every 1 second

        while True:
            elapsed = time.time() - start_time

            if elapsed > max_wait:
                print(f"✗ Timeout after {max_wait} seconds waiting for flash erase to complete")
                api.close()
                return False

            # Query flash status
            try:
                code, response = api._serial.request(MSP_DATAFLASH_SUMMARY)

                if response and len(response) >= 13:
                    # Parse MSP_DATAFLASH_SUMMARY response:
                    # byte 0: flashReady (1 = ready, 0 = busy)
                    # bytes 1-4: sectorCount (uint32_t)
                    # bytes 5-8: totalSize (uint32_t)
                    # bytes 9-12: usedSize (uint32_t)
                    flash_ready = response[0]

                    if flash_ready == 1:
                        print(f"✓ Flash ready after {elapsed:.1f} seconds")
                        break
                    else:
                        print(f"  Still erasing... ({elapsed:.0f}s elapsed)", end='\r')
                        time.sleep(poll_interval)
                else:
                    print(f"✗ Invalid response from MSP_DATAFLASH_SUMMARY")
                    api.close()
                    return False

            except Exception as poll_error:
                print(f"✗ Error polling flash status: {poll_error}")
                api.close()
                return False

        print("\n✓ Blackbox flash erased successfully")
        print("✓ FC settings and calibration preserved")

    except Exception as e:
        print(f"✗ Error erasing flash: {e}")
        api.close()
        return False

    api.close()
    return True

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'

    success = erase_blackbox_flash(port)
    sys.exit(0 if success else 1)
