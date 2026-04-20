# Todo: Fix Blackbox SD Card Lockup

## Phase 1: Investigation

- [ ] Use inav-architecture agent to find blackbox SD card code paths
- [ ] Trace initialization, write, and flush paths for blocking calls
- [ ] Identify SPI/SDIO bus operations that lack timeouts
- [ ] Check for infinite loops or unbounded retries
- [ ] Map the call chain from blackbox write to SD card driver

## Phase 2: Implementation

- [ ] Add timeouts to blocking SD card operations
- [ ] Add error handling for SD card init failures
- [ ] Add error handling for SD card write failures
- [ ] Ensure blackbox disables gracefully on failure
- [ ] Ensure FC continues normal operation when blackbox fails
- [ ] Bonus: Add OSD system message or error indication on blackbox failure

## Phase 3: Validation

- [ ] Build SITL
- [ ] Build at least one hardware target
- [ ] Review all changed code paths for correctness

## Completion

- [ ] Code compiles
- [ ] PR created against maintenance-9.x
- [ ] Completion report sent to manager
