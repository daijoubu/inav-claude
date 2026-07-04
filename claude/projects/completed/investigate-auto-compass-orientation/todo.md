# Todo: Auto Compass Orientation Detection — Feasibility Investigation

## Phase 1: Read INAV Compass Calibration

- [ ] Read `src/main/sensors/compass.c` — understand calibration sample collection, fit logic, and where attitude is available
- [ ] Read rotation enum definition (likely `src/main/common/axis.h` or nearby) — list all ROTATION_* entries
- [ ] Compare INAV rotation set against ArduPilot ROTATION_MAX set — flag any gaps or extras

## Phase 2: Cost Estimation

- [ ] Estimate RAM cost: 300 samples × (int8_t roll + int8_t pitch + int8_t yaw) = ~900 bytes; confirm actual struct size
- [ ] Estimate flash cost: variance-minimisation loop over ~ROTATION_MAX (~24) candidates × 300 samples
- [ ] Check worst-case target (F4, smallest flash/RAM) — is budget available?

## Phase 3: Configurator UI Assessment

- [ ] Identify where calibration results are reported in configurator (`src/main/msp/msp.c` MSP side + configurator JS side)
- [ ] List new UI elements needed: orientation confidence score, detected orientation display, apply/reject prompt

## Phase 4: Write Recommendation

- [ ] Summarise findings for each of the 4 feasibility questions
- [ ] State go/no-go with rationale
- [ ] If go: sketch implementation phases and effort estimate
- [ ] Save findings as `investigation-findings.md` in project directory

## Completion

- [ ] All four feasibility questions answered
- [ ] `investigation-findings.md` written
- [ ] Completion report sent to manager
