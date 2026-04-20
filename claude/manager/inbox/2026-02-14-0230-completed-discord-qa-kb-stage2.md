# Task Completed: Discord Q&A Knowledge Base (Stage 2)

**Date:** 2026-02-14 02:30
**From:** Developer
**To:** Manager
**Type:** Completion Report

## Status: COMPLETED (v1)

## Summary

Built a tool that mines INAV Discord conversation history to discover recurring problems and their canonical answers. The pipeline extracts questions, clusters semantically similar ones (problems asked by different people in different words), ranks answers using a cross-encoder, and integrates INAV wiki content. Results are searchable via natural language query with FAISS vector search.

## Pipeline Architecture

7-stage pipeline:
1. **Data Preparation** — Load/merge/deduplicate extracted Discord messages (5,624 unique from 172 files)
2. **Question Detection** — Heuristic filter + zero-shot NLI classifier (cross-encoder/nli-deberta-v3-small), with helper user filtering
3. **Thread Reconstruction** — Reply chains + author continuation + @mentions + semantic similarity fallback
4. **Clustering** — HDBSCAN on MiniLM embeddings, with author diversity and coherence validation
5. **Answer Extraction** — Cross-encoder ranking (ms-marco-MiniLM-L-6-v2) + positive signal detection
6. **Wiki Integration** — 1,454 wiki sections embedded and matched to clusters
7. **Searchable KB** — SQLite database + FAISS index with CLI query tool

## Key Design Decisions

- **Helper detection**: Auto-identifies top posters (by message frequency) and filters their short diagnostic questions ("What version?"), which otherwise dominate clusters
- **Author diversity**: Requires >= 2 unique question askers per cluster — recurring problems come from different people
- **Max cluster size cap**: Clusters > 15 are rejected as too generic
- **Precision over recall**: High thresholds at every stage; abstains when no confident answer exists

## Results

- **77 recurring problem clusters** with answers
- **220 total recurring questions** clustered
- **71/77 clusters** matched to relevant wiki pages
- Query results show strong matches for real INAV problems (VTX config: 0.89 similarity, compass calibration: 0.92)

## Files Created

- `discord_bot/qa_pipeline.py` — Main pipeline script (build the knowledge base)
- `discord_bot/qa_query.py` — Query interface (search the knowledge base)
- `discord_bot/requirements.txt` — Python dependencies
- Output: `discord_bot/dump-2026-02-14/.../qa_knowledge_base.db` and `.faiss`

## Usage

```bash
# Build KB
HF_HOME=/tmp/hf_cache python3 qa_pipeline.py <extracted_dir> --wiki-dir <wiki_path>

# Query
HF_HOME=/tmp/hf_cache python3 qa_query.py <db_path> "your question"

# Interactive mode
HF_HOME=/tmp/hf_cache python3 qa_query.py <db_path> --interactive

# Dump all clusters
HF_HOME=/tmp/hf_cache python3 qa_query.py <db_path> --dump
```

## Known Limitations

- Dataset is small (~6k messages from cache) — more data will improve cluster quality
- Some clusters still have imperfect answer matches (cross-thread contamination)
- HF_HOME must be set to a writable directory (home .cache is read-only on this system)
- torch was upgraded to 2.10.0+cpu (from 1.8.0) to support current sentence-transformers

## Next Steps / Future Improvements

- Run on larger Discord export data (more conversations = better clusters)
- Add incremental update support (append new data without full rebuild)
- Fine-tune the NLI classifier on labeled INAV question data for better question detection
- Consider a verification LLM step for answer validation

---
**Developer**
