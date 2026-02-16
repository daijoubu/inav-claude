# Todo: Agent Fleet Token Efficiency Optimization

## Phase 1: High-Impact Changes (Week 1)

**Goal:** Reduce fleet average from 12,500 to 8,000-10,000 tokens (35-40% reduction)

### Model Downgrades (1.5 hours, 20,000 tokens savings)

- [ ] Downgrade target-developer: Sonnet → Haiku
  - [ ] Modify `.claude/agents/target-developer.md` model field
  - [ ] Test with 3 board configuration queries
  - [ ] Verify output quality matches pre-optimization

- [ ] Downgrade aerodynamics-expert: Sonnet → Haiku
  - [ ] Modify `.claude/agents/aerodynamics-expert.md` model field
  - [ ] Test with 3 aerodynamics questions
  - [ ] Verify source citations still accurate

- [ ] Downgrade inav-builder: Sonnet → Haiku
  - [ ] Modify `.claude/agents/inav-builder.md` model field
  - [ ] Test with simple builds (SITL, single target)
  - [ ] Verify error handling still effective

### Build inav-architecture Index (3 hours, 15,000 tokens savings)

- [ ] Create `inav-architecture-index.json` structure
  - [ ] Add common paths (PID, RTH, GPS, CRSF, navigation, etc.)
  - [ ] Add subsystem mappings
  - [ ] Add pattern references

- [ ] Build index content from codebase
  - [ ] Scan `inav/src/main/` directories
  - [ ] Extract key file locations
  - [ ] Map symbol → file relationships
  - [ ] Validate all paths exist

- [ ] Store index in agent directory
  - [ ] Location: `.claude/agents/inav-architecture/architecture-index.json`
  - [ ] Create agent subdirectory if needed

- [ ] Integrate index into agent
  - [ ] Modify agent to check index first
  - [ ] Keep full verification as fallback
  - [ ] Update "Quick Lookup" section in agent prompt

- [ ] Test with common queries
  - [ ] "Where is the PID controller?"
  - [ ] "Where is RTH logic?"
  - [ ] "How does navigation work?"
  - [ ] "Where is GPS driver?"
  - [ ] "What file handles CRSF telemetry?"
  - [ ] Verify 80%+ token reduction for indexed queries

### Build target-developer Board Config Index (2 hours, 5,000 tokens savings)

- [ ] Create `target-developer-board-index.json`
  - [ ] List all board directories
  - [ ] Extract key files (target.h, target.c, CMakeLists.txt)
  - [ ] Map MCU type → targets
  - [ ] Index common board names

- [ ] Build from `inav/src/main/target/` directory
  - [ ] Scan all board directories
  - [ ] Extract configuration details
  - [ ] Build quick lookup tables

- [ ] Store in agent directory
  - [ ] Location: `.claude/agents/target-developer/board-index.json`

- [ ] Integrate into agent
  - [ ] Modify agent to use index for quick lookups
  - [ ] Keep file reading as verification step

- [ ] Test with board queries
  - [ ] "What target.h settings exist on MATEKF405?"
  - [ ] "Which boards use STM32F405?"
  - [ ] "Show me the pin definitions for JHEMCUF435"
  - [ ] Verify 50-60% token reduction for indexed queries

### Validation

- [ ] All Phase 1 changes deployed
- [ ] Run token usage baseline on 10 invocations per agent
- [ ] Validate output quality (no regressions)
- [ ] Document actual vs estimated savings
- [ ] All tests passing

---

## Phase 2: Medium-Impact Changes (Week 2)

**Goal:** Reduce fleet average to 4,000-6,000 tokens (additional 30-40% reduction)

### Implement Lightweight Query Modes (2 hours, 5,000 tokens savings)

- [ ] inav-architecture lightweight mode
  - [ ] Detect query type (location vs explanation vs how-to)
  - [ ] Return minimal response for simple queries
  - [ ] Keep comprehensive mode as option

- [ ] target-developer lightweight mode
  - [ ] Quick answers for board lookups
  - [ ] Full context for complex troubleshooting

- [ ] inav-code-review lightweight mode
  - [ ] Skip file size limits check
  - [ ] Return findings only (no context)

- [ ] Test with mixed query types
  - [ ] Simple queries: verify <50% token reduction
  - [ ] Complex queries: verify comprehensive mode still available

### Add Caching Layers (2 hours, 4,000 tokens savings)

