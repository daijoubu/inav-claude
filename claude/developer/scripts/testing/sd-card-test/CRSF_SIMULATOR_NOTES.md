# CRSF Simulator - Paused

## Status: Waiting for FTDI adapter

## Background

The F765/H743 arming lockup issue appears to only reproduce when using CRSF receiver (which pilots use), not over USB-VCP.

## What Was Done

1. Created CRSF frame simulator (`crsf_simulator.py`)
2. Created context manager for CRSF testing (`crsf_context.py`)
3. Updated test suite to support CRSF simulation via `--crsf-port` flag

## Next Steps

When FTDI adapter is available:

1. Connect FTDI to FC UART6 (or configured CRSF UART)
2. Run tests with CRSF simulation:
   ```bash
   python sd_card_test.py /dev/ttyACM0 --tests 8 \
       --crsf-port /dev/ttyUSB0 \
       --crsf-rate 150 \
       --attempts 50
   ```

3. Compare results with vs without CRSF simulation

## Hypothesis

If bug reproduces with CRSF but not USB:
- UART interrupts interfere with SDIO in some way
- Points to interrupt priority or timing issue
- DMA priority change (LOW vs VERY_HIGH) in HAL driver may be relevant

If bug still doesn't reproduce:
- Issue may be specific to particular SD card
- May need actual CRSF hardware (not just simulated frames)
- May need specific timing windows we can't simulate

## Files

- `claude/developer/scripts/testing/hitl/crsf_simulator.py` - Frame generator
- `claude/developer/scripts/testing/hitl/crsf_context.py` - Context manager
- `sd_card_test/main.py` - Updated with CRSF options
