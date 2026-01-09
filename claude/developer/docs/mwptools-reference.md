# mwptools Reference for INAV Development

**Location:** `~/inavflight/mwptools/`
**Source:** https://codeberg.org/stronnag/mwptools
**Author:** Jonathan Hudson

mwptools is a suite of tools for INAV mission planning, ground control, and development/debugging. This document covers CLI tools useful for ground-testing flight controllers and INAV development.

## Installation Status

**Full mwptools build:** Requires newer Go (1.19+) and Vala compiler. Not currently installed.

**Ruby scripts (installed):** Blackbox analysis scripts are symlinked to `~/.local/bin/`:
- `inav-parse_bb_compass.rb` - Compass/heading analysis with SVG graphs
- `inav_states.rb` - Navigation state extraction
- `inav_gps_alt.rb` - GPS vs baro altitude comparison
- `inav_hw_status.rb` - Hardware status extraction
- `inav_modes.rb` - Flight mode extraction
- `inav_sats.rb` - Satellite count analysis
- `inav_heading.rb` - Heading analysis

**blackbox_decode:** Symlinked to `~/.local/bin/blackbox_decode`

**gnuplot:** Available for graph generation.

### To rebuild full mwptools (when dependencies available)

```bash
cd ~/inavflight/mwptools
~/.local/bin/meson setup _build --prefix=~/.local --strip
ninja -C _build install
```

Requires: valac, libgtk-4-dev, libshumate-dev, golang 1.19+

---

## Key CLI Tools for Development

### fc-get / fc-set - CLI Settings Manager

**Purpose:** Backup and restore INAV CLI settings (diff files).

**Usage:**
```bash
# Backup settings to file (auto-detects FC)
fc-get /tmp/my-settings.txt

# Restore settings from file
fc-set /tmp/my-settings.txt
```

**Options:**
- `-b, --baud` - Baud rate (default: 115200)
- `-d, --device` - Serial device (auto-detected if not specified)
- `-n, --no-back` - Don't create backup when restoring

**Workflow:**
1. Backup before firmware update: `fc-get /tmp/backup.txt`
2. Flash new firmware
3. Restore settings: `fc-set /tmp/backup.txt`
4. Original file is backed up with timestamp, then updated with current diff

---

### cliterm - Interactive CLI Terminal

**Purpose:** Terminal for interacting with INAV CLI. Auto-detects FC and enters CLI mode.

**Usage:**
```bash
# Basic usage (auto-detects device, enters CLI)
cliterm

# With specific device
cliterm -d /dev/ttyACM0

# GPS passthrough mode (for u-center or ublox-cli)
cliterm -g

# MSC mode (USB Mass Storage for SD card access)
cliterm -m

# SITL connection
cliterm -s   # Connects to localhost:5670
```

**Options:**
- `-b, --baud` - Baud rate (default: 115200)
- `-d, --device` - Serial device
- `-n, --noinit` - Don't auto-enter CLI
- `-m, --msc` - Reboot FC in Mass Storage mode
- `-g, -p, --gpspass` - GPS passthrough mode
- `-s, --sitl` - SITL mode (localhost:5670)
- `-f, --file` - Read commands from file

**Key bindings:**
- `Ctrl-D` - Quit CLI without saving
- `Ctrl-C` - Exit cliterm

---

### flashgo - Blackbox Flash Downloader

**Purpose:** Download blackbox logs from on-board flash (faster than configurator).

**Usage:**
```bash
# Check flash usage
flashgo -info

# Download to auto-generated filename
flashgo

# Download to specific file
flashgo -file my_log.TXT

# Download and erase flash
flashgo -erase

# Erase only (no download)
flashgo -only-erase

# Download entire flash (test mode)
flashgo -test
```

**Options:**
- `-dir` - Output directory
- `-file` - Output filename
- `-info` - Show flash info and exit
- `-erase` - Erase after download
- `-only-erase` - Erase only, no download
- `-test` - Download whole flash regardless of used state

**Performance:** ~52KB/s on VCP boards (5x faster than baud rate suggests).

---

### fcflash - Firmware Flasher

