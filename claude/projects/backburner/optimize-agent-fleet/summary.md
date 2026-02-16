# Project: Agent Fleet Token Efficiency Optimization

**Status:** ⏸️ BACKBURNER
**Priority:** MEDIUM-HIGH
**Type:** Optimization / Infrastructure
**Created:** 2026-02-15
**Paused Since:** 2026-02-15
**Estimated Effort:** 16 hours (2 weeks)
**Assignee:** Developer

---

## Overview

Systematic optimization of the 14-agent fleet to reduce token consumption by 60-70%. Current analysis identifies three inefficient agents (inav-architecture, target-developer, aerodynamics-expert) consuming 2-3x more tokens than necessary, and optimization opportunities across the entire fleet.

---

## Problem

### Current State
- Agent fleet average: **12,500 tokens/call**
- Three agents consuming **20,000+ tokens/call** (2.5-3x baseline)
- Inefficiencies from:
  - Expensive models (Sonnet) for simple lookup tasks
  - No caching or indexing (repeated regeneration)
  - Bloated embedded knowledge bases
  - Inefficient tool invocation patterns

### Impact
- Monthly token consumption: ~600,000 tokens/month on agent operations
- Limits available budget for scaling agent usage
- Slows down interactive agent operations (151s average for inav-architecture vs 30s baseline)

---

## Solution

### Approach
Three-phase optimization:
1. **Phase 1 (Week 1):** High-impact, low-effort changes
   - Downgrade models (Sonnet → Haiku for lookups)
   - Build architecture/config indexes
   - Estimated savings: 40,000 tokens/call

2. **Phase 2 (Week 2):** Medium-impact, medium-effort changes
   - Implement lightweight query modes
   - Add caching layers
   - Optimize tool patterns
   - Estimated savings: 15,000 tokens/call

3. **Phase 3+ (Week 2+):** Monitoring & maintenance
   - Token usage dashboard
   - Prevent regressions
   - Document optimization patterns for future agents

---

## Target Metrics

### Agent-Specific Improvements

| Agent | Current | Target | Reduction |
|-------|---------|--------|-----------|
| inav-architecture | 26,325 | <5,000 | 85-92% |
| target-developer | ~18,000 | ~8,000 | 55-60% |
| aerodynamics-expert | ~20,000 | ~10,000 | 50-55% |
| inav-builder | ~12,000 | ~8,000 | 30-35% |
| Fleet Average | 12,500 | 4,000-6,000 | 60-70% |

### Success Criteria
- [ ] Fleet average reduced from 12,500 to 4,000-6,000 tokens
- [ ] inav-architecture: 85%+ reduction
- [ ] Zero functionality regression
- [ ] Monitoring dashboard deployed
- [ ] All optimizations documented

---

## Implementation

### Deliverables
1. Optimized agent implementations (7 agents modified)
2. Index files:
   - `inav-architecture-index.json`
   - `target-developer-board-index.json`
   - `msp-expert-message-index.json`
   - `settings-lookup-section-index.json`
3. Lightweight query mode implementations
4. Token usage monitoring dashboard
5. Agent optimization checklist for future agents
6. Implementation documentation

### Phases

**Phase 1: High-Impact Changes (7.5 hours)**
- [ ] Downgrade target-developer: Sonnet → Haiku (1 hour, 8,000 tokens)
- [ ] Downgrade aerodynamics-expert: Sonnet → Haiku (0.5 hour, 6,000 tokens)
- [ ] Downgrade inav-builder: Sonnet → Haiku (0.5 hour, 6,000 tokens)
- [ ] Build inav-architecture index (3 hours, 15,000 tokens)
- [ ] Build target-developer board config index (2 hours, 5,000 tokens)
- [ ] Validate with test queries (0.5 hour)

**Phase 2: Medium-Impact Changes (8.5 hours)**
- [ ] Implement lightweight query modes (2 hours, 5,000 tokens)
- [ ] Add caching to 3 agents (2 hours, 4,000 tokens)
- [ ] Optimize tool patterns (1.5 hours, 3,000 tokens)
- [ ] Build remaining indexes (msp, settings) (2 hours, 4,000 tokens)
- [ ] Output filtering implementations (1 hour, 2,000 tokens)

