# Todo: Fix Magnetometer GUI_control Reference Error

## Phase 1: Investigation

- [ ] Check out `maintenance-9.x` branch in inav-configurator
- [ ] Navigate to Magnetometer tab and reproduce the error
- [ ] Read `tabs/magnetometer.js` around line 653
- [ ] Find where `GUI_control` is defined (likely `js/gui.js`)
- [ ] Check how other tabs properly reference `GUI_control`
- [ ] Identify the root cause (missing import, scope issue, load order)

## Phase 2: Fix Implementation

- [ ] Add proper import/require for `GUI_control` if missing
- [ ] OR adjust code to use correct scope/reference
- [ ] Test magnetometer tab loads without errors
- [ ] Verify 3D visualization initializes correctly
- [ ] Check browser console for any remaining errors

## Phase 3: Verification

- [ ] Test all other tabs still work correctly
- [ ] Verify fix follows configurator module patterns
- [ ] Check if `feature-gps-preset-ui` branch needs same fix
- [ ] Run any existing configurator tests

## Phase 4: Pull Request

- [ ] Create branch from `maintenance-9.x`
- [ ] Commit fix with descriptive message
- [ ] Create PR targeting `maintenance-9.x`
- [ ] Document the root cause in PR description
- [ ] Send completion report to manager
