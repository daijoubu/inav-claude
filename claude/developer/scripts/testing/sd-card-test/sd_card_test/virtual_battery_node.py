"""
Virtual DroneCAN battery node.

Publishes uavcan.equipment.power.BatteryInfo on CAN bus, with a scripted
idle -> load-sag -> idle voltage/current profile for reproducing the
2026-08-16 NEMESIS flight anomaly (fix-dronecan-cell-voltage-calculation
project): idle cell voltage reading low by a factor consistent with a
mis-detected cell count, and displayed cell voltage not tracking pack
voltage proportionally under a load-induced sag.

Usage:
    python3 virtual_battery_node.py [--node-id 80] [--can vcan0] [--hz 10]
        [--cells 3] [--idle-cell-v 4.10] [--idle-duration 15]
        [--sag-pack-v 10.1] [--sag-current 44] [--ramp-s 1.5] [--sag-duration 20]

Requires: dronecan, python-can, and a CAN interface (vcan0 for SITL, can0 via
slcand for real hardware).
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

BatteryInfo = dronecan.uavcan.equipment.power.BatteryInfo

HEALTH_OK       = 0
HEALTH_WARNING  = 1
HEALTH_ERROR    = 2
HEALTH_CRITICAL = 3
HEALTH_NAMES    = {0: 'OK', 1: 'WARNING', 2: 'ERROR', 3: 'CRITICAL'}

STATUS_FLAG_NAMES = {
    1:    'IN_USE',
    2:    'CHARGING',
    4:    'CHARGED',
    8:    'TEMP_HOT',
    16:   'TEMP_COLD',
    32:   'OVERLOAD',
    64:   'BAD_BATTERY',
    128:  'NEED_SERVICE',
    256:  'BMS_ERROR',
}

# ENOBUFS from socketcan - FC went offline / TX queue full
_ENOBUFS_RETRY_DELAY = 1.0
_MAX_CONSECUTIVE_FAILURES = 10


class Profile:
    """Idle -> load-sag -> idle voltage/current profile, cycling forever.

    Phase timeline (seconds from start of each cycle):
      [0, idle_duration)                        -> idle
      [idle_duration, idle_duration+ramp_s)      -> ramp down to sag values
      [idle_duration+ramp_s, +sag_duration)      -> held at sag values
      [.., +ramp_s)                              -> ramp back up to idle
      then repeats
    """

    def __init__(self, cells, idle_cell_v, sag_pack_v, sag_current, idle_duration, ramp_s, sag_duration):
        self.idle_pack_v = cells * idle_cell_v
        self.sag_pack_v = sag_pack_v
        self.sag_current = sag_current
        self.idle_duration = idle_duration
        self.ramp_s = ramp_s
        self.sag_duration = sag_duration
        self.cycle_s = idle_duration + ramp_s + sag_duration + ramp_s
        self.t0 = time.time()

    def sample(self):
        t = (time.time() - self.t0) % self.cycle_s
        d, r, s = self.idle_duration, self.ramp_s, self.sag_duration

        if t < d:
            return self.idle_pack_v, 0.5, 'idle'
        if t < d + r:
            frac = (t - d) / r
            v = self.idle_pack_v + frac * (self.sag_pack_v - self.idle_pack_v)
            i = frac * self.sag_current
            return v, i, 'ramp-down'
        if t < d + r + s:
            return self.sag_pack_v, self.sag_current, 'sag'
        frac = (t - (d + r + s)) / r
        v = self.sag_pack_v + frac * (self.idle_pack_v - self.sag_pack_v)
        i = (1.0 - frac) * self.sag_current
        return v, i, 'ramp-up'


def make_battery_info(voltage, current, battery_id, status_flags=0):
    msg = BatteryInfo()
    msg.temperature = 298.15  # 25C in Kelvin
    msg.voltage = voltage
    msg.current = current
    msg.average_power_10sec = voltage * current
    msg.remaining_capacity_wh = 50.0
    msg.full_charge_capacity_wh = 74.0
    msg.hours_to_full_charge = 0.0
    msg.status_flags = status_flags
    msg.state_of_health_pct = 95
    msg.state_of_charge_pct = 67
    msg.state_of_charge_pct_stdev = 5
    msg.battery_id = battery_id
    msg.model_instance_id = 1
    msg.model_name.data = list(b'SITLBatt')
    msg.model_name.len = len(msg.model_name.data)
    return msg


def make_node(can_iface: str, node_id: int, bitrate: int):
    print(f"Initializing DroneCAN node {node_id} on {can_iface}...")
    node = dronecan.make_node(can_iface, node_id=node_id, bitrate=bitrate)
    print(f"  Spin started.")
    return node


def main():
    parser = argparse.ArgumentParser(description="Virtual DroneCAN battery node")
    parser.add_argument("--node-id", type=int, default=80, help="CAN node ID (default: 80)")
    parser.add_argument("--can", default="vcan0", help="CAN interface (default: vcan0)")
    parser.add_argument("--hz", type=float, default=10.0, help="Publish rate in Hz (default: 10)")
    parser.add_argument("--bitrate", type=int, default=500000, help="CAN bitrate (default: 500000)")
    parser.add_argument("--battery-id", type=int, default=0, help="battery_id field (default: 0)")

    parser.add_argument("--cells", type=int, default=3, help="Simulated pack cell count (default: 3)")
    parser.add_argument("--idle-cell-v", type=float, default=4.10,
                        help="Resting per-cell voltage, volts (default: 4.10)")
    parser.add_argument("--idle-duration", type=float, default=15.0,
                        help="Seconds to hold idle voltage before sagging (default: 15)")

    parser.add_argument("--sag-pack-v", type=float, default=10.1,
                        help="Pack voltage under load, volts (default: 10.1, matches the"
                             " 2026-08-16 NEMESIS footage's ~44A load event)")
    parser.add_argument("--sag-current", type=float, default=44.0,
                        help="Current under load, amps (default: 44.0)")
    parser.add_argument("--ramp-s", type=float, default=1.5,
                        help="Seconds to ramp between idle and sag (default: 1.5)")
    parser.add_argument("--sag-duration", type=float, default=20.0,
                        help="Seconds to hold sag values before ramping back to idle (default: 20)")

    parser.add_argument("--static", action="store_true",
                        help="Publish a fixed idle voltage/current forever, no sag cycling"
                             " (useful for isolating the idle cell-count-detect case alone)")
    parser.add_argument("--health", type=int, default=0, choices=[0, 1, 2, 3],
                        help="Node health: 0=OK 1=WARNING 2=ERROR 3=CRITICAL (default: 0)")
    parser.add_argument("--status-flags", type=int, default=0,
                        help="BatteryInfo status_flags bitmask to publish (default: 0)")
    args = parser.parse_args()

    if not (1 <= args.node_id <= 125):
        print(f"Node ID must be 1-125, got {args.node_id}")
        sys.exit(1)

    node = make_node(args.can, args.node_id, args.bitrate)
    node.health = args.health
    print(f"  Health: {HEALTH_NAMES[node.health]}")

    profile = Profile(
        cells=args.cells,
        idle_cell_v=args.idle_cell_v,
        sag_pack_v=args.sag_pack_v,
        sag_current=args.sag_current,
        idle_duration=args.idle_duration,
        ramp_s=args.ramp_s,
        sag_duration=args.sag_duration,
    )

    print(f"Publishing BatteryInfo at {args.hz}Hz, battery_id={args.battery_id}")
    print(f"  Idle: {args.cells}S @ {args.idle_cell_v:.2f}V/cell = {args.cells * args.idle_cell_v:.2f}V pack, 0.5A")
    if args.static:
        print(f"  --static: holding idle values forever, no sag cycling")
    else:
        print(f"  Sag event: pack -> {args.sag_pack_v:.1f}V @ {args.sag_current:.1f}A,"
              f" ramp {args.ramp_s:.1f}s, hold {args.sag_duration:.1f}s,"
              f" cycle period {profile.cycle_s:.1f}s")
    if args.status_flags:
        names = [n for f, n in STATUS_FLAG_NAMES.items() if args.status_flags & f]
        print(f"  status_flags=0x{args.status_flags:x} ({', '.join(names)})")
    print(f"Press Ctrl+C to stop.")
    print()

    interval_s = 1.0 / args.hz
    seq = 0
    last_print = time.time()
    last_phase = None
    consecutive_failures = 0

    try:
        while True:
            loop_start = time.time()

            if args.static:
                voltage = args.cells * args.idle_cell_v
                current = 0.5
                phase = 'idle (static)'
            else:
                voltage, current, phase = profile.sample()

            if phase != last_phase:
                print(f"  [{time.time():.1f}] Phase -> {phase} (voltage={voltage:.2f}V, current={current:.1f}A)")
                last_phase = phase

            msg = make_battery_info(voltage, current, args.battery_id, args.status_flags)

            try:
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
                    node.health = args.health
                    consecutive_failures = 0
                time.sleep(_ENOBUFS_RETRY_DELAY)
                continue
            except TransferError:
                pass

            now = time.time()
            if now - last_print >= 5.0:
                print(f"  [{now:.1f}] Published {seq} msgs in {(now - last_print):.1f}s"
                      f" ({seq / (now - last_print):.1f}/s avg), current phase={phase},"
                      f" voltage={voltage:.2f}V, current={current:.1f}A")
                seq = 0
                last_print = now

            try:
                node.spin(timeout=0)
            except TransferError:
                pass

            elapsed = time.time() - loop_start
            sleep_remain = interval_s - elapsed
            if sleep_remain > 0:
                time.sleep(sleep_remain)

    except KeyboardInterrupt:
        print("\nStopping.")


if __name__ == "__main__":
    main()
