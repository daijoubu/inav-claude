# Todo: Document Parameter Group System

## Phase 1: Research & Understanding

- [ ] Read and understand `src/main/config/parameter_group.h`
  - [ ] Understand pgRegistry_t structure
  - [ ] Understand version storage (top 4 bits of pgn)
  - [ ] Understand registration macros
- [ ] Study PR #11236 changes
  - [ ] Understand what field was removed
  - [ ] Understand why version increment is required
  - [ ] Understand Pawel's comment
- [ ] Examine registration examples
  - [ ] blackbox.c - PG_REGISTER_WITH_RESET_TEMPLATE
  - [ ] Find profile config examples
  - [ ] Find array config examples
- [ ] Trace version validation
  - [ ] Find pgLoad() implementation
  - [ ] Understand version mismatch handling
- [ ] Check for existing PG documentation in inav/docs/development/

## Phase 2: Create Documentation Structure

- [ ] Create directory: `claude/developer/docs/parameter_groups/`
- [ ] Plan documentation organization
  - [ ] Main README.md outline
  - [ ] Supporting documents outline

## Phase 3: Write Core Documentation

- [ ] Write `README.md` - Main overview
  - [ ] What are parameter groups?
  - [ ] Why do they exist?
  - [ ] High-level architecture
  - [ ] Quick reference guide
- [ ] Write `versioning-rules.md`
  - [ ] When to increment versions
  - [ ] What happens on version mismatch
  - [ ] Version storage: 4-bit field (0-15 range)
  - [ ] What happens when version wraps from 15 to 0
  - [ ] Decision flowchart
  - [ ] Common mistakes
- [ ] Write `registration-guide.md`
  - [ ] PG_DECLARE vs PG_REGISTER
  - [ ] System vs Profile configs
  - [ ] With/without reset templates
  - [ ] Array configurations
- [ ] Write `case-study-pr11236.md`
  - [ ] The problem
  - [ ] Why version wasn't incremented
  - [ ] What breaks
  - [ ] The fix
  - [ ] Lessons learned

## Phase 4: Document Technical Details

- [ ] Document `__pg_registry_*` linker sections
  - [ ] How linker creates sections
  - [ ] PG_REGISTER_ATTRIBUTES mechanism
  - [ ] Iteration with PG_FOREACH
- [ ] Document settings.yaml relationship
  - [ ] How settings map to PG fields
  - [ ] Type system
  - [ ] Default values vs reset templates
  - [ ] Validation

## Phase 5: Review & Polish

- [ ] Verify all code examples are accurate
- [ ] Add cross-references to source files
- [ ] Ensure PR #11236 case study is clear
- [ ] Check for technical accuracy
- [ ] Proofread for clarity

## Completion

- [ ] Documentation complete and accurate
- [ ] Case study clearly explains version requirement
- [ ] All success criteria met
- [ ] Send completion report to manager
