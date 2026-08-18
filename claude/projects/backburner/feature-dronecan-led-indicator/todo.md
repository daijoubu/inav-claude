# Todo List: DroneCAN LED Indicator Support

## Phase 1: Document + Failing Test

- [ ] Write user-facing documentation: how to enable DroneCAN light output
      (independent of / alongside onboard LED strip), how INAV
      indicator/LED state maps to `light_id` values, expected update
      rate/latency, and how the Configurator exposes this
- [ ] Write a failing test (SITL scenario or mocked CAN node) that exercises
      LED/indicator state → `indication.LightsCommand` broadcast end-to-end
- [ ] Write a failing test (or manual test plan, if firmware-only test
      infra can't cover it) confirming onboard WS2812 strip output is
      unaffected when DroneCAN light output is also enabled
- [ ] Confirm both tests fail for the right reason (feature not yet
      implemented, not a setup error)

## Phase 2: Implementation

- [ ] Add DroneCAN light output path: broadcast `indication.LightsCommand`
      from relevant `ledstrip.c` state (or a simplified indicator-state
      model, not full strip animation)
- [ ] Ensure onboard WS2812 strip output path is untouched/unaffected by
      DroneCAN light output being enabled — both must be independently
      togglable and usable simultaneously
- [ ] Add `light_id` mapping configuration (anti-collision, strobe, wing,
      logo, taxi, landing, etc.)
- [ ] Determine and implement appropriate broadcast rate
- [ ] Add CLI setting for enabling DroneCAN light output + `light_id`
      mapping, independent of existing LED strip CLI settings
- [ ] **Configurator:** add UI for enabling/disabling DroneCAN light output
      and configuring `light_id` mapping (evaluate DroneCAN tab vs LED
      strip tab as the right home — document the choice); wire up
      corresponding MSP settings if new ones are needed

## Phase 3: Verify

- [ ] Failing tests from Phase 1 now pass
- [ ] Behavior matches the documentation written in Phase 1
- [ ] Hardware-verify against a real DroneCAN light/LED node — confirm
      colors and `light_id` mapping are correct
- [ ] Hardware-verify onboard strip + DroneCAN lights together (both
      enabled) and each alone (only onboard, only DroneCAN) — confirm no
      cross-interference
- [ ] Configurator UI verified: enabling/disabling and mapping works, no
      regression to existing LED strip tab
- [ ] Full build matrix (F4/F7/H7/AT32/SITL) clean

## Completion

- [ ] Code compiles
- [ ] Tests pass
- [ ] PR created against correct base branch (check
      `.claude/skills/git-workflow/SKILL.md`) — firmware and, if UI changed,
      a corresponding inav-configurator PR
- [ ] Completion report sent to manager
