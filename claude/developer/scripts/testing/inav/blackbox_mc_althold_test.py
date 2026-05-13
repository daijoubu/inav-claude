#!/usr/bin/env python3
"""
blackbox_mc_althold_test.py
============================
Test MC ALTHOLD climb rate using SITL blackbox.
Arms as MULTIROTOR, sweeps THROTTLE, reads navTgtVel[2].
Run against different SITL builds to compare PR results.

Usage:
  1. Start SITL: ./build_sitl/bin/SITL.elf &
  2. python3 blackbox_mc_althold_test.py
"""

import sys, time, os, struct, threading, socket, subprocess, glob

SITL_HOST = 'localhost'
RC_PORT   = 5761
MSP_PORT  = 5760

SITL_DIR  = "/home/raymorris/Documents/planes/inavflight/inav2/build_sitl_pr11359"
DECODER   = "/home/raymorris/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode"

MAX_CLIMB         = 700
ALT_HOLD_DEADBAND = 40
HOVER_THR         = 1300   # nav_mc_hover_thr — asymmetric to stress-test
IDLE_THR          = 1050   # default nav_mc_idle_thr
MAX_THR           = 2000

RC_LOW  = 1000
RC_MID  = 1500
RC_HIGH = 2000

GPS_FIX  = 2
GPS_SATS = 14
GPS_LAT  = 515074000
GPS_LON  = -1278000
GPS_ALT_CM = 5000

MSP_API_VERSION    = 1
MSP_SET_RAW_RC     = 200
MSP_SET_RAW_GPS    = 201
MSP_SET_RX_CONFIG  = 45
MSP_SET_MODE_RANGE = 35
MSP_EEPROM_WRITE   = 250
MSP_REBOOT         = 68
MSP2_INAV_STATUS   = 0x2000
MSP_SIMULATOR      = 0x201F

RX_TYPE_MSP   = 2
BOXARM        = 0
BOXNAVALTHOLD = 3

BIT_ARMED      = (1 << 2)
BIT_CALIB      = (1 << 9)
BIT_ARM_SWITCH = (1 << 14)
BIT_RC_LINK    = (1 << 18)
BIT_THROTTLE   = (1 << 19)
BIT_CLI        = (1 << 20)

BLOCKING_BITS = (BIT_CALIB | BIT_RC_LINK | BIT_THROTTLE | BIT_CLI |
                 (1<<1) | (1<<11) | (1<<12))


def _crc8(data):
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc

def v1(cmd, data=None):
    d = bytes(data or [])
    cs = len(d) ^ cmd
    for b in d: cs ^= b
    return bytes([0x24, 0x4D, 0x3C, len(d), cmd]) + d + bytes([cs])

def v2(cmd, data=None):
    p = bytes(data or [])
    h = bytes([0x24, 0x58, 0x3C, 0x00,
               cmd & 0xFF, (cmd >> 8) & 0xFF,
               len(p) & 0xFF, (len(p) >> 8) & 0xFF])
    return h + p + bytes([_crc8(h[3:] + p)])

def parse(buf):
    i = 0
    while i < len(buf) - 4:
        if buf[i] == 0x24:
            if buf[i+1] == 0x4D and i+5 <= len(buf):
                sz = buf[i+3]
                if i+5+sz <= len(buf):
                    return buf[i+4], buf[i+5:i+5+sz]
            elif buf[i+1] == 0x58 and i+9 <= len(buf):
                sz  = buf[i+6] | (buf[i+7] << 8)
                cmd = buf[i+4] | (buf[i+5] << 8)
                if i+9+sz <= len(buf):
                    return cmd, buf[i+8:i+8+sz]
        i += 1
    return None, None

def xchg(sock, frame, timeout=1.5):
    try: sock.sendall(frame)
    except Exception as e:
        print(f"  send error: {e}"); return None, None
    sock.settimeout(timeout)
    buf, dl = b"", time.time() + timeout
    while time.time() < dl:
        try:
            c = sock.recv(1024)
            if not c: break
            buf += c
            cmd, d = parse(buf)
            if cmd is not None: return cmd, d
        except socket.timeout: break
    return parse(buf)

def send_drop(sock, frame):
    try:
        sock.sendall(frame)
        sock.settimeout(0.01)
        try: sock.recv(64)
        except socket.timeout: pass
    except Exception: pass

def flag_names(af):
    n = {(1<<1):"FAILSAFE", (1<<3):"WAS_EVER_ARMED", BIT_CALIB:"CALIB",
         (1<<11):"NAV_UNSAFE", (1<<12):"NAV_UNSAFE2", BIT_ARM_SWITCH:"ARM_SWITCH",
         BIT_RC_LINK:"RC_LINK", BIT_THROTTLE:"THROTTLE", BIT_CLI:"CLI"}
    return [v for k, v in n.items() if af & k]

