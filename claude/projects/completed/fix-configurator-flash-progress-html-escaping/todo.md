# Todo: Fix Configurator Flash Progress Bar HTML Escaping

## Phase 1: Reproduce (bug fix)

- [ ] Trigger a failed firmware update in inav-configurator and confirm the
      raw `<span style="color:red">Failed</span>` markup is displayed as text
      instead of styled red "Failed" text
- [ ] Confirm root cause — identify whether the status text is inserted via
      a text-only API (`.text()`/`textContent`) where an HTML-interpreting
      API (`.html()`/`innerHTML`) is needed, or vice versa

## Phase 2: Implementation

- [ ] Fix the insertion method for the failure status message
- [ ] Check other progress bar states (success, in-progress, cancelled) for
      the same issue and fix if present

## Phase 3: Verify

- [ ] Confirm a failed flash now shows styled red "Failed" text
- [ ] Confirm related/adjacent status states render correctly and weren't
      broken by the fix

## Completion

- [ ] Code compiles
- [ ] Tests pass (if applicable)
- [ ] PR created
- [ ] Completion report sent to manager
