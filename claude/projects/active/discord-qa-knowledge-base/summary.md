# Project: Discord Q&A Knowledge Base

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Tooling / AI Pipeline
**Created:** 2026-02-14
**Estimated Effort:** TBD (developer to propose after design)

## Overview

Build a tool that mines the INAV Discord conversation history (~20k messages) to discover **recurring problems** and their canonical answers. The goal is not simple Q&A extraction — it's recurring institutional knowledge mining. Problems that multiple people have encountered (expressed in different words) are the highest-value targets, because they will likely come up again.

The resulting tool may also incorporate information from the INAV wiki as an additional knowledge source.

## Key Design Principles

- **Precision over recall** — much better to return nothing than a wrong answer
- Must run within 4GB VRAM (some CUDA available) or CPU
- Focus on **recurring** problems, not one-off questions
- Discard low-confidence results at every stage

## Reference Material

- **Detailed pipeline research:** `discord_bot/chatgpt_convo.txt` — contains thorough analysis of pipeline architectures, model choices, clustering approaches, and confidence scoring strategies
- **INAV wiki:** `inavwiki/` — may be incorporated as additional knowledge source alongside Discord-mined Q&A

## Proposed Pipeline (from research)

1. **Question Detection** — classifier (deberta-v3-small or similar), high confidence threshold (0.9+)
2. **Semantic Embedding** — embed questions (bge-small-en or MiniLM)
3. **Cluster Recurring Problems** — HDBSCAN to find questions asked multiple times in different words; discard singletons
4. **Validate Clusters** — reject low-coherence clusters
5. **Extract Answers** — cross-encoder ranking per thread, compare answers across instances
6. **Build Canonical Answers** — summarize consistent answers; reject conflicting ones
7. **Confidence Scoring** — cluster size, answer consistency, OP feedback signals
8. **Searchable KB** — FAISS vector search, abstain if similarity below threshold

## Developer's Role

The developer should:
1. Read the research in `discord_bot/chatgpt_convo.txt`
2. Propose their own recommendations for the best implementation approach
3. Consider how INAV wiki content could be incorporated
4. Implement the tool

## Success Criteria

- [ ] Tool extracts recurring Q&A clusters from Discord cache/export data
- [ ] Results are high-precision (no wrong answers)
- [ ] Output is searchable via natural language query
- [ ] Runs within 4GB VRAM constraint
- [ ] INAV wiki integration considered/implemented
- [ ] Documented with usage instructions
