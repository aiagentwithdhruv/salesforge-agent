---
name: salesforge-agent
version: 1.0.0
description: AI sales intelligence pipeline with Elasticsearch — hackathon project ($20K prize pool)
author: AiwithDhruv
license: proprietary
tier: premium
last_verified: 2026-02-23
refresh_cadence: on-change
dependencies: []
platforms: [claude-code, cursor]
---

# SalesForge Agent — Agent Loadout

> AI-powered sales intelligence pipeline built for the Elasticsearch Agent Builder Hackathon ($20K prize pool). Ingests raw leads, scores with transparent rubric, discovers similar companies via hybrid search, generates personalized outreach.

---

## What's Included

| File | Type | Purpose |
|------|------|---------|
| `README.md` | Context | Full architecture, pipeline steps, tech stack |
| `agent/` | Code | Elastic Agent Builder code |
| `data/` | Knowledge | Sample lead data |
| `ingestion/` | Code | Data pipeline scripts |
| `requirements.txt` | Config | Python dependencies |

---

## Quick Reference

| Field | Value |
|-------|-------|
| **Hackathon** | Elasticsearch Agent Builder |
| **Prize Pool** | $20,000 |
| **Status** | BUILT, not deployed |
| **Agent** | Elastic Agent Builder |
| **Search** | Hybrid (BM25 + kNN vectors, 1536-dim) |
| **LLM** | Claude Sonnet 4.5 |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Dashboard** | Kibana |

### Pipeline
```
100 Raw Leads → [Score 0-100] → 25 Hot | 72 Warm | 3 Cold → [Hybrid Search] → [Outreach Generation]
```

### Scoring Rubric (4 Dimensions)
1. Employee Count (0-25)
2. Funding Stage (0-25)
3. Industry Match (0-25)
4. Description Quality (0-25)

---

## Self-Update Rules

| Event | Update | File |
|-------|--------|------|
| Hackathon result | Record prize/ranking | This file |
| Scoring rubric refined | Update rubric docs | `README.md` |
| New data ingested | Update data stats | This file |

---

## Changelog

### v1.0.0 (2026-02-23)
- Initial loadout from hackathon project
