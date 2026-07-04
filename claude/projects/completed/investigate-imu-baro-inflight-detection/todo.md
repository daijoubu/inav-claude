# Todo: Investigate IMU/Baro In-Flight Detection for Fixed-Wing

## Phase 1: Understand the Problem

- [ ] Read `isProbablyStillFlying()` — full implementation and all callers
- [ ] Trace `IN_FLIGHT_EMERG_REARM` path — confirm GPS dependency blocks it
- [ ] Document the exact circular dependency with code references

## Phase 2: Survey Existing Signals

- [ ] Check position estimator for any in-flight confidence or motion flags independent of GPS
- [ ] Check AHRS/IMU outputs — is acceleration magnitude, gyro rate, or attitude change rate available?
- [ ] Check baro — is altitude rate / vertical speed derivable independently of GPS?
- [ ] Note what signals are available during GPS outage specifically

## Phase 3: Evaluate Candidate Signals

- [ ] For each viable candidate: assess false-positive risk (ground turbulence, prop wash) and false-negative risk (glide, engine-off descent)
- [ ] Assess whether the right fix is in `isProbablyStillFlying()` or a separate check for `IN_FLIGHT_EMERG_REARM`
- [ ] Consider threshold tuning — what would "probably flying" mean in IMU/baro terms for fixed-wing?

## Phase 4: Write Recommendation

- [ ] Answer all four feasibility questions from the project summary
- [ ] Write `investigation-findings.md` in project directory
- [ ] State go/no-go with rationale
- [ ] If go: identify candidate signal(s) and sketch implementation approach

## Completion

- [ ] `investigation-findings.md` written
- [ ] Completion report sent to manager
