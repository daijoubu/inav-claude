# Todo List: Optimize Agent Fleet Token Consumption

## Phase 1: Measurement

- [ ] Baseline current token consumption per call for inav-architecture, target-developer, aerodynamics-expert
- [ ] Identify which parts of each agent's context are re-derived unnecessarily on every call

## Phase 2: Caching / Indexing

- [ ] Design caching strategy for repeated/similar queries
- [ ] Build lightweight index (vs. full-content load) for architecture and target lookups

## Phase 3: Model Selection Review

- [ ] Reassess whether each agent needs its current model tier

## Phase 4: Validation

- [ ] Re-measure token consumption post-change; confirm 60-70% reduction target
- [ ] Spot-check answer quality on representative queries for regressions

## Completion

- [ ] Document caching/indexing approach for future agents
- [ ] Send completion report to manager
