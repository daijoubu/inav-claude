# Todo: Investigate Bidirectional DShot Feasibility

## Phase 1: Analyze Betaflight Implementation

- [ ] Identify key source files for bidirectional DShot in ~/inavflight/betaflight/
  - [ ] DShot output driver (timer + DMA TX)
  - [ ] Bidirectional input capture (DMA RX after signal inversion)
  - [ ] GCR (Golay Coded Representation) decoding of ERPM response
  - [ ] GPIO pin direction switching (output → input → output per cycle)
- [ ] Document the data flow: motor command TX → pin flip → ESC response RX → GCR decode → ERPM value
- [ ] Note DMA channel requirements per motor (TX stream + RX stream? shared?)
- [ ] Note timer requirements (capture compare, input capture mode)
- [ ] Identify any PIO/hardware tricks BF uses (e.g., timer-triggered DMA, burst mode)

## Phase 2: Audit INAV DMA Usage

- [ ] Map all current DMA consumers in INAV:
  - [ ] Motor PWM/DShot output (existing unidirectional)
  - [ ] SPI (gyro, OSD, flash)
  - [ ] UART (GPS, receiver, telemetry)
  - [ ] ADC (battery, current, RSSI)
  - [ ] I2C (baro, mag — if DMA-driven)
  - [ ] LED strip
- [ ] Create DMA stream/channel map for key chips:
  - [ ] STM32F405 (2 DMA controllers, 8 streams each — most constrained)
  - [ ] STM32F722 (2 DMA controllers, 8 streams each)
  - [ ] STM32H743 (2 DMA controllers + MDMA + BDMA)
  - [ ] AT32F435 (2 DMA controllers)
- [ ] Identify free DMA streams on each chip family
- [ ] Check for DMA stream conflicts with bidirectional DShot requirements

## Phase 3: Feasibility Assessment

- [ ] Can bidir DShot fit within F405 DMA budget? (hardest case)
- [ ] Are there timer/DMA mapping conflicts on popular targets?
- [ ] Performance impact: does the RX DMA window overlap with gyro SPI DMA?
- [ ] Would INAV need to drop any existing DMA consumer to make room?
- [ ] Compare INAV vs BF DMA usage philosophy (INAV uses DMA for more peripherals)
- [ ] Write clear GO / NO-GO / PARTIAL recommendation

## Phase 4: Implementation Plan (if feasible)

- [ ] List specific INAV files to modify or create
- [ ] Describe required changes to timer and DMA infrastructure
- [ ] Identify which BF code can be ported vs. must be rewritten
- [ ] Estimate effort per phase
- [ ] Note any target-specific limitations (e.g., "works on H7/F7, not F4")
- [ ] Propose a phased rollout plan

## Completion

- [ ] Analysis report written
- [ ] Feasibility verdict documented
- [ ] Implementation plan (if feasible)
- [ ] Completion report sent to manager
