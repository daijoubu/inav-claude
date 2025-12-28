# INAV Firmware - Developer Guide

> **Maintainers:** Update this file when making architectural changes or adding major features.

## Overview

INAV is open-source flight controller firmware for STM32/AT32 microcontrollers. It supports multirotors, fixed-wing aircraft, rovers, and boats with advanced GPS navigation.

**Language:** C (C99)
**Targets:** STM32F4/F7/H7, AT32F43x
**Build System:** CMake + Make/Ninja

## Quick Start

building / compiling for testing: use the build-sitl skill

## Directory Structure

```
src/main/
├── main.c              # Entry point → init() → scheduler()
├── platform.h          # MCU family includes
├── fc/                 # Flight controller core
│   ├── fc_init.c           # Hardware initialization sequence
│   ├── fc_core.c           # Main control loop
│   ├── fc_msp.c            # MSP protocol handler (largest file)
│   ├── fc_tasks.c          # Task definitions
│   ├── cli.c               # Command-line interface
│   └── runtime_config.h    # Feature flags, flight modes
├── flight/             # Flight control algorithms
│   ├── pid.c               # PID controllers
│   ├── mixer.c             # Motor/servo mixing
│   ├── imu.c               # Sensor fusion
│   └── failsafe.c          # Safety systems
├── navigation/         # GPS navigation (largest subsystem)
│   ├── navigation.c        # Core navigation logic
│   ├── navigation_fixedwing.c
│   ├── navigation_multicopter.c
│   └── navigation_pos_estimator.c
├── sensors/            # Sensor processing
│   ├── gyro.c, acceleration.c, barometer.c, compass.c
│   └── battery.c, pitotmeter.c, opflow.c
├── drivers/            # Hardware abstraction
│   ├── accgyro/            # IMU drivers (MPU6000, ICM42xxx, BMI270)
│   ├── barometer/          # Baro drivers (BMP280, MS5611, DPS310)
│   ├── compass/            # Mag drivers (HMC5883, QMC5883)
│   ├── bus.c               # I2C/SPI bus management
│   └── pwm_output.c        # Motor/servo PWM
├── rx/                 # Receiver protocols
│   ├── rx.c, crsf.c, sbus.c, fport.c, ibus.c
├── telemetry/          # Telemetry output
│   ├── mavlink.c, smartport.c, crsf.c, ltm.c
├── msp/                # MSP protocol definitions
├── blackbox/           # Flight logging
├── programming/        # Logic conditions scripting
├── config/             # Settings system (EEPROM storage)
├── common/             # Utilities (math, filters, CRC)
├── scheduler/          # Task scheduler
└── target/             # Board configs (210+ targets)
    └── MATEKF405/
        ├── target.h        # Pin definitions
        ├── target.c        # Board init
        └── config.c        # Default settings
```

## Architecture

### Control Loop Flow
```
Sensors → IMU Fusion → PID Controllers → Mixer → PWM Output
   ↑                                              ↓
Scheduler (8kHz gyro, 100Hz nav, 10Hz GPS)    Motors/Servos
```

### Key Subsystems

1. **Scheduler** (`scheduler/`): Priority-based task execution for real-time control
2. **MSP Protocol** (`msp/`, `fc/fc_msp.c`): Configurator communication
3. **Parameter Groups** (`config/`): Dynamic settings stored in EEPROM/Flash
4. **Navigation** (`navigation/`): Position estimation, waypoint following, RTH

## Unit Testing

```bash
mkdir testing && cd testing
cmake -DTOOLCHAIN= ..       # Empty toolchain = native build
make check                   # Run all tests
./src/test/unit/time_unittest   # Run single test
```

Tests use Google Test framework. See `src/test/unit/`.

## Adding a New Board Target

1. Create `src/main/target/MYBOARD/`
2. Define pins/sensors in `target.h`
3. Add initialization in `target.c`
4. Set defaults in `config.c`
5. Add to CMakeLists.txt

## Adding a New Sensor Driver

1. Create driver in `drivers/<type>/<sensor>.c`
2. Add detection in `sensors/<type>.c`
3. Register in sensor init chain
4. Add MSP handlers if needed (`fc/fc_msp.c`)

## Code Style

See [Development.md](docs/development/Development.md):
- Methods returning bool should be questions: `isOkToArm()`
- Methods with `find*` can return null; `get*` should not
- Keep methods short and testable
- Avoid noise-words in variable names

## Do not
- Do not create a claude/ directory here in inav/ . The claude directory is ../calude/ from here

## Key Files by Size

| File | Purpose |
|------|---------|
| `fc/fc_msp.c` | MSP protocol (~166KB) |
| `navigation/navigation.c` | Core navigation (5400 lines) |
| `flight/pid.c` | PID controllers (1500 lines) |
| `fc/fc_core.c` | Main control loop (1100 lines) |

## Resources

- [Building Guide](docs/development/Building%20in%20Linux.md)
- [Development Guide](docs/development/Development.md)
- [Contributing](docs/development/Contributing.md)
- [INAV Wiki](https://github.com/iNavFlight/inav/wiki)
- [INAV Discord](https://discord.gg/peg2hhbYwN)
