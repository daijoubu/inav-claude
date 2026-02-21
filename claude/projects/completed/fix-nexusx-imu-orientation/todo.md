# Todo: Fix NEXUS-X IMU Orientation

## Implementation

- [ ] Read current alignment in `target/NEXUSX/target.h`
- [ ] Determine correct alignment constant (CW180_DEG is confirmed wrong — likely CW0_DEG)
- [ ] Update `IMU_ICM42605_ALIGN` to correct value
- [ ] Build NEXUSX target to verify it compiles
- [ ] Create PR against `maintenance-9.x`, reference issue #11325

## Completion

- [ ] PR created
- [ ] Send completion report to manager
