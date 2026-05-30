"""
Overnight DroneCAN monitor.

Runs arm/disarm cycles while monitoring:
- DroneCAN MSP status (bus_off, error_passive, TEC, REC, LEC)
- Arming flags (decodes ALL flags including HWFAIL)
- Node 1 CAN heartbeat via candump filter
- Full candump log for post-analysis

Stops when failure detected or deadline reached.
"""
import argparse
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta

# Add parent to path for standalone use
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sd_card_test.fc_control import FCControl
from sd_card_test.contexts import FCContexts
from sd_card_test.msp import MSPCode, MSPParse
from sd_card_test.models import ArmingFlag


HERE = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(HERE, "overnight_logs")


class OvernightMonitor:

    STOP_BUS_OFF = "bus_off"
    STOP_NODE1_LOST = "node1_lost"
    STOP_HWFAIL = "hwfail"
    STOP_DEADLINE = "deadline"
    STOP_MAX_CYCLES = "max_cycles"

    def __init__(self, port: str, can_iface: str = "can0",
                 deadline: str = "06:30", max_cycles: int = 0):
        self.port = port
        self.can_iface = can_iface
        self.deadline = self._parse_deadline(deadline)
        self.max_cycles = max_cycles
        self.fc = None
        self.candump_proc = None
        self.node1_mon_proc = None
        self.candump_log = ""
        self.node1_log = ""
        self.cycle = 0
        self.stop_reason = None
        self.bus_off_start = None

        os.makedirs(LOG_DIR, exist_ok=True)

    def _parse_deadline(self, s: str) -> datetime:
        now = datetime.now()
        parts = s.strip().split(":")
        h, m = int(parts[0]), int(parts[1])
        dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if dt <= now:
            dt += timedelta(days=1)
        return dt

    def start_candump(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.candump_log = os.path.join(LOG_DIR, f"candump_{ts}.log")
        self.node1_log = os.path.join(LOG_DIR, f"node1_heartbeat_{ts}.log")

        self.candump_proc = subprocess.Popen(
            ["candump", "-l", self.can_iface, "-f", self.candump_log],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        # Wait for candump to create the log file
        time.sleep(2)

        # Monitor node 1 heartbeat (CAN ID filter: mask lower 7 bits = node 1)
        with open(self.node1_log, "w") as f:
            self.node1_mon_proc = subprocess.Popen(
                ["candump", self.can_iface + ",1:7F"],
                stdout=f, stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )

        print(f"  CAN log:       {self.candump_log}", flush=True)
        print(f"  Node 1 log:    {self.node1_log}", flush=True)

    def stop_candump(self):
        if self.node1_mon_proc:
            os.killpg(os.getpgid(self.node1_mon_proc.pid), signal.SIGTERM)
            self.node1_mon_proc = None
        if self.candump_proc:
            self.candump_proc.terminate()
            self.candump_proc = None

    def check_node1_alive(self) -> bool:
        """Check if node 1 has transmitted on CAN in the last 3 seconds."""
        try:
            result = subprocess.run(
                ["candump", self.can_iface + ",1:7F", "-n", "1", "-T", "2000"],
                capture_output=True, text=True, timeout=5
            )
            return bool(result.stdout.strip())
        except Exception:
            return False

    def run_cycle(self) -> dict:
        """Single arm/disarm cycle with DroneCAN monitoring."""
        result = {
            "armed": False,
            "dronecan": None,
            "arming_status": None,
            "arming_flags": 0,
            "arming_flag_names": [],
            "duration": 0,
            "fail_msg": "",
        }
        cycle_start = time.time()

        contexts = FCContexts(self.fc)

        with contexts.armed(timeout=30) as armed:
            if not armed:
                a = self.fc.get_arming_status()
                if a:
                    result["arming_flags"] = a.arming_flags
                    result["arming_flag_names"] = ArmingFlag.decode_flags(a.arming_flags)
                result["fail_msg"] = armed.error or ""
                result["duration"] = time.time() - cycle_start
                return result

            result["armed"] = True

            # Run servo stress while polling DroneCAN
            stress = self.fc.start_servo_stress_background(
                2.0, pattern='sweep', servo_channels=[0, 1, 2, 3]
            )

            # Poll DroneCAN every 500ms during armed period
            dronecan_obs = []
            poll_end = time.time() + 2.5
            while time.time() < poll_end:
                try:
                    resp = self.fc.send_receive(MSPCode.DRONECAN_STATUS, timeout=0.6)
                    if resp:
                        p = MSPParse.dronecan_status(resp)
                        if p:
                            dronecan_obs.append(p)
                except Exception:
                    pass
                time.sleep(0.45)

            self.fc.wait_for_servo_stress(stress)

        # After context exits (disarmed), get final arming status
        a = self.fc.get_arming_status()
        if a:
            result["arming_status"] = {
                "cycle_time": a.cycle_time,
                "i2c_errors": a.i2c_errors,
                "cpu_load": a.cpu_load,
            }
            result["arming_flags"] = a.arming_flags
            result["arming_flag_names"] = ArmingFlag.decode_flags(a.arming_flags)

        if dronecan_obs:
            result["dronecan"] = dronecan_obs[-1]
            result["dronecan_obs"] = dronecan_obs

        result["duration"] = time.time() - cycle_start
        return result

    def should_stop(self, cycle_result: dict) -> str:
        """Check stop conditions. Returns stop reason string or empty string."""
        dc = cycle_result.get("dronecan")

        # Bus off check
        if dc and dc.get("bus_off"):
            if self.bus_off_start is None:
                self.bus_off_start = time.time()
            elif time.time() - self.bus_off_start > 3:
                return self.STOP_BUS_OFF
        else:
            self.bus_off_start = None

        # Check arming flags for HWFAIL
        flags = cycle_result.get("arming_flags", 0)
        if flags & ArmingFlag.ARMING_DISABLED_HARDWARE_FAILURE:
            return self.STOP_HWFAIL

        return ""

    def print_cycle_summary(self, r: dict):
        armed = "ARMED" if r["armed"] else "FAIL"
        dc = r.get("dronecan")
        if dc:
            can_line = (f"TEC={dc['tec']} REC={dc['rec']} LEC={dc['lec']} "
                        f"TX={dc['tx_fifo_fill']}(hwm={dc['tx_queue_hwm']}) "
                        f"BO={dc['bus_off']} EP={dc['error_passive']}")
        else:
            can_line = "NO CAN DATA"

        flag_names = r.get("arming_flag_names", [])
        flags_str = "|".join(flag_names) if flag_names else "none"

        alive = self.check_node1_alive()
        alive_str = "Y" if alive else "**GONE**"

        print(f"  [{armed}] CAN: {can_line}  FLAGS: {flags_str}  N1:{alive_str}")

        # On failure, print all flags in detail
        if r["arming_flags"]:
            print(f"    arming_flags raw: 0x{r['arming_flags']:08x}")

    def run(self):
        start_time = datetime.now()
        print("=" * 70)
        print("OVERDRONE NIGHT: Overnight DroneCAN Failure Capture")
        print("=" * 70)
        print(f"  Start:    {start_time.strftime('%H:%M:%S')}")
        print(f"  Deadline: {self.deadline.strftime('%H:%M:%S')}")
        print(f"  Port:     {self.port}")
        print(f"  CAN:      {self.can_iface}")
        if self.max_cycles:
            print(f"  Max:      {self.max_cycles} cycles")
        print()

        self.fc = FCControl(self.port)
        if not self.fc.connect():
            print("FAILED: Cannot connect to FC")
            sys.exit(1)
        print("  FC connected")
        print()

        self.start_candump()
        print()

        self.cycle = 0
        node1_missing_cycles = 0

        while True:
            self.cycle += 1

            # Check deadline
            now = datetime.now()
            if now >= self.deadline:
                print(f"\n  DEADLINE REACHED at {now.strftime('%H:%M:%S')}")
                self.stop_reason = self.STOP_DEADLINE
                break

            if self.max_cycles and self.cycle >= self.max_cycles:
                print(f"\n  Max cycles ({self.max_cycles}) reached")
                self.stop_reason = self.STOP_MAX_CYCLES
                break

            print(f"\n--- Cycle {self.cycle} @ {now.strftime('%H:%M:%S')} ---")
            r = self.run_cycle()

            # Check node 1 alive
            node1_alive = self.check_node1_alive()
            if not node1_alive:
                node1_missing_cycles += 1
                print(f"  *** Node 1 heartbeat MISSING (cycle {node1_missing_cycles}) ***")
            else:
                node1_missing_cycles = 0

            self.print_cycle_summary(r)

            # Check stop conditions
            reason = self.should_stop(r)
            if reason == self.STOP_BUS_OFF:
                print(f"\n  *** STOP: Bus off detected for >3s ***")
                self.stop_reason = reason
                break
            elif reason == self.STOP_HWFAIL:
                names = r.get("arming_flag_names", [])
                print(f"\n  *** STOP: Hardware failure flags: {names} ***")
                self.stop_reason = reason
                break

            if node1_missing_cycles >= 2:
                print(f"\n  *** STOP: Node 1 missing for {node1_missing_cycles} cycles ***")
                self.stop_reason = self.STOP_NODE1_LOST
                break

        # Summary
        elapsed = datetime.now() - start_time
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"  Cycles:     {self.cycle}")
        print(f"  Duration:   {elapsed.total_seconds() / 60:.1f} min")
        print(f"  Stop reason: {self.stop_reason}")
        print(f"  CAN log:    {self.candump_log}")
        print(f"  Node 1 log: {self.node1_log}")
        print()

        self.stop_candump()
        self.fc.disconnect()


def main():
    parser = argparse.ArgumentParser(
        description="Overnight DroneCAN failure capture"
    )
    parser.add_argument("port", help="Serial port (e.g., /dev/ttyACM1)")
    parser.add_argument("--can", default="can0", help="CAN interface")
    parser.add_argument("--deadline", default="06:30", help="Stop time HH:MM")
    parser.add_argument("--max-cycles", type=int, default=0,
                        help="Max cycles (0=unlimited)")
    args = parser.parse_args()

    monitor = OvernightMonitor(
        port=args.port,
        can_iface=args.can,
        deadline=args.deadline,
        max_cycles=args.max_cycles,
    )
    monitor.run()


if __name__ == "__main__":
    main()
