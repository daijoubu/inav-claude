# Todo: Fix Configurator Outputs Page Servo Index Offset

## Phase 1: Reproduce (bug fix)

- [ ] Configure a servo mixer with servos 1-4 starting at output S3
- [ ] Confirm Mixer page shows Servo 1-4 correctly
- [ ] Confirm Outputs page shows the same servos as Servo 2-5 (off by one)
- [ ] Confirm root cause — determine whether the two pages use different
      indexing bases, different source data, or the Outputs page has a
      simple labeling bug

## Phase 2: Implementation

- [ ] Fix the Outputs page (or whichever page is incorrect) so servo
      numbering matches the actual FC output assignment
- [ ] Ensure the fix doesn't break numbering for configs that don't start
      at a non-zero output offset

## Phase 3: Verify

- [ ] Confirm Mixer and Outputs pages now agree on servo numbering for the
      S3-start config
- [ ] Confirm numbering is still correct for a default config (servos
      starting at S1)

## Completion

- [ ] Code compiles
- [ ] Tests pass (if applicable)
- [ ] PR created
- [ ] Completion report sent to manager
