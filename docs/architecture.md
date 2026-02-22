# SalesForge Agent — Architecture

## Overview

SalesForge is a multi-step AI agent built on Elasticsearch Agent Builder that automates the sales intelligence pipeline: research → score → outreach.

```
┌──────────────────────────────────────────────────────────────┐
│                      USER / SALES REP                         │
│  "Research fintech leads and generate outreach for hot ones"  │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    ELASTIC AGENT BUILDER                       │
│                                                                │
│  ┌─────────────┐                                              │
│  │ System       │  Multi-step reasoning engine that:          │
│  │ Prompt +     │  1. Parses user intent                      │
│  │ LLM (GPT-4o) │  2. Plans tool sequence                    │
│  │              │  3. Executes tools                          │
│  │              │  4. Synthesizes results                     │
│  └──────┬───────┘                                              │
│         │                                                      │
│         │ TOOL CALLS                                           │
│         ▼                                                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    TOOL LAYER                             │ │
│  │                                                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐ │ │
│  │  │ Search   │  │ ES|QL    │  │ Elastic Workflows      │ │ │
│  │  │ (Hybrid) │  │ Queries  │  │                        │ │ │
│  │  │          │  │          │  │ • score_and_route      │ │ │
│  │  │ • BM25   │  │ • Stats  │  │ • log_actions          │ │ │
│  │  │ • kNN    │  │ • Filter │  │                        │ │ │
│  │  │ • Filter │  │ • Agg    │  │                        │ │ │
│  │  └────┬─────┘  └────┬─────┘  └───────────┬────────────┘ │ │
│  └───────┼──────────────┼───────────────────┼──────────────┘ │
│          │              │                    │                 │
└──────────┼──────────────┼────────────────────┼────────────────┘
           │              │                    │
           ▼              ▼                    ▼
┌──────────────────────────────────────────────────────────────┐
│                    ELASTICSEARCH                              │
│                                                                │
│  Index: leads-raw                                             │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Fields:                                                  │  │
│  │ • company_name, industry, employee_count (structured)   │  │
│  │ • company_description (text, analyzed)                   │  │
│  │ • company_description_vector (dense_vector, 1536d)      │  │
│  │ • score, score_tier, score_reasoning (computed)          │  │
│  │ • outreach_email (generated)                             │  │
│  │ • agent_actions (nested audit log)                       │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

### Step 1: Ingest (seed_data.py / bulk_index.py)
- Generate or load lead data
- Create vector embeddings via OpenAI text-embedding-3-small
- Bulk index into `leads-raw` with hybrid mappings

### Step 2: Research (Agent → Search tool)
- User asks about leads → Agent uses hybrid search
- BM25 for keyword matching (industry, company name)
- kNN for semantic search (company description similarity)
- Results returned to agent for reasoning

### Step 3: Score (Agent → score_and_route workflow)
- Agent calls scoring workflow per lead
- Deterministic rubric: employees + funding + industry + description
- Returns: score (0-100), tier (Hot/Warm/Cold), reasoning
- Updates lead document in Elasticsearch

### Step 4: Generate Outreach (Agent → LLM reasoning)
- Agent reads scored lead details from Elasticsearch
- Uses LLM to generate personalized email
- References specific company attributes
- Stores generated email in lead document

### Step 5: Log (Agent → log_actions workflow)
- Every step logged as nested action in the lead document
- Full audit trail: who, what, when
- Enables analytics on agent productivity

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Hybrid search (BM25 + kNN) | Best of both: precise keyword + fuzzy semantic matching |
| Deterministic scoring rubric | Reproducible, explainable scores (not black-box LLM scoring) |
| Elastic Workflows for scoring | Separates scoring logic from LLM, more reliable |
| Nested agent_actions | Full audit trail without separate index |
| Single index design | Simpler for hackathon; production would split enriched data |
