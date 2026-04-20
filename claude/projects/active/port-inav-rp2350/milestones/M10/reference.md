# M10: Stabilized Flight — First Flight — Reference

**Goal:** Stable ACRO/ANGLE mode flight with manual control.

> **About the search tool:** The `search.py` script at `~/Documents/planes/rpi_pico_2350_port/`
> searches thousands of pages of pre-project research — including a detailed implementation guide
> (PDF + MD, 3,000+ lines), Betaflight PR analysis, and a full Claude research session. Use it to
> quickly find relevant implementation details without reading everything.

## Quick Searches
```bash
cd ~/Documents/planes/rpi_pico_2350_port
./search.py --doc PDF scheduler
./search.py --doc PDF PID
./search.py --doc CHAT arming
./search.py --doc MD timing
./search.py --list-sections | grep -iE 'pid|flight|scheduler|arm|loop|timing'
grep -n -i 'scheduler\|cycle\|loop\|pid\|arming' inav_rp2350_port_plan.md | head -30
```

---

## Loop Rate Target

- **8kHz** (125μs) if CPU headroom allows — matches `TASK_GYROPID_DESIRED_PERIOD 125`
- **4kHz** (250μs) initial target — more achievable for first flight
- RP2350 at 150MHz should handle 4kHz comfortably; benchmark before targeting 8kHz

### CPU Budget at 4kHz (250μs per cycle)
| Task | Budget |
|------|--------|
| Gyro SPI read (DMA) | ~20μs |
| PID computation | ~30μs |
| Motor DShot update | ~5μs (PIO, nearly free) |
| Scheduler overhead | ~10μs |
| Remaining (GPS, nav, USB) | ~185μs |

---

## Gyro → PID → Motor Pipeline

All platform-agnostic in INAV — should work once M5 and M7 are solid:
```
[Gyro data-ready EXTI]
    → gyroReadSensor()     // SPI DMA read (M5)
    → gyroFilter()         // software lowpass/notch
    → pidController()      // P/I/D terms → output
    → mixTable()           // mix for airframe type
    → pwmWriteMotor()      // DShot via PIO (M7)
    → pwmCompleteMotorUpdate()
```

### Task Priorities (INAV Scheduler)
```c
// Highest priority — must complete every cycle
DEFINE_TASK(gyroTask, NULL, gyroUpdate, TASK_PRIORITY_REALTIME, 125);  // 8kHz

// Medium — every 4 cycles (1kHz)
DEFINE_TASK(pidTask, NULL, pidUpdate, TASK_PRIORITY_HIGH, 1000);

// Lower — background tasks
DEFINE_TASK(gpsTask, ...)
DEFINE_TASK(navTask, ...)
```

---

## Arming & Disarming

INAV's arming logic is platform-agnostic. Verify these work:
- **Arm:** Stick command (throttle low + yaw right) or switch
- **Disarm:** Stick command or switch; also triggers on failsafe
- **Arming checks:** gyro calibrated, receiver connected, no system faults
- **`pwmEnableMotors()`** called on arm — motors start receiving DShot
- **`pwmDisableMotors()`** / `pwmShutdownPulsesForAllMotors()` called on disarm

---

## Flight Modes (all platform-agnostic)

| Mode | What It Does |
|------|-------------|
| ACRO | Rate control — pure gyro stabilization |
| ANGLE | Self-leveling using accelerometer |
| HORIZON | Blend of ACRO and ANGLE |

For first flight: test ACRO first (no accel dependency), then ANGLE.

---

## DWT Cycle Counter (for scheduler timing)

```c
// M2 reference already covers enabling DWT
// INAV scheduler uses getCycleCounter() for precise task timing
// Verify DWT is enabled and counting before first flight:
uint32_t before = getCycleCounter();
delay(1);
uint32_t after = getCycleCounter();
// Difference should be ~150000 (1ms at 150MHz)
```

---

## Bench Testing Before First Flight

1. **Self-level test (ANGLE mode):** Tilt board → motors respond to level it
   - Motor on "heavy side" should spin up
2. **PID response:** Apply stick input → motors respond in correct direction
3. **Failsafe:** Remove RC → motors stop after failsafe timeout
4. **Cycle time:** CLI `status` → verify loop time consistent (~250μs or 125μs)
5. **CPU load:** ensure not exceeding ~70% of cycle time

---

## PID Initial Values

Start conservative for first flight — can tune after:
```
P: 20-30  I: 20  D: 10  (roll/pitch)
P: 50    I: 40  D: 0    (yaw)
```
Lower rates → more stable, easier to tune.

---

## Multicore Consideration

By M10 everything still runs on core 0. Multicore offload (OSD) comes in M12.
- Do NOT use multicore in M10 — keep it simple until flight is proven

---

## First Flight Checklist

- [ ] Props **off** for all bench tests
- [ ] Verify motor direction and order (use motor test in configurator)
- [ ] Verify receiver input is correct (Rx tab — sticks move channels)
- [ ] Verify arming/disarming works
- [ ] Verify failsafe activates (turn off TX → motors stop)
- [ ] Set conservative PIDs
- [ ] Open area for first flight, fly in ANGLE mode
- [ ] Have a reliable disarm method ready
