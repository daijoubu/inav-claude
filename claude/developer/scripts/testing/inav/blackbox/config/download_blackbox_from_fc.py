#!/usr/bin/env python3
"""
Download blackbox log from FC SPIFLASH via MSP.

Usage:
    ./download_blackbox_from_fc.py [port] [output_file]

Example:
    ./download_blackbox_from_fc.py /dev/ttyACM0 blackbox.TXT
"""

import struct
import sys
import time
from mspapi2 import MSPApi

def download_blackbox(port='/dev/ttyACM0', output_file=None):
    """Download blackbox log from FC."""

    print(f"Connecting to FC on {port}...")
    api = MSPApi(port=port, baudrate=115200)
    api.open()
    time.sleep(0.5)

    # MSP commands
    MSP_DATAFLASH_SUMMARY = 70
    MSP_DATAFLASH_READ = 71

    # Get flash summary
    print("\nQuerying blackbox flash summary...")
    try:
        response = api._serial.request(MSP_DATAFLASH_SUMMARY)
        if isinstance(response, tuple):
            summary = response[1]
        else:
            summary = response
    except Exception as e:
        print(f"Error querying flash: {e}")
        api.close()
        return False

    if len(summary) < 13:
        print(f"Unexpected summary length: {len(summary)} bytes")
        api.close()
        return False

    flags, sectors, totalSize, usedSize = struct.unpack('<BIII', summary[:13])
    print(f"  Ready: {bool(flags & 1)}")
    print(f"  Sectors: {sectors}")
    print(f"  Total size: {totalSize} bytes ({totalSize/1024/1024:.1f} MB)")
    print(f"  Used size: {usedSize} bytes ({usedSize/1024:.1f} KB)")

    if usedSize == 0:
        print("\n✗ No blackbox data found!")
        api.close()
        return False

    # Download with small chunks for reliability
    print(f"\nDownloading {usedSize} bytes...")
    print("This will take about 2-3 minutes...")

    log_data = bytearray()
    address = 0
    chunk_size = 128  # Small chunks to avoid timeouts
    errors = 0
    max_errors = 10

    last_progress = 0
    start_time = time.time()

    while address < usedSize and errors < max_errors:
        to_read = min(chunk_size, usedSize - address)
        request = struct.pack('<IH', address, to_read)

        try:
            response = api._serial.request(MSP_DATAFLASH_READ, request)
            if isinstance(response, tuple):
                chunk = response[1]
            else:
                chunk = response

            # Response: [address:4][data:...]
            if len(chunk) >= 4:
                chunk_data = chunk[4:]
                log_data.extend(chunk_data)
                address += len(chunk_data)
                errors = 0  # Reset error count on success

                # Progress every 5%
                progress = (100 * address) // usedSize
                if progress >= last_progress + 5:
                    elapsed = time.time() - start_time
                    rate = address / elapsed if elapsed > 0 else 0
                    eta = (usedSize - address) / rate if rate > 0 else 0
                    print(f"  {address}/{usedSize} bytes ({progress}%) - {rate:.0f} B/s - ETA: {eta:.0f}s")
                    last_progress = progress
            else:
                print(f"Short read at {address}, retrying...")
                errors += 1
                time.sleep(0.1)
                continue

        except Exception as e:
            errors += 1
            print(f"Error at {address}: {e} (attempt {errors}/{max_errors})")
            time.sleep(0.1)
            continue

        time.sleep(0.005)  # Small delay between requests

    api.close()

    if errors >= max_errors:
        print(f"\n✗ Too many errors, download incomplete!")
        return False

    if len(log_data) > 0:
        if output_file is None:
            output_file = f"blackbox_fc_{int(time.time())}.TXT"

        with open(output_file, 'wb') as f:
            f.write(log_data)

        elapsed = time.time() - start_time
        print(f"\n✓ Downloaded {len(log_data)} bytes in {elapsed:.1f}s to {output_file}")
        print(f"\nDecode with: blackbox_decode {output_file}")
        return True
    else:
        print("\n✗ No data downloaded!")
        return False

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'
    output = sys.argv[2] if len(sys.argv) > 2 else None

    success = download_blackbox(port, output)
    sys.exit(0 if success else 1)