def get_af(msp_sock):
    cmd, d = xchg(msp_sock, v2(MSP2_INAV_STATUS), timeout=1.5)
    if d and len(d) >= 13:
        return struct.unpack_from('<I', d, 9)[0]
    return None


class RCSender(threading.Thread):
    def __init__(self, rc_sock):
        super().__init__(daemon=True)
        self._s   = rc_sock
        self.roll=RC_MID; self.pitch=RC_MID; self.thr=RC_LOW
        self.yaw=RC_MID;  self.aux1=RC_LOW;  self.aux2=RC_LOW
        self._lk  = threading.Lock()
        self._run  = True
        self._n    = 0

    def set(self, **kw):
        with self._lk:
            for k, v in kw.items(): setattr(self, k, v)

    def run(self):
        while self._run:
            with self._lk:
                r,p,t,y,a1,a2 = self.roll,self.pitch,self.thr,self.yaw,self.aux1,self.aux2
            chs  = [r, p, t, y, a1, a2] + [RC_MID]*10
            rc_d = b"".join(struct.pack('<H', c) for c in chs)
            gps_d = struct.pack('<BBiiHH', GPS_FIX, GPS_SATS,
                                GPS_LAT, GPS_LON, GPS_ALT_CM, 0)
            send_drop(self._s, v1(MSP_SET_RAW_RC, rc_d))
            send_drop(self._s, v1(MSP_SET_RAW_GPS, gps_d))
            self._n += 1
            if self._n % 25 == 0:
                send_drop(self._s, v2(MSP_SIMULATOR, [2, 1]))
            time.sleep(0.02)

    def stop(self): self._run = False; self.join(1.0)


def configure_via_cli():
    print("[CLI] Connecting to port 5760...")
    try:
        s = socket.socket()
        s.connect((SITL_HOST, MSP_PORT))
        s.settimeout(3.0)
    except Exception as e:
        print(f"  ERROR: {e}"); return False

    def cli(cmd):
        s.sendall((cmd + '\n').encode())
        resp = b""
        dl = time.time() + 2.5
        while time.time() < dl:
            try:
                c = s.recv(4096)
                if not c: break
                resp += c
                if b'# ' in resp[-15:] or b'Rebooting' in resp: break
            except socket.timeout: break
        return resp.decode(errors='replace')

    s.sendall(b'#')
    time.sleep(0.5)
    try: s.recv(4096)
    except: pass

    for cmd in ["feature BLACKBOX",
                "set blackbox_device = FILE",
                "set platform_type = MULTIROTOR",
                "set receiver_type = MSP",
                "set nav_mc_manual_climb_rate = 700",
                "set alt_hold_deadband = 40",
                "set nav_mc_hover_thr = 1300",
                "set nav_mc_althold_throttle = 1"]:   # 1 = HOVER mode
        r = cli(cmd)
        for line in r.splitlines():
            l = line.strip()
            if l and '#' not in l and l != cmd:
                print(f"  {cmd[:40]}: {l}")

    print("  Saving...")
    s.sendall(b'save\n')
    time.sleep(0.3)
    try: resp = s.recv(256).decode(errors='replace')
    except: resp = ""
    print(f"  save -> {resp.strip()!r}")
    s.close()
    return True


def configure_via_msp(msp_sock):
    print("[MSP] Setting mode ranges...")
    xchg(msp_sock, v1(MSP_SET_MODE_RANGE, bytes([0, BOXARM, 0, 32, 48])), timeout=0.3)
    xchg(msp_sock, v1(MSP_SET_MODE_RANGE, bytes([1, BOXNAVALTHOLD, 1, 32, 48])), timeout=0.3)
    print("  ARM=AUX1>1700, NAVALTHOLD=AUX2>1700")

    xchg(msp_sock, v1(MSP_EEPROM_WRITE), timeout=0.5)
    time.sleep(0.2)
    xchg(msp_sock, v1(MSP_REBOOT), timeout=0.3)
    return True


