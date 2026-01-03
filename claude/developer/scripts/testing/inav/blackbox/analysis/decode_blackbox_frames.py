#!/usr/bin/env python3
"""
Decode blackbox I-frames and P-frames manually to understand encoding.
"""

import struct

def decode_unsigned_vb(data, offset):
    """Decode variable-byte unsigned integer."""
    value = 0
    shift = 0
    while offset < len(data):
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        shift += 7
        if (byte & 0x80) == 0:
            break
    return value, offset

def decode_signed_vb(data, offset):
    """Decode variable-byte signed integer using zigzag encoding."""
    unsigned_value, offset = decode_unsigned_vb(data, offset)
    # Zigzag decode: (n >> 1) ^ -(n & 1)
    signed_value = (unsigned_value >> 1) ^ (-(unsigned_value & 1))
    return signed_value, offset

def analyze_log(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    # Find end of headers
    header_end = data.rfind(b'\nH ')
    print(f"Headers end at offset: 0x{header_end:x} ({header_end})")

    # Find first I-frame after headers
    i_offset = data.find(b'I', header_end)
    print(f"First I-frame found at offset: 0x{i_offset:x} ({i_offset})")

    # Show surrounding bytes for context
    print(f"Bytes before I-frame: {data[i_offset-10:i_offset].hex()}")
    print(f"Bytes at I-frame: {data[i_offset:i_offset+20].hex()}")

    # Decode first I-frame
    print("\n=== First I-frame ===")
    offset = i_offset + 1  # Skip 'I' marker

    loopIteration, offset = decode_unsigned_vb(data, offset)
    print(f"loopIteration: {loopIteration}")

    time_i1, offset = decode_unsigned_vb(data, offset)
    print(f"time: {time_i1} µs")

    # Find next I-frame
    i2_offset = data.find(b'I', offset)
    print(f"\nSecond I-frame found at offset: 0x{i2_offset:x} ({i2_offset})")

    offset = i2_offset + 1
    loopIteration2, offset = decode_unsigned_vb(data, offset)
    print(f"loopIteration: {loopIteration2}")

    time_i2, offset = decode_unsigned_vb(data, offset)
    print(f"time: {time_i2} µs")
    print(f"time delta from I1: {time_i2 - time_i1} µs")

    # Find third I-frame
    i3_offset = data.find(b'I', offset)
    if i3_offset > 0:
        print(f"\nThird I-frame found at offset: 0x{i3_offset:x} ({i3_offset})")

        offset = i3_offset + 1
        loopIteration3, offset = decode_unsigned_vb(data, offset)
        print(f"loopIteration: {loopIteration3}")

        time_i3, offset = decode_unsigned_vb(data, offset)
        print(f"time: {time_i3} µs")
        print(f"time delta from I2: {time_i3 - time_i2} µs")

    # Find first P-frame after first I-frame
    p_offset = data.find(b'P', i_offset)
    if p_offset > 0:
        print(f"\n=== First P-frame ===")
        print(f"P-frame found at offset: 0x{p_offset:x} ({p_offset})")

        offset = p_offset + 1  # Skip 'P' marker

        # Decode time delta (SIGNED_VB)
        time_delta, offset = decode_signed_vb(data, offset)
        print(f"time delta (second-order): {time_delta}")

        # Try to reconstruct time value
        # For first P after I, history[1] == history[2] == I-frame
        # Predicted: 2*time_i1 - time_i1 = time_i1
        # Actual = predicted + delta
        predicted_time = time_i1
        reconstructed_time = predicted_time + time_delta
        print(f"Predicted time: {predicted_time} µs")
        print(f"Reconstructed time: {reconstructed_time} µs")

        # Find second P-frame
        p2_offset = data.find(b'P', offset)
        if p2_offset > 0:
            print(f"\n=== Second P-frame ===")
            print(f"P-frame found at offset: 0x{p2_offset:x} ({p2_offset})")

            offset = p2_offset + 1
            time_delta2, offset = decode_signed_vb(data, offset)
            print(f"time delta (second-order): {time_delta2}")

            # For second P after I:
            # history[1] = first P-frame, history[2] = I-frame
            # Predicted: 2*reconstructed_time - time_i1
            predicted_time2 = 2 * reconstructed_time - time_i1
            reconstructed_time2 = predicted_time2 + time_delta2
            print(f"Predicted time: {predicted_time2} µs")
            print(f"Reconstructed time: {reconstructed_time2} µs")

if __name__ == '__main__':
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else 'test_results/blackbox_2_fields_only.TXT'
    analyze_log(filename)
