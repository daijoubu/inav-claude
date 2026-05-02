# Todo: Investigate ITCM Headroom and DroneCAN ISR Migration

## Phase 1: Audit Current ITCM Usage

- [ ] Build MATEKF765SE and locate `.map` file
- [ ] Extract all symbols in `.itcm` / `.tcm_code` sections from map file
- [ ] Search source for `FAST_CODE`, `RAM_CODE`, ITCM section attributes
- [ ] Produce table: symbol → size → subsystem → reason

## Phase 2: Evaluate Relocation Candidates

- [ ] For each ITCM resident, assess whether it is truly latency-critical
- [ ] Identify any speculative or unjustified ITCM placements
- [ ] Estimate flash penalty for candidates on Cortex-M7 (ART accelerator context)

## Phase 3: DroneCAN ISR Size Estimate

- [ ] Review planned DroneCAN TX ISR design (from `feature-stm32f7-can-tx-isr`)
- [ ] Draft ISR handler pseudocode / prototype
- [ ] Estimate ITCM cost if handler placed in ITCM

## Phase 4: Recommendation Document

- [ ] Write `claude/developer/investigations/itcm-dronecan-isr-analysis.md`
- [ ] Issue recommendation: PROCEED / RELOCATE FIRST / REDESIGN
- [ ] Send findings report to manager

## Completion

- [ ] Analysis document complete
- [ ] Recommendation clearly stated
- [ ] `feature-stm32f7-can-tx-isr` team briefed on findings
- [ ] Send completion report to manager