**Purpose:** Flash INAV firmware from command line (DFU or USB serial).

**Usage:**
```bash
# Auto-detect mode (DFU for /dev/ttyACM*, serial for /dev/ttyUSB*)
fcflash inav_8.0.0_MATEKF405SE.hex

# Rescue mode (FC already in bootloader via hardware button)
fcflash rescue /dev/ttyACM0 inav_8.0.0_MATEKF405SE.hex

# Full erase before flash
fcflash erase inav_8.0.0_MATEKF405SE.hex

# Specific baud rate (USB serial mode)
fcflash 921600 /dev/ttyUSB0 inav_8.0.0_MATEKF405SE.hex
```

**Requirements:**
- `dfu-util` for DFU mode
- `stm32flash` for USB serial mode
- `objcopy` (from gcc) for hex to bin conversion

---

### mspmplex - MSP Multiplexer

**Purpose:** Allow multiple MSP clients (mwp, configurator) to access one FC simultaneously.

**Location:** `src/samples/mspmplex/`

**Usage:**
```bash
# Start multiplexer (on machine connected to FC)
mspmplex -verbose 1

# Client 1: mwp connecting via UDP
mwp -d udp://localhost:27072

# Client 2: INAV Configurator connecting via UDP
# Connect to udp://hostname:27072
```

**Notes:**
- Requires INAV 8.0+ (uses MSPV2 flags)
- Up to 64 clients supported
- Configurator must be on different host than mspmplex

---

## Blackbox Analysis Tools

Located in `src/bbox-replay/`:

### inav-parse_bb_compass.rb
Analyze compass/heading from blackbox logs. Generates CSV and SVG graphs.

```bash
./inav-parse_bb_compass.rb --plot LOG00001.TXT
```

### inav_gps_alt.rb
Compare GPS vs baro vs position estimator altitude.

### inav_states.rb
Extract navigation state transitions from logs.

### inav_hw_status.rb
Extract hardware status from logs.

### replay_bbox_ltm.rb
Replay blackbox data as LTM telemetry for mwp visualization.

---

## CRSF Tools

Located in `src/samples/crsf/`:

### crsfparser (Rust)
Parse and display CRSF telemetry frames.

```bash
# Build
cd src/samples/crsf
cargo build --release

# Parse from file
./target/release/crsfparser capture.log

# Parse from serial
crsfparser < /dev/ttyUSB0

# Parse from UDP
nc -l -k -u -p 42042 | crsfparser
```

---

## Other Useful Tools

### dbg-tool
Display INAV debug messages (`MSP_DEBUGMSG`) in terminal. Useful for serial printf debugging.

See: https://codeberg.org/stronnag/dbg-tool

### ublox-cli / ublox-test
GPS testing and configuration tools for u-blox receivers.

### mwp-log-replay
Replay mwp log files for analysis.

---

## Quick Reference

| Tool | Purpose | Key Command |
|------|---------|-------------|
| `fc-get` | Backup CLI settings | `fc-get backup.txt` |
| `fc-set` | Restore CLI settings | `fc-set backup.txt` |
| `cliterm` | Interactive CLI | `cliterm` |
| `flashgo` | Download blackbox logs | `flashgo -info` |
| `fcflash` | Flash firmware | `fcflash firmware.hex` |
| `mspmplex` | MSP multiplexer | `mspmplex -verbose 1` |

---

## Comparison with Existing Tools

We already have `fc-cli.py` in `.claude/skills/flash-firmware-dfu/`. Key differences:

| Feature | fc-cli.py | mwptools |
|---------|-----------|----------|
| Language | Python | Vala/Go/Ruby |
| MSP Library | mspapi2 | Custom |
| CLI Settings | Single commands | Full diff backup/restore |
| Blackbox | Download only | Download + analysis |
| GPS passthrough | No | Yes (cliterm -g) |
| MSC mode | Yes | Yes (cliterm -m) |
| Multi-client | No | Yes (mspmplex) |

**Recommendation:** Use mwptools for:
- Full CLI settings backup/restore
- Blackbox analysis with graphs
- Multiple simultaneous MSP clients
- GPS configuration via passthrough
