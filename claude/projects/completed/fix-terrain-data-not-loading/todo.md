# Todo: Fix Terrain Data Not Loading

## Phase 1: Investigation & Reproduction

- [ ] Use Chrome DevTools MCP to take snapshot of configurator
- [ ] Check console for JavaScript errors related to terrain
- [ ] Inspect network panel for terrain data API requests
- [ ] Identify terrain data source/endpoint being used
- [ ] Use test-engineer to navigate to map/mission view
- [ ] Document steps to reproduce the issue
- [ ] Verify what "terrain data doesn't load" means (error message? silent fail? UI issue?)

## Phase 2: Root Cause Analysis

- [ ] Analyze console errors (if any)
- [ ] Analyze network request failures (if any)
- [ ] Check if terrain data API endpoint has changed
- [ ] Verify terrain data service availability
- [ ] Check configurator settings for terrain feature
- [ ] Review recent commits for terrain-related changes
- [ ] Determine exact root cause

## Phase 3: Implementation

- [ ] Implement fix based on root cause
- [ ] Test fix with attached flight controller
- [ ] Verify terrain data loads successfully
- [ ] Verify no new console errors

## Phase 4: Completion

- [ ] Build configurator (if changes made)
- [ ] Test in development mode
- [ ] Create PR (if applicable)
- [ ] Document findings and solution
- [ ] Send completion report to manager
