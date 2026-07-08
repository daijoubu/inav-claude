# Project Proposal: Agent Fleet Token Efficiency Optimization

**Date:** 2026-02-15 | **From:** Developer | **To:** Manager | **Priority:** MEDIUM-HIGH

**Estimated Effort:** 16 hours (2 weeks)
**Estimated Savings:** 60-70% token reduction (~600,000 tokens/month)

## Executive Summary

Comprehensive analysis of all 14 project agents reveals significant inefficiency in 3 agents (inav-architecture, target-developer, aerodynamics-expert) and optimization opportunities across the fleet. Token usage review shows these agents consume 2-3x more tokens than necessary for their tasks.

**Problem:** Current agent fleet average ~12,500 tokens/call. Three agents alone consume 20,000+ tokens/call (26,325 for inav-architecture).

**Opportunity:** Implement caching, indexing, and model optimization to reduce fleet average to 4,000-6,000 tokens/call (60-70% reduction).

**Impact:** Monthly token savings of 600,000+ tokens, making room for more agent usage and complex tasks within budget.

## Detailed Findings

### Agent Efficiency Breakdown

**Inefficient (3 agents):**
- inav-architecture: 26,325 tokens/call (2.5-3x baseline)
- target-developer: ~18,000 tokens/call (2x baseline)
- aerodynamics-expert: ~20,000 tokens/call (2x baseline)

**Moderate (4 agents):** 10,000-15,000 tokens (acceptable, improvable)

**Efficient (4 agents):** 6,000-9,000 tokens (well-designed baseline)

### Root Causes

1. **Model Selection Issues** (Sonnet for lookup tasks)
   - target-developer, aerodynamics-expert, inav-builder use expensive model for simple lookups
   - Potential savings: 20,000 tokens/session

2. **No Caching/Indexing**
   - inav-architecture regenerates answers repeatedly
   - target-developer reads full config files for simple queries
   - Potential savings: 25,000+ tokens/session

3. **Embedded Knowledge Bloat**
   - inav-architecture: 512 lines embedded (should be 50 lines + JSON index)
   - Potential savings: 8,000 tokens/session

## Proposed Project

### Phase 1: High-Impact Changes (Week 1)
**Effort:** 7.5 hours | **Savings:** 40,000 tokens/call | **ROI:** Excellent

- Downgrade 3 agents from Sonnet to Haiku (1.5 hours, 20,000 tokens)
- Build inav-architecture index (3 hours, 15,000 tokens)
- Build target-developer board config index (2 hours, 5,000 tokens)

### Phase 2: Medium-Impact Changes (Week 2)
**Effort:** 8.5 hours | **Savings:** 15,000 tokens/call | **ROI:** Good

- Implement lightweight query modes
- Add caching layers to agents
- Optimize tool invocation patterns
- Output filtering for verbose operations

### Phase 3: Monitoring & Maintenance (Week 2+)
**Effort:** 4 hours | **Savings:** Ongoing optimization

- Set up token usage dashboard
- Prevent regressions
- Document optimization patterns for future agents

## Success Criteria

**Phase 1:**
- [ ] inav-architecture: 26,325 → <5,000 tokens (85% reduction)
- [ ] target-developer & aerodynamics-expert: downgraded and indexed
- [ ] Total savings: >40,000 tokens/call

**Phase 2:**
- [ ] All agents optimized
- [ ] Caching validated
- [ ] Total savings: >55,000 tokens/call

**Overall:**
- [ ] Fleet average: 12,500 → 4,000-6,000 tokens (60-70%)
- [ ] Monitoring dashboard live
- [ ] Zero functionality regression

## Deliverables

1. Optimized agent implementations (7 agents modified)
2. Index files (inav-architecture, target-developer, msp-expert, settings-lookup)
3. Token monitoring dashboard
4. Agent optimization checklist for future agents
5. Implementation documentation

## Detailed Reports

Developer has completed analysis and created two comprehensive reports:
- `claude/developer/reports/inav-architecture-token-efficiency-analysis.md` (6,000 words)
- `claude/developer/reports/multi-agent-efficiency-analysis.md` (7,000 words)

## Risks & Mitigation

**Risks:** Low
- Model downgrades are non-breaking (Haiku fully capable for lookups)
- Indexing is additive (improves accuracy)
- Caching includes TTL invalidation

**Mitigation:**
- Gradual rollout with validation tests
- Comprehensive mode kept as fallback
- Token monitoring throughout implementation

## Recommendation

Create project "optimize-agent-fleet" to systematically improve agent efficiency and free up substantial token budget for future capabilities.

**Start:** Immediately (recommend Phase 1 begins this week)
**Timeline:** 2 weeks for full implementation
**Effort:** 16 hours developer time
**Expected ROI:** 60-70% token savings (600,000+ tokens/month)

---
**Developer**
