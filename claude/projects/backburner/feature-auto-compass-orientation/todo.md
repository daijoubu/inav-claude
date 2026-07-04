# Todo: Automatic Compass Orientation Detection

## Phase 0: Update project docs

- [ ] Confirm summary.md reflects PC-side calculation architecture (stream samples from FC, compute in configurator)

## Phase 1: Firmware (small)

- [ ] Find compass calibration tick in `compassUpdate()` / `compassCalibrate()` — identify where to hook sample emission
- [ ] Define new MSP message: attitude (Euler or quaternion) + raw mag vector per calibration tick
- [ ] Emit message only while calibration is in progress (`!compassIsCalibrationComplete()`)
- [ ] No sample buffer — emit and forget
- [ ] Build full matrix: F4, F7, H7, AT32, SITL — change should be small, all should be clean

## Phase 2: Configurator

- [ ] Identify magnetometer calibration flow in `inav-configurator/src/`
- [ ] Subscribe to new MSP sample stream during calibration; accumulate (attitude, mag) pairs
- [ ] After calibration completes, run variance-minimisation over 8 `sensor_align_e` orientations
- [ ] Display result: "Detected orientation: CW90_DEG_FLIP (confidence 6.2×)"
- [ ] Show guidance: ≥3× = reliable, <2× = ambiguous, report "indeterminate" if external alignment active
- [ ] "Apply detected orientation" button: sets `align_mag`, saves to FC

## Phase 3: Testing

- [ ] Physical bench test: compass mounted in wrong orientation → verify correct suggestion
- [ ] Physical bench test: compass in correct orientation → verify no false suggestion
- [ ] Verify no RAM regression on any target (no static buffer added)

## Completion

- [ ] PR opened against `maintenance-10.x` (firmware + configurator)
- [ ] Completion report sent to manager