- [ ] Create cache structure in agent directories
  - [ ] Location: `.claude/agents/<agent>/cache/`
  - [ ] Implementation: JSON key-value store
  - [ ] TTL: 24 hours minimum

- [ ] Implement caching for:
  - [ ] inav-architecture: common path lookups
  - [ ] msp-expert: message definitions
  - [ ] target-developer: board configurations

- [ ] Cache invalidation strategy
  - [ ] Time-based TTL (24 hours)
  - [ ] Manual flush on code changes
  - [ ] Validation checksums

- [ ] Test caching
  - [ ] Same query twice: verify 2nd is cached (0 tools)
  - [ ] Check cache doesn't return stale data
  - [ ] Verify TTL expiration works

### Build Additional Indexes (2 hours, 4,000 tokens savings)

- [ ] msp-expert message index
  - [ ] Create `msp-message-index.json`
  - [ ] Map code → message name → details
  - [ ] Pre-cache common messages

- [ ] settings-lookup section index
  - [ ] Enhance existing section mapping
  - [ ] Create quick lookup by prefix
  - [ ] Cache section line ranges

### Optimize Tool Patterns (1.5 hours, 3,000 tokens savings)

- [ ] Combine Glob + Grep operations
  - [ ] Review tool invocation patterns
  - [ ] Replace sequential tools with combined operations
  - [ ] Test for accuracy

- [ ] Reduce Read() calls
  - [ ] Use Grep to find content before reading
  - [ ] Cache frequently-read files
  - [ ] Implement partial reads where possible

### Output Filtering (1 hour, 2,000 tokens savings)

- [ ] test-engineer output filtering
  - [ ] Filter verbose test output
  - [ ] Return summary metrics only
  - [ ] Keep failure details visible

- [ ] inav-code-review filtering
  - [ ] Summarize file changes
  - [ ] Focus on critical issues first
  - [ ] Defer non-critical findings

### Validation

- [ ] All Phase 2 changes deployed
- [ ] Run token usage baseline on 10 invocations per agent
- [ ] Validate caching works correctly
- [ ] Test lightweight modes don't lose functionality
- [ ] Document actual vs estimated savings

---

## Phase 3: Monitoring & Maintenance

**Goal:** Prevent regressions, enable future optimization

### Deploy Token Monitoring Dashboard (2 hours)

- [ ] Create metrics tracking
  - [ ] Capture tokens per agent per day
  - [ ] Track trend over time
  - [ ] Alert on regressions (>10% increase)

- [ ] Build dashboard
  - [ ] Location: `claude/metrics/agent-dashboard.md`
  - [ ] Display: tokens, tool uses, duration, trend
  - [ ] Update: daily (automated if possible)

- [ ] Documentation
  - [ ] How to read dashboard
  - [ ] When to investigate anomalies
  - [ ] Who to notify if regressions detected

### Document Optimization Patterns (1 hour)

- [ ] Create optimization guide
  - [ ] When to downgrade models
  - [ ] How to build indexes
  - [ ] Caching best practices
  - [ ] Tool optimization patterns

- [ ] Create agent optimization checklist
  - [ ] Apply to all future agents
  - [ ] Prevent new agents from being inefficient

### Create Future Agent Template (1 hour)

- [ ] Build optimized agent template
  - [ ] Efficient model selection
  - [ ] Built-in caching support
  - [ ] Index-first design
  - [ ] Lightweight mode default

### Completion

- [ ] All documentation merged to git
- [ ] Dashboard deployed and monitoring
- [ ] Team trained on new optimization standards
- [ ] Send completion report to manager

---

## Completion Checklist

### Quality Assurance
- [ ] All agents function identically to pre-optimization
- [ ] No output quality regression
- [ ] Performance improvements validated
- [ ] Security/safety not affected

### Testing
- [ ] Unit tests for each optimization
- [ ] Integration tests across agent interactions
- [ ] Token usage verified against estimates
- [ ] Load testing (concurrent agent calls)

### Documentation
- [ ] Each optimization documented with rationale
- [ ] Implementation guide for future work
- [ ] Agent optimization checklist created
- [ ] Token monitoring dashboard live

### Deployment
- [ ] All code changes committed
- [ ] PR created and reviewed
- [ ] Merged to main branch
- [ ] Monitoring active

### Reporting
- [ ] Completion report sent to manager
- [ ] Actual vs estimated savings documented
- [ ] Lessons learned captured
- [ ] Follow-up recommendations included
