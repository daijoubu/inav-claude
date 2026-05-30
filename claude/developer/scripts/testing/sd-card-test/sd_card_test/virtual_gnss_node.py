"""
Virtual DroneCAN GNSS node.

Publishes uavcan.equipment.gnss.Fix2 at 25Hz on CAN bus.
Simulates the MatekL431 GNSS module for HAL update testing.

Usage:
    python3 virtual_gnss_node.py [--node-id 74] [--can can0] [--hz 25]

Requires: dronecan, python-can, and a CAN interface (can0 via slcand).
"""
import argparse
import sys
import time

import can
from can import CanOperationError
# python-can 4.x SocketCAN doesn't implement flush_tx_buffer (raises NotImplementedError)
# but dronecan PythonCAN driver calls it. Monkey-patch to no-op.
try:
    from can.interfaces.socketcan import SocketcanBus
    SocketcanBus.flush_tx_buffer = lambda self: None
except ImportError:
    pass

import dronecan
from dronecan.transport import TransferError

Fix2 = dronecan.uavcan.equipment.gnss.Fix2

# ENOBUFS from socketcan - FC went offline / TX queue full
_ENOBUFS_RETRY_DELAY = 1.0
_MAX_CONSECUTIVE_FAILURES = 10


def make_fix2(
    lat_deg: float,
    lon_deg: float,
    alt_msl_m: float = 50.0,
    alt_ellipsoid_m: float = 80.0,
    sats: int = 12,
    pdop: float = 1.5,
    vel_north: float = 0.0,
    vel_east: float = 0.0,
    vel_down: float = 0.0,
    fix_3d: bool = True,
):
    """Create a uavcan.equipment.gnss.Fix2 message.

    INAV's gps_dronecan.c reads: longitude_deg_1e8/10, latitude_deg_1e8/10,
    height_msl_mm/10, ned_velocity*100, pdop*100, covariance[0,2,5] for eph/epv.
    """
    msg = Fix2()
    msg.timestamp.usec = int(time.time() * 1e6)
    msg.gnss_timestamp.usec = msg.timestamp.usec
    msg.gnss_time_standard = 3
    msg.num_leap_seconds = 27

    msg.longitude_deg_1e8 = int(lon_deg * 1e8)
    msg.latitude_deg_1e8 = int(lat_deg * 1e8)
    msg.height_ellipsoid_mm = int(alt_ellipsoid_m * 1000)
    msg.height_msl_mm = int(alt_msl_m * 1000)

    msg.ned_velocity.items = [vel_north, vel_east, vel_down]
    msg.sats_used = sats
    msg.status = 3 if fix_3d else 2
    msg.mode = 0
    msg.sub_mode = 0
    msg.pdop = pdop

    return msg


def make_node(can_iface: str, node_id: int, bitrate: int):
    """Create a DroneCAN node with the given config."""
    print(f"Initializing DroneCAN node {node_id} on {can_iface}...")
    node = dronecan.make_node(can_iface, node_id=node_id, bitrate=bitrate)
    print(f"  Spin started.")
    return node


def main():
    parser = argparse.ArgumentParser(description="Virtual DroneCAN GNSS node")
    parser.add_argument("--node-id", type=int, default=74, help="CAN node ID (default: 74)")
    parser.add_argument("--can", default="can0", help="CAN interface (default: can0)")
    parser.add_argument("--hz", type=float, default=25.0, help="Publish rate in Hz (default: 25)")
    parser.add_argument("--bitrate", type=int, default=500000, help="CAN bitrate (default: 500000)")
    args = parser.parse_args()

    if not (1 <= args.node_id <= 125):
        print(f"Node ID must be 1-125, got {args.node_id}")
        sys.exit(1)

    node = make_node(args.can, args.node_id, args.bitrate)

    msg = make_fix2(
        lat_deg=-33.856784,
        lon_deg=151.215297,
        alt_msl_m=50.0,
        alt_ellipsoid_m=80.0,
    )

    interval_s = 1.0 / args.hz
    seq = 0
    last_print = time.time()
    consecutive_failures = 0

    print(f"Publishing Fix2 at {args.hz}Hz (interval={interval_s*1000:.1f}ms)")
    print(f"  Position: lat={-33.856784:.4f}, lon={151.215297:.4f}")
    print(f"  Fix: 3D, sats=12, pdop=1.5, stationary")
    print(f"Press Ctrl+C to stop.")
    print()

    try:
        while True:
            try:
                msg.timestamp.usec = int(time.time() * 1e6)
                msg.gnss_timestamp.usec = msg.timestamp.usec
                node.broadcast(msg)
                consecutive_failures = 0
                seq += 1
            except CanOperationError as e:
                consecutive_failures += 1
                print(f"  [{time.time():.1f}] CAN write failed ({e})."
                      f" failures={consecutive_failures}")
                if consecutive_failures >= _MAX_CONSECUTIVE_FAILURES:
                    print(f"  Too many failures, reinitializing DroneCAN node...")
                    try:
                        node.close()
                    except Exception:
                        pass
                    node = make_node(args.can, args.node_id, args.bitrate)
                    consecutive_failures = 0
                time.sleep(_ENOBUFS_RETRY_DELAY)
                continue
            except TransferError:
                # Transient DroneCAN transfer error, skip this frame
                pass

            now = time.time()
            if now - last_print >= 5.0:
                print(f"  [{now:.1f}] Published {seq} msgs in {(now - last_print):.1f}s ({seq / (now - last_print):.1f}/s avg)")
                seq = 0
                last_print = now

            try:
                node.spin(timeout=0)
            except TransferError:
                pass

            elapsed = time.time() - now
            sleep_remain = interval_s - elapsed
            if sleep_remain > 0:
                time.sleep(sleep_remain)

    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        pass


if __name__ == "__main__":
    main()