**Phase 3: Monitoring & Maintenance (4 hours)**
- [ ] Deploy token usage dashboard (2 hours)
- [ ] Document optimization patterns (1 hour)
- [ ] Create agent optimization checklist (1 hour)

---

## Analysis & Evidence

### Detailed Reports Generated
Developer has completed comprehensive analysis:
- `claude/developer/reports/inav-architecture-token-efficiency-analysis.md` (6,000 words)
- `claude/developer/reports/multi-agent-efficiency-analysis.md` (7,000 words)

### Key Findings

**Model Selection Issues:**
- target-developer, aerodynamics-expert, inav-builder use Sonnet model for lookup-only tasks
- Sonnet: 1,000-2,000 tokens/call overhead vs Haiku
- Potential savings: 20,000 tokens/session just from model downgrades

**No Caching/Indexing:**
- inav-architecture: regenerates answers repeatedly (30 tool invocations for simple query)
- target-developer: reads full target.h files instead of indexed lookups
- msp-expert: no MSP message lookup cache
- Potential savings: 25,000+ tokens/session from indexing

**Embedded Knowledge Bloat:**
- inav-architecture: 512 lines embedded (should be 50 lines + JSON)
- Knowledge bases could be external JSON for 15-20% token savings

---

## Why Backburner?

This project represents high-value work (60-70% token savings) but:
- **Not urgent:** Current token usage is manageable
- **Non-blocking:** No development work depends on this
- **Can defer:** Agent performance is acceptable
- **Strategic timing:** Better implemented when team has time to validate thoroughly

### Resume Triggers
This project should move to **active** when:
- [ ] Token budget becomes constrained
- [ ] Developer has capacity for optimization work
- [ ] Need to scale agent usage (more concurrent operations)
- [ ] Quarterly infrastructure optimization cycle

---

## Risks & Mitigation

### Risks
- **Low:** Model downgrades (Haiku fully capable for lookups)
- **Low:** Index building (improves accuracy and speed)
- **Medium:** Caching (requires invalidation strategy)

### Mitigation Strategies
1. Keep comprehensive mode as fallback for all agents
2. Implement cache TTL (24 hours minimum)
3. Gradual rollout with token monitoring throughout
4. Comprehensive test suite for each optimization
5. Zero-breaking-change policy (purely performance improvements)

---

## Related

**Proposal email:** `claude/developer/email/sent/2026-02-15-0000-proposal-agent-fleet-token-efficiency.md`

**Analysis reports:**
- `claude/developer/reports/inav-architecture-token-efficiency-analysis.md`
- `claude/developer/reports/multi-agent-efficiency-analysis.md`

**Token usage baseline:** `claude/metrics/token-usage.csv`

---

## Timeline

**Phase 1:** Week 1 (when resumed)
- Duration: 7.5 hours
- Savings: 40,000 tokens/call

**Phase 2:** Week 2 (when resumed)
- Duration: 8.5 hours
- Savings: 15,000 tokens/call (additional)

**Phase 3:** Week 2+ (when resumed)
- Duration: 4 hours
- Ongoing optimization: 5,000+ tokens/call

**Total:** 20 hours (16 hours dev + 4 hours validation/monitoring)

---

## Success Metrics

### Token Efficiency
- [ ] Fleet average: 12,500 → 4,000-6,000 tokens (60-70%)
- [ ] inav-architecture: 26,325 → <5,000 tokens (85%)
- [ ] Monthly savings: ~400,000+ tokens

### Quality
- [ ] Zero functionality regressions
- [ ] All agent outputs match pre-optimization quality
- [ ] No performance degradation for common queries

### Documentation
- [ ] Implementation guide for each optimization
- [ ] Agent optimization checklist for future agents
- [ ] Token monitoring dashboard deployed

---

## Notes

- **Priority:** This is valuable work that frees substantial token budget
- **Complexity:** Low to medium (mostly configuration and index building)
- **Risk:** Very low (all changes are optimization-only, no functionality changes)
- **ROI:** Excellent (20 hours of work saves 400,000+ tokens/month indefinitely)

When resumed, recommend starting with Phase 1 (highest impact, lowest risk).
