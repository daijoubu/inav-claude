# Todo: GitHub Action - PG Version Check

## Prerequisites

- [ ] Understand PG versioning rules from documentation project
- [ ] Review PR #11236 as test case
- [ ] Study GitHub Actions workflow syntax
- [ ] Review GitHub REST API for commenting

## Phase 1: Research & Planning

- [ ] Research GitHub Actions for PR diff analysis
  - [ ] Find actions that parse diffs
  - [ ] Determine best approach (gh CLI vs actions/github-script)
- [ ] Study existing INAV CI workflows
  - [ ] Review .github/workflows/ structure
  - [ ] Check existing permissions setup
- [ ] Define detection heuristics
  - [ ] List patterns that indicate struct changes
  - [ ] Define version increment detection regex
  - [ ] Plan false positive mitigation

## Phase 2: Detection Script Development

- [ ] Create `.github/scripts/check-pg-versions.sh`
- [ ] Implement file filtering
  - [ ] Get changed files from PR
  - [ ] Filter to .c and .h files only
  - [ ] Skip files without PG_REGISTER
- [ ] Implement struct change detection
  - [ ] Parse typedef struct definitions
  - [ ] Detect field additions (+ lines)
  - [ ] Detect field removals (- lines)
  - [ ] Detect field type changes
- [ ] Implement version check logic
  - [ ] Extract PG_REGISTER version number
  - [ ] Compare old vs new version
  - [ ] Detect when version should increment
- [ ] Implement comment generation
  - [ ] Format issue list
  - [ ] Include file locations
  - [ ] Add helpful recommendations
  - [ ] Link to documentation

## Phase 3: GitHub Action Workflow

- [ ] Create `.github/workflows/pg-version-check.yml`
- [ ] Configure trigger events
  - [ ] pull_request (opened)
  - [ ] pull_request (synchronize)
  - [ ] Target branches: maintenance-9.x, maintenance-10.x
- [ ] Set up permissions
  - [ ] pull-requests: write (for commenting)
  - [ ] contents: read (for checkout)
- [ ] Add checkout step
  - [ ] Use actions/checkout@v4
  - [ ] Set fetch-depth for diff access
- [ ] Add detection step
  - [ ] Run check-pg-versions.sh
  - [ ] Pass GitHub token
  - [ ] Pass PR number
- [ ] Implement comment posting
  - [ ] Use github.rest.issues.createComment
  - [ ] Or use gh CLI comment creation
  - [ ] Format markdown properly

## Phase 4: Testing

- [ ] Test on PR #11236 scenario
  - [ ] Create test branch with struct change
  - [ ] Remove version increment
  - [ ] Verify detection works
- [ ] Test version increment detection
  - [ ] Create test with proper version bump
  - [ ] Verify no false alarm
- [ ] Test PG_RESET_TEMPLATE-only changes
  - [ ] Modify default values only
  - [ ] Verify no false positive
- [ ] Test multiple PG changes in one PR
  - [ ] Modify 2-3 different PG structs
  - [ ] Verify all detected
- [ ] Test edge cases
  - [ ] Comment-only changes in struct
  - [ ] Whitespace changes
  - [ ] Macro-based field definitions

## Phase 5: Documentation & Integration

- [ ] Document the action
  - [ ] Create/update .github/workflows/README.md
  - [ ] Explain what it checks
  - [ ] Explain how to interpret warnings
  - [ ] Document false positive scenarios
- [ ] Add inline script comments
- [ ] Create PR to add the action
  - [ ] Include test results
  - [ ] Show examples of detection
  - [ ] Request review from maintainers

## Completion Checklist

- [ ] Workflow file created and tested
- [ ] Detection script handles common cases
- [ ] Comments are helpful and actionable
- [ ] False positive rate acceptable
- [ ] Documentation complete
- [ ] PR created for review
- [ ] Send completion report to manager

## Example Test Cases

### Test Case 1: Missing Version Increment (Should Detect)
```c
// Before
typedef struct blackboxConfig_s {
    uint16_t rate_num;
    uint16_t rate_denom;
    uint8_t device;
    uint8_t invertedCardDetection;  // REMOVED
    uint32_t includeFlags;
} blackboxConfig_t;
PG_REGISTER_WITH_RESET_TEMPLATE(..., 4);

// After (no version change)
typedef struct blackboxConfig_s {
    uint16_t rate_num;
    uint16_t rate_denom;
    uint8_t device;
    uint32_t includeFlags;
} blackboxConfig_t;
PG_REGISTER_WITH_RESET_TEMPLATE(..., 4);  // Still 4!
```
**Expected:** ⚠️ Warning comment posted

### Test Case 2: Proper Version Increment (Should Not Detect)
```c
// Same struct change but version bumped
PG_REGISTER_WITH_RESET_TEMPLATE(..., 5);  // Now 5!
```
**Expected:** ✅ No comment (change handled correctly)

### Test Case 3: Template-Only Change (Should Not Detect)
```c
// Struct unchanged
typedef struct blackboxConfig_s {
    uint16_t rate_num;
    uint16_t rate_denom;
    uint8_t device;
    uint32_t includeFlags;
} blackboxConfig_t;

// Only template defaults changed
PG_RESET_TEMPLATE(blackboxConfig_t, blackboxConfig,
-   .device = BLACKBOX_DEVICE_FLASH,
+   .device = BLACKBOX_DEVICE_SERIAL,
);
```
**Expected:** ✅ No comment (template changes don't need version bump)
