# Todo: Fix CRSF MSP Integer Overflow (#11209)

## Phase 1: Analysis

- [ ] Read issue #11209 for full context
- [ ] Locate `crsfDataReceive()` in `src/main/rx/crsf.c`
- [ ] Understand the code flow for MSP_REQ and MSP_WRITE handling
- [ ] Identify exact location of the vulnerable subtraction
- [ ] Verify the issue exists in current code

## Phase 2: Implementation

- [ ] Add bounds check: `if (crsfFrame.frame.frameLength < 4) break;`
- [ ] Place check before any `frameLength - 4` calculation
- [ ] Ensure both MSP_REQ and MSP_WRITE cases are protected
- [ ] Build firmware to verify no compile errors

## Phase 3: Testing

- [ ] Run existing unit tests (if any for CRSF)
- [ ] Consider adding unit test for malformed frame handling
- [ ] Test with SITL if possible

## Phase 4: PR Creation

- [ ] Create branch from maintenance-9.x
- [ ] Commit with descriptive message referencing #11209
- [ ] Create PR targeting maintenance-9.x
- [ ] Reference issue in PR description

## Completion

- [ ] Code compiles without warnings
- [ ] Tests pass
- [ ] PR created and linked to issue
- [ ] Send completion report to manager
