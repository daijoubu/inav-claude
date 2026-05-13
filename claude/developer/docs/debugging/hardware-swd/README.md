# Hardware SWD Debugging with Pico Debugprobe

SWD (Serial Wire Debug) lets you flash firmware and run GDB on a flight controller without using USB DFU. For the RP2350_PICO target, this is the preferred way to debug live firmware.

## What You Need

| Item | Purpose |
|------|---------|
| A spare Raspberry Pi Pico or Pico 2 | Becomes the debugprobe (SWD adapter) |
| Three jumper wires | SWDCLK, SWDIO, GND |
| Two optional wires | UART bridge for serial console |

## UF2 Firmware Files

These files are in this directory:

| File | Use When |
|------|----------|
| `debugprobe_on_pico.uf2` | Your debug adapter is a Pico 1 (RP2040) |
| `debugprobe_on_pico2.uf2` | Your debug adapter is a Pico 2 (RP2350) |

Either Pico can debug any other Pico — e.g., a Pico 1 debugprobe can debug an RP2350_PICO target, and vice versa.

## Step 1: Flash the Debugprobe Firmware

1. Hold the BOOTSEL button on your spare Pico while plugging it in
2. It mounts as a USB mass storage device
3. Drag-and-drop the appropriate `.uf2` file onto it
4. It reboots automatically and appears as two USB devices:
   - A CMSIS-DAP SWD adapter (for OpenOCD/GDB)
   - A USB-UART bridge (for serial console)

## Step 2: Wire to the Target

Debugprobe pinout (standard — same for Pico 1 and Pico 2 debugprobe):

```
Debugprobe        Target (RP2350_PICO debug header)
──────────        ─────────────────────────────────
GND          →    GND
GP2 (SWDCLK) →    SWDCLK
GP3 (SWDIO)  →    SWDIO

Optional UART bridge:
GP4 (TX out) →    Target UART RX
GP5 (RX in)  →    Target UART TX
```

The RP2350_PICO (Pico 2) debug header is the **3-pin JST-style connector** near the USB connector, labeled GND / SWDIO / SWDCLK.

> **Do not connect 3V3 or VSYS between the two boards unless one is unpowered.** Both should be powered independently (each via their own USB cable).

## Step 3: OpenOCD

**Use the Pico SDK's OpenOCD** — the system OpenOCD (0.11.0) lacks RP2350 support.

```bash
OPENOCD=~/.pico-sdk/openocd/0.12.0+dev/openocd
SCRIPTS=~/.pico-sdk/openocd/0.12.0+dev/scripts
```

### Start OpenOCD (RP2350 target)

```bash
~/.pico-sdk/openocd/0.12.0+dev/openocd \
  -s ~/.pico-sdk/openocd/0.12.0+dev/scripts \
  -f interface/cmsis-dap.cfg \
  -f target/rp2350.cfg \
  -c "adapter speed 5000"
```

Leave this running. It listens on:
- `localhost:3333` — GDB remote target
- `localhost:4444` — OpenOCD telnet console

Expected output (verified 2026-03-03):
```
Info : Using CMSIS-DAPv2 interface with VID:PID=0x2e8a:0x000c, serial=...
Info : SWD DPIDR 0x4c013477
Info : [rp2350.dap.core0] Cortex-M33 r1p0 processor detected
Info : [rp2350.dap.core0] target has 8 breakpoints, 4 watchpoints
Info : [rp2350.dap.core1] Cortex-M33 r1p0 processor detected
Info : Listening on port 3333 for gdb connections
```

### Flash Firmware via SWD (without GDB)

```bash
~/.pico-sdk/openocd/0.12.0+dev/openocd \
  -s ~/.pico-sdk/openocd/0.12.0+dev/scripts \
  -f interface/cmsis-dap.cfg \
  -f target/rp2350.cfg \
  -c "adapter speed 5000" \
  -c "program inav/build/inav_9.0.1_RP2350_PICO.elf verify reset exit"
```

Use the `.elf` file (not `.hex`) for RP2350 — OpenOCD needs the ELF to know the correct flash address.

If you only have a `.bin`:
```bash
  -c "program inav/build/inav_9.0.1_RP2350_PICO.bin verify reset exit 0x10000000"
```

The RP2350_PICO flash starts at `0x10000000` (external XIP flash).

### OpenOCD for RP2040 (Pico 1 as target)

Replace `target/rp2350.cfg` with `target/rp2040.cfg`. Everything else is identical.

## Step 4: GDB Live Debugging

With OpenOCD already running in another terminal:

```bash
gdb-multiarch inav/build/inav_9.0.1_RP2350_PICO.elf
```