def run_flight(rc_sock, msp_sock):
    for _ in range(5):
        xchg(msp_sock, v2(MSP_SIMULATOR, [2, 1]), timeout=0.3)
        time.sleep(0.05)
    print("  HITL enabled")

    # Throttle must start LOW to clear THROTTLE arming blocker for MC
    rc = RCSender(rc_sock)
    rc.set(thr=RC_LOW, pitch=RC_MID, aux1=RC_LOW, aux2=RC_LOW)
    rc.start()

    print("  Waiting for RC link + blockers to clear (thr=LOW)...")
    ready = False
    for i in range(150):
        time.sleep(0.1)
        af = get_af(msp_sock)
        if af is None: continue
        if (af & BLOCKING_BITS) == 0:
            print(f"  Ready to arm at t={(i+1)*0.1:.1f}s (flags=0x{af:08X})")
            ready = True
            break
        if i % 20 == 19:
            print(f"  t={(i+1)*0.1:.0f}s flags=0x{af:08X} {flag_names(af)}")

    if not ready:
        af = get_af(msp_sock)
        print(f"  WARNING: still have blockers: {flag_names(af or 0)}")

    armed = False
    for attempt in range(3):
        print(f"  Arm attempt {attempt+1}: AUX1=HIGH (thr=LOW)...")
        rc.set(aux1=RC_HIGH, thr=RC_LOW)

        for i in range(60):
            time.sleep(0.1)
            af = get_af(msp_sock)
            if af is None: continue
            if af & BIT_ARMED:
                armed = True
                print(f"  ARMED! flags=0x{af:08X}")
                break
            if (af & BIT_ARM_SWITCH) and attempt < 2:
                print(f"  ARM_SWITCH latched - resetting...")
                rc.set(aux1=RC_LOW)
                time.sleep(1.5)
                break
            if i % 20 == 19:
                print(f"  t={(i+1)*0.1:.0f}s flags=0x{af:08X} {flag_names(af)}")

        if armed: break

    if not armed:
        af = get_af(msp_sock)
        print(f"  ARMING FAILED: flags=0x{af or 0:08X} {flag_names(af or 0)}")
        rc.stop()
        return False

    # Ramp to hover throttle, then enable ALTHOLD
    print(f"  Ramping to hover ({HOVER_THR}), then enabling ALTHOLD...")
    rc.set(thr=HOVER_THR)
    time.sleep(2)
    rc.set(aux2=RC_HIGH)
    time.sleep(2)

    af = get_af(msp_sock)
    print(f"  flags=0x{af or 0:08X} after ALTHOLD enable")

    # Throttle sweep: hover, then various positions
    sweep = [
        (HOVER_THR, "hover/neutral",  4),
        (1600,      "+300 climb",     6),
        (HOVER_THR, "hover/neutral",  3),
        (1800,      "+500 climb",     6),
        (HOVER_THR, "hover/neutral",  3),
        (2000,      "full up",        6),
        (HOVER_THR, "hover/neutral",  3),
        (1100,      "-200 descend",   6),
        (HOVER_THR, "hover/neutral",  3),
        (1050,      "near-idle",      6),
        (HOVER_THR, "hover/neutral",  3),
    ]

    print("\n  Throttle sweep:")
    for pwm, lbl, secs in sweep:
        rc.set(thr=pwm)
        print(f"    thr={pwm} ({lbl}) {secs}s")
        time.sleep(secs)

    print("  Disarming...")
    rc.set(aux2=RC_LOW, aux1=RC_LOW, thr=RC_LOW)
    time.sleep(4)
    rc.stop()
    print("  Done.")
    return True


def decode_and_analyze(logfile):
    print(f"\n[Decode] {logfile} ({os.path.getsize(logfile)} bytes)")

    res = subprocess.run([DECODER, "--stdout", logfile],
                         capture_output=True, text=True, timeout=60)
    if res.returncode != 0:
        print(f"  ERROR: rc={res.returncode}: {res.stderr[:500]}"); return
    if not res.stdout.strip():
        print(f"  ERROR: empty output"); return

    lines = res.stdout.splitlines()
    cols  = [c.strip() for c in lines[0].split(',')]

    # mcPosAxisP[2] = posControl.pids.pos[Z].output_constrained = targetVel = climbRateDemand
    # This is the direct output of the rcClimbRate formula, signed (negative = descend)
    vz_col  = next((c for c in cols if 'mcPosAxisP' in c and '[2]' in c), None)
    # Fallback to navTgtVel[2] if mcPosAxisP[2] not found
    if not vz_col:
        vz_col = next((c for c in cols if 'navTgtVel' in c and '[2]' in c), None)
    thr_col = 'rcData[3]' if 'rcData[3]' in cols else None  # THROTTLE is function index 3

    if not vz_col:
        print(f"  mcPosAxisP[2]/navTgtVel[2] not found. Nav cols: {[c for c in cols if 'nav' in c.lower() or 'mc' in c.lower()]}")
        return

    vz_idx   = cols.index(vz_col)
    time_idx = cols.index('time (us)') if 'time (us)' in cols else 0
    thr_idx  = cols.index(thr_col) if thr_col else None
    print(f"  '{vz_col}' col={vz_idx}, throttle=rcData[3] col={thr_idx}")

    records = []
    for line in lines[1:]:
        parts = line.split(',')
        if len(parts) <= vz_idx: continue
        try:
            records.append((int(parts[time_idx].strip()),
                            int(parts[vz_idx].strip()),
                            int(parts[thr_idx].strip()) if thr_idx else 0))
        except ValueError: continue

    if not records:
        print("  No records."); return

    t0  = records[0][0]
    dur = (records[-1][0] - t0) / 1e6
    print(f"  {len(records)} records, {dur:.1f}s")

    # Find 1.5s windows with stable navTgtVel[2]
    stable, i = [], 0
    while i < len(records):
        t_s  = records[i][0]
        vals = [(v, th) for t, v, th in records if t_s <= t < t_s + 1_500_000]
        if len(vals) >= 20:
            vs = [v for v, _ in vals]
            mean = sum(vs) / len(vs)
            std  = (sum((x-mean)**2 for x in vs)/len(vs))**0.5
            if std < 25:
                stable.append([t_s-t0, mean, std, len(vals),
                                sum(th for _, th in vals)/len(vals)])
        while i < len(records) and records[i][0] < t_s + 1_000_000:
            i += 1

    if not stable:
        print("  No stable windows found."); return

    # Merge adjacent similar windows
    merged = []
    for e in stable:
        t_r, mean, std, n, thr = e
        if (merged and abs(mean - merged[-1][1]) < 15
                and (t_r - merged[-1][0]) < 2_000_000):
            p = merged[-1]; nn = p[3]+n
            merged[-1] = [p[0], (p[1]*p[3]+mean*n)/nn, max(p[2],std), nn,
                          (p[4]*p[3]+thr*n)/nn]
        else:
            merged.append(e[:])

    test_pwms = [HOVER_THR, 1600, 1800, 2000, 1100, 1050]

    print(f"\n  {'t(s)':>6} {'Avg Thr':>8} {'climbRateDemand':>16} {'std':>6}  (mcPosAxisP[2])")
    print("  " + "-"*40)
    for e in merged:
        t_r, mean, std, n, avg_thr = e
        print(f"  {t_r/1e6:>6.1f} {avg_thr:>8.0f} {mean:>14.1f} {std:>6.1f}")

    print(f"\n  Log: {logfile}")


