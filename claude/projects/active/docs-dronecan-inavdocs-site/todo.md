# Todo: Contribute DroneCAN Documentation to inavdocs

## Phase 1: Setup

- [ ] Fork `iNavFlight/iNavFlight.github.io` under the project's own GitHub
      account
- [ ] Add the fork as a remote / point the local `inavdocs/` clone at it
      (currently tracks `robotgoat/inavdocs`, read-only reference)
- [ ] `npm install` and confirm `npm run build` / `npm run start` work
      locally (see repo README)

## Phase 2: Correctness Fix (already-shipped functionality)

- [ ] Branch off `master`
- [ ] Fix `docs/03-getting-started/01-hardware-overview.mdx` — remove/replace
      the "INAV does not support any DroneCAN based sensors yet" claim
- [ ] Add DroneCAN as a documented voltage/current source in
      `docs/05-core-features/battery.mdx`
- [ ] Add DroneCAN as a documented GPS source in `docs/05-core-features/gps.mdx`
- [ ] `npm run build` clean
- [ ] Open PR against `iNavFlight/iNavFlight.github.io` `master`

## Phase 3: New Feature-Stack Documentation (per firmware PR, as each lands)

For each of the following, hold off drafting until the corresponding
firmware PR is at least out of draft:

- [ ] Node management / health guard (PR #11698 area) — node status,
      health guard behavior, GPS/battery node-ID filtering
- [ ] Parameter get/set + node info + configurator DroneCAN tab (PR #11683
      + configurator #2671)
- [ ] DNA server (PR #11688 + configurator #2672)
- [ ] Actuator control / ESC control / RC input over CAN
      (`feature-dronecan-actuator-control`, `-esc-control`, `-rcinput` —
      not yet PR'd)
- [ ] CAN bus error blackbox logging (PR #11729)
- [ ] Once `fix-dronecan-cell-voltage-calculation` resolves: note correct
      cell-voltage behavior for a DroneCAN battery source in `battery.mdx`

## Completion

- [ ] At least the Phase 2 correctness-fix PR merged or under review
- [ ] Phase 3 tracked as follow-on work, not blocking this project's
      completion — reasonable to complete this project once Phase 2 ships
      and Phase 3's scope is documented/handed off
- [ ] Send completion report to manager