Inside GDB:
```
(gdb) target remote localhost:3333
(gdb) monitor halt                # halt the running CPU
(gdb) info target                 # show memory map (flash sections, RAM, etc.)
(gdb) x/4i $pc                   # disassemble 4 instructions at current PC
(gdb) load                        # flash firmware (optional, if not flashed yet)
(gdb) break systemInit            # set a breakpoint
(gdb) monitor resume              # resume without detaching (or use 'continue')
(gdb) backtrace                   # when stopped at a breakpoint
(gdb) info registers
```

Example: halting a live INAV build (verified 2026-03-03) shows the CPU mid-task:
```
imuUpdateAccelerometer () at inav/src/main/flight/imu.c:915
=> 0x10048298 <imuUpdateAccelerometer>:  push {r7, lr}
```

The ELF is at `inav/build/bin/RP2350_PICO.elf` (not in `build/` root — note the `bin/` subdirectory).

### Useful GDB Commands for INAV Debugging

```
(gdb) print gyroSensor1.gyroDev.gyroADCRaw   # inspect a global
(gdb) watch motorValue[0]                      # watch a variable for changes
(gdb) monitor reset halt                       # restart from beginning
(gdb) detach                                   # disconnect without stopping FC
```

## UART Serial Console

The debugprobe exposes a USB-UART bridge. Connect to it with any serial terminal:

```bash
# Find the debugprobe UART port (it's different from the FC's USB serial)
ls /dev/serial/by-id/ | grep -i pico

# Open it
screen /dev/ttyACM1 115200
# or
minicom -D /dev/ttyACM1 -b 115200
```

This is useful when the target FC's USB serial is being used for MSP (e.g., when testing the configurator connection) and you still want a debug console.

## Identifying Pico Devices by USB Product ID

Multiple Pico-based devices may be plugged in at once. Use `lsusb` to tell them apart:

| USB PID (`2e8a:XXXX`) | Device |
|-----------------------|--------|
| `000a` | Pico (RP2040) running CDC serial app (MicroPython, Arduino, IMU emulator, INAV, etc.) |
| `000b` | Pico 2 (RP2350) running CDC serial app |
| `000c` | **Debugprobe CMSIS-DAP** — this is what you want for SWD |
| `0003` | Pico in BOOTSEL / mass storage mode |

Quick check:
```bash
lsusb | grep 2e8a
# 2e8a:000c → debugprobe ready
# 2e8a:000a → Pico with serial app (IMU emulator, INAV, etc.) — NOT a debugprobe
```

OpenOCD will also tell you immediately: if no `000c` device is present it prints
`"Error: unable to find a matching CMSIS-DAP device"`.

## Troubleshooting

### "Error: unable to find a matching CMSIS-DAP device"
- Debugprobe not plugged in, or wrong UF2 flashed
- Try: `lsusb | grep -i "CMSIS\|2e8a"` (Raspberry Pi vendor ID is `2e8a`)

### "Error: DAP request failed"
- Check wiring: SWDCLK and SWDIO may be swapped
- Reduce adapter speed: `-c "adapter speed 1000"`

### OpenOCD connects but GDB can't attach
- Make sure `target remote localhost:3333` uses the right port
- Check OpenOCD is still running (it should show "Listening on port 3333")

### RP2350_PICO USB serial disappears when OpenOCD connects
- Normal — OpenOCD halts the CPU, which stops the USB stack
- Use the UART bridge console instead while debugging

### "cortex_m reset_config sysresetreq" warning
- Harmless on RP2350, ignore it

## Quick Reference

```bash
# One-liner: flash and reset (most common use)
~/.pico-sdk/openocd/0.12.0+dev/openocd \
  -s ~/.pico-sdk/openocd/0.12.0+dev/scripts \
  -f interface/cmsis-dap.cfg -f target/rp2350.cfg \
  -c "adapter speed 5000; program build/inav_9.0.1_RP2350_PICO.elf verify reset exit"

# Start OpenOCD for interactive GDB session
~/.pico-sdk/openocd/0.12.0+dev/openocd \
  -s ~/.pico-sdk/openocd/0.12.0+dev/scripts \
  -f interface/cmsis-dap.cfg -f target/rp2350.cfg \
  -c "adapter speed 5000"

# In another terminal, attach GDB
gdb-multiarch inav/build/inav_9.0.1_RP2350_PICO.elf \
  -ex "target remote localhost:3333" \
  -ex "monitor reset halt"
```

## See Also

- Raspberry Pi Debugprobe docs: https://www.raspberrypi.com/documentation/microcontrollers/debug-probe.html
- OpenOCD scripts: `~/.pico-sdk/openocd/0.12.0+dev/scripts/target/rp2350.cfg`
- For STM32 targets (F4/F7/H7): use DFU flashing instead — see `fc-flasher` agent and `.claude/skills/flash-firmware-dfu/`