def main():
    print("=" * 70)
    print("MC ALTHOLD — SITL Blackbox Test")
    print(f"hover={HOVER_THR}, idle={IDLE_THR}, deadband={ALT_HOLD_DEADBAND}, max_climb={MAX_CLIMB}")
    print("=" * 70)

    if not os.path.exists(DECODER):
        print(f"ERROR: decoder not found at {DECODER}"); return 1

    print("[1] CLI config...")
    configure_via_cli()
    print("    Waiting 12s for reboot...")
    time.sleep(12)

    print("\n[2] MSP config...")
    try:
        msp_sock = socket.socket()
        msp_sock.connect((SITL_HOST, MSP_PORT))
        msp_sock.settimeout(2.0)
    except Exception as e:
        print(f"  ERROR: {e}"); return 1

    cmd, data = xchg(msp_sock, v1(MSP_API_VERSION), timeout=2.0)
    if data is None:
        print("  ERROR: No MSP"); msp_sock.close(); return 1
    print(f"  FC OK: {data.hex()[:20]}")

    configure_via_msp(msp_sock)
    msp_sock.close()
    print("    Waiting 18s for reboot...")
    time.sleep(18)

    print("\n[3] Connecting for flight...")
    try:
        rc_sock = socket.socket(); rc_sock.connect((SITL_HOST, RC_PORT)); rc_sock.settimeout(0.1)
        msp_sock = socket.socket(); msp_sock.connect((SITL_HOST, MSP_PORT)); msp_sock.settimeout(2.0)
    except Exception as e:
        print(f"  ERROR: {e}"); return 1

    cmd, data = xchg(msp_sock, v1(MSP_API_VERSION), timeout=2.0)
    if data is None:
        print("  ERROR: No MSP after reboot"); return 1
    print(f"  FC OK: {data.hex()[:20]}")

    pre_logs = set(glob.glob(os.path.join(SITL_DIR, "20*.TXT")))

    print("\n[4] Running flight sequence...")
    ok = run_flight(rc_sock, msp_sock)
    rc_sock.close(); msp_sock.close()
    if not ok:
        print("Flight failed"); return 1

    print("\n[5] Finding log...")
    time.sleep(3)
    post_logs = set(glob.glob(os.path.join(SITL_DIR, "20*.TXT")))
    new_logs  = post_logs - pre_logs
    if new_logs:
        logfile = sorted(new_logs)[-1]
    else:
        all_logs = sorted(glob.glob(os.path.join(SITL_DIR, "20*.TXT")), key=os.path.getmtime)
        if not all_logs:
            print("  ERROR: No logs found"); return 1
        logfile = all_logs[-1]
    print(f"  {logfile} ({os.path.getsize(logfile)} bytes)")

    print("\n[6] Decoding...")
    decode_and_analyze(logfile)
    return 0


if __name__ == '__main__':
    sys.exit(main())
