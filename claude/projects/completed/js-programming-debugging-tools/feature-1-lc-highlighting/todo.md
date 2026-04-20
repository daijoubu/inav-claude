# Todo: Feature 1 - Active LC Highlighting

**Status:** 📋 TODO
**Estimated Effort:** 3-4 hours

---

## Phase 1: Setup & Investigation (30 min)

- [ ] Read decompiler code to understand LC → line mapping
- [ ] Identify where mapping is created during decompilation
- [ ] Confirm mapping data structure and format
- [ ] Review CodeMirror gutter API documentation
- [ ] Check existing Programming tab MSP query for active LCs

---

## Phase 2: Expose LC → Line Mapping (45 min)

- [ ] Modify decompiler to store LC → line mapping
- [ ] Create data structure to hold mapping
- [ ] Ensure mapping updates when code is regenerated
- [ ] Add accessor method to retrieve mapping
- [ ] Test mapping creation with sample LCs

---

## Phase 3: Implement Gutter Markers (1.5-2h)

### CodeMirror Setup

- [ ] Define custom gutter for LC status
- [ ] Add gutter to editor configuration
- [ ] Create CSS styles for gutter markers
- [ ] Design/add green checkmark icon

### Marker Update Logic

- [ ] Create function to update gutter markers
- [ ] Query MSP for active LCs (use existing mechanism)
- [ ] Look up editor lines for active LCs using mapping
- [ ] Clear old markers
- [ ] Add new markers for active LCs
- [ ] Handle edge cases (no active LCs, invalid mapping)

### Integration with Update Loop

- [ ] Hook into existing MSP update cycle
- [ ] Update markers at same frequency as Programming tab
- [ ] Ensure efficient updates (only change when needed)
- [ ] Test performance with multiple active LCs

---

## Phase 4: Testing (45 min - 1h)

### Basic Functionality

- [ ] Create test LC with simple condition
- [ ] Verify marker appears when condition is true
- [ ] Change FC state to make condition false
- [ ] Verify marker disappears

### Compound Conditions

- [ ] Test with AND condition (a && b)
- [ ] Test with OR condition (a || b)
- [ ] Verify entire condition line gets marker

### Multiple Active LCs

- [ ] Create 3-5 Logic Conditions
- [ ] Activate different combinations
- [ ] Verify all markers display correctly

### Edge Cases

- [ ] Switch to different tab and back
- [ ] Disconnect from FC
- [ ] Regenerate code (verify mapping updates)
- [ ] Test with empty/no LCs

### Performance

- [ ] Monitor for UI lag or flicker
- [ ] Check marker update frequency
- [ ] Verify no memory leaks (markers properly cleared)

---

## Phase 5: Polish & Documentation (15-30 min)

- [ ] Code review for quality
- [ ] Add code comments
- [ ] Ensure consistent code style
- [ ] Test on different screen sizes
- [ ] Verify visual design is clean

---

## Completion

- [ ] All tests passing
- [ ] Code reviewed and polished
- [ ] No performance issues
- [ ] Visual design approved
- [ ] Ready for PR (if desired) or move to Feature 2
- [ ] Send completion report to manager

---

## Notes

- This feature is independent of Features 2 and 3
- Can be implemented and tested standalone
- Should integrate cleanly with existing Programming tab
- Focus on clean, efficient implementation

---

**Next:** Feature 2 - Code Sync Status (2h)
