#!/usr/bin/env python3
"""
Test MSP2_INAV_DRONECAN_NODES (0x2042) and MSP2_INAV_DRONECAN_NODE_INFO (0x2043).

Usage:
    python3 test_dronecan_nodes.py [--port /dev/ttyACM0]
"""

import argparse
import struct
import sys

from mspapi2.msp_api import MSPApi
from mspapi2.msp_serial import MSPUnsupportedError

MSP2_INAV_DRONECAN_NODES     = 0x2042
MSP2_INAV_DRONECAN_NODE_INFO = 0x2043

HEALTH_NAMES = {0: "OK", 1: "WARNING", 2: "ERROR", 3: "CRITICAL"}
MODE_NAMES   = {0: "OPERATIONAL", 1: "INITIALIZATION", 2: "MAINTENANCE",
                3: "SOFTWARE_UPDATE", 7: "OFFLINE"}

# NODES list: nodeID(1) + health(1) + mode(1) + last_seen_ms(4) = 7 bytes
NODE_RECORD_FMT  = "<BBBI"
NODE_RECORD_SIZE = struct.calcsize(NODE_RECORD_FMT)  # 7

# NODE_INFO detail: nodeID(1)+health(1)+mode(1)+uptime_sec(4)+vendor_status(2)+last_seen_ms(4)+name_len(1)+name[32]
NODE_INFO_FMT    = "<BBBIHIB32s"
NODE_INFO_SIZE   = struct.calcsize(NODE_INFO_FMT)


def parse_node_record(data: bytes, offset: int) -> dict:
    node_id, health, mode, last_seen_ms = struct.unpack_from(NODE_RECORD_FMT, data, offset)
    return {
        "nodeID":       node_id,
        "health":       health,
        "health_str":   HEALTH_NAMES.get(health, f"UNKNOWN({health})"),
        "mode":         mode,
        "mode_str":     MODE_NAMES.get(mode, f"UNKNOWN({mode})"),
        "last_seen_ms": last_seen_ms,
    }


def parse_node_info(data: bytes) -> dict:
    fields = struct.unpack_from(NODE_INFO_FMT, data, 0)
    node_id, health, mode, uptime_sec, vendor_status, last_seen_ms, name_len, name_raw = fields
    name = name_raw[:name_len].decode("ascii", errors="replace") if name_len else ""
    return {
        "nodeID":        node_id,
        "health":        health,
        "health_str":    HEALTH_NAMES.get(health, f"UNKNOWN({health})"),
        "mode":          mode,
        "mode_str":      MODE_NAMES.get(mode, f"UNKNOWN({mode})"),
        "uptime_sec":    uptime_sec,
        "vendor_status": vendor_status,
        "last_seen_ms":  last_seen_ms,
        "name":          name,
    }


def print_node_summary(node: dict) -> None:
    print(f"  Node ID:    {node['nodeID']}")
    print(f"  Health:     {node['health_str']} ({node['health']})")
    print(f"  Mode:       {node['mode_str']} ({node['mode']})")
    print(f"  Last seen:  {node['last_seen_ms']}ms")


def print_node_info(node: dict) -> None:
    print(f"  Node ID:       {node['nodeID']}")
    print(f"  Health:        {node['health_str']} ({node['health']})")
    print(f"  Mode:          {node['mode_str']} ({node['mode']})")
    print(f"  Uptime:        {node['uptime_sec']}s")
    print(f"  Vendor status: 0x{node['vendor_status']:04X}")
    print(f"  Last seen:     {node['last_seen_ms']}ms")
    print(f"  Name:          '{node['name']}'" if node['name'] else "  Name:          (unknown)")


def test_dronecan_nodes(api: MSPApi) -> list:
    print("\n--- MSP2_INAV_DRONECAN_NODES (0x2042) ---")
    print(f"    Expected record size: {NODE_RECORD_SIZE} bytes (nodeID+health+mode+last_seen_ms)")

    _, raw = api._serial.request(MSP2_INAV_DRONECAN_NODES, b"", timeout=2.0)

    if not raw:
        print("FAIL: empty response")
        return []

    node_count = raw[0]
    print(f"Node count: {node_count}")

    if node_count == 0:
        print("No DroneCAN nodes detected (bus may be empty).")
        return []

    expected_len = 1 + node_count * NODE_RECORD_SIZE
    if len(raw) != expected_len:
        print(f"FAIL: response length {len(raw)} bytes, expected {expected_len} "
              f"(1 + {node_count} * {NODE_RECORD_SIZE})")
        return []

    nodes = []
    for i in range(node_count):
        offset = 1 + i * NODE_RECORD_SIZE
        node = parse_node_record(raw, offset)
        print(f"\nNode {i + 1}:")
        print_node_summary(node)
        nodes.append(node)

    print(f"\nPASS: {node_count} node(s), payload {len(raw)} bytes")
    return nodes


def test_dronecan_node_info(api: MSPApi, nodes: list) -> None:
    print("\n--- MSP2_INAV_DRONECAN_NODE_INFO (0x2043) ---")

    all_passed = True

    for node in nodes:
        node_id = node["nodeID"]
        print(f"\nQuerying node ID {node_id}...")

        payload = struct.pack("<B", node_id)
        _, raw = api._serial.request(MSP2_INAV_DRONECAN_NODE_INFO, payload, timeout=2.0)

        if not raw:
            print(f"  FAIL: empty response for node {node_id}")
            all_passed = False
            continue

        if len(raw) < NODE_INFO_SIZE:
            print(f"  FAIL: response too short ({len(raw)} bytes, expected {NODE_INFO_SIZE})")
            all_passed = False
            continue

        info = parse_node_info(raw)
        if info["nodeID"] != node_id:
            print(f"  FAIL: response node ID {info['nodeID']} != requested {node_id}")
            all_passed = False
            continue

        print("  PASS")
        print_node_info(info)

    # Error case: node ID that shouldn't exist
    print("\nQuerying non-existent node ID 127...")
    payload = struct.pack("<B", 127)
    try:
        _, raw = api._serial.request(MSP2_INAV_DRONECAN_NODE_INFO, payload, timeout=2.0)
        print(f"  FAIL: got {len(raw)} bytes for non-existent node — expected MSP_RESULT_ERROR")
        all_passed = False
    except MSPUnsupportedError:
        print("  PASS: MSP_RESULT_ERROR received (node not found)")

    if all_passed:
        print("\nAll NODE_INFO tests PASSED")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test DroneCAN MSP messages")
    parser.add_argument("--port", default="/dev/ttyACM0")
    parser.add_argument("--baudrate", type=int, default=115200)
    args = parser.parse_args()

    with MSPApi(port=args.port, baudrate=args.baudrate) as api:
        nodes = test_dronecan_nodes(api)
        test_dronecan_node_info(api, nodes)

    print("\nDone.")


if __name__ == "__main__":
    main()
