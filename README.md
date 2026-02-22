# SalesForge Agent

> AI-powered sales intelligence pipeline that ingests raw leads, scores them with a transparent rubric, discovers similar companies via vector search, and generates personalized outreach — all from a single Elasticsearch conversation.

**Built for the [Elasticsearch Agent Builder Hackathon](https://elasticsearch.devpost.com/) ($20K prize pool)**

---

## The Problem

Sales teams waste 40% of their time on manual lead research, qualification, and outreach drafting. They jump between CRMs, LinkedIn, company databases, and email tools — piecing together information that should flow automatically. The result? Missed opportunities, generic outreach, and inconsistent lead scoring that varies from rep to rep.

## What SalesForge Does

SalesForge is not just a search agent — it's a **complete sales intelligence pipeline** that transforms raw lead data into ready-to-send personalized outreach.

```
100 Raw Leads → [Score Pipeline] → 25 Hot | 72 Warm | 3 Cold → [Outreach] → Personalized Emails
```

### The Pipeline

| Step | What Happens | Elastic Tech Used |
|------|-------------|-------------------|
| **1. Ingest** | Bulk-load leads with 1536-dim vector embeddings | Elasticsearch + OpenAI Embeddings |
| **2. Score** | Deterministic rubric scores all leads 0-100 across 4 dimensions | Elasticsearch Update API |
| **3. Discover** | ES\|QL analytics: industry breakdown, funding distribution, score statistics | **ES\|QL** with auto-generated charts |
| **4. Research** | Hybrid search (BM25 keyword + kNN vectors) finds the right leads | **Elasticsearch Search** (Hybrid) |
| **5. Compare** | Side-by-side lead comparison with transparent reasoning | **Agent Builder** multi-step chain |
| **6. Find Similar** | "Find me leads like this one" — pure vector similarity search | **kNN dense vector search** |
| **7. Generate** | Personalized outreach referencing specific company details | **Agent Builder** + LLM |
| **8. Log** | Every action recorded to audit trail index | **Elastic Workflows** (agent-actions-log) |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     SalesForge Agent                             │
│                  (Elastic Agent Builder)                         │
│                                                                  │
│  User: "Find my best leads for AI services"                     │
│                        │                                         │
│                        ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Multi-Step Reasoning Engine                  │   │
│  │                                                          │   │
│  │  Step 1: Pipeline Overview (ES|QL)                       │   │
│  │  Step 2: Hybrid Search (BM25 + kNN)                     │   │
│  │  Step 3: Score Analysis (deterministic rubric)           │   │
│  │  Step 4: Side-by-side Comparison                        │   │
│  │  Step 5: Personalized Outreach Generation               │   │
│  │  Step 6: Action Logging (audit trail)                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                        │                                         │
│           ┌────────────┼────────────┐                           │
│           ▼            ▼            ▼                           │
│  ┌─────────────┐ ┌──────────┐ ┌──────────────────┐            │
│  │   Search    │ │  ES|QL   │ │ Elastic Workflows │            │
│  │  (Hybrid)   │ │ Queries  │ │  (Score + Log)    │            │
│  └──────┬──────┘ └────┬─────┘ └────────┬─────────┘            │
│         │              │                │                       │
│  ┌──────▼──────────────▼────────────────▼───────────────────┐  │
│  │              Elasticsearch Indices                         │  │
│  │                                                           │  │
│  │  leads-raw (100 leads)     │  agent-actions-log (audit)  │  │
│  │  • Company data            │  • Action type               │  │
│  │  • 1536-dim vectors        │  • Timestamp                 │  │
│  │  • Scores (0-100)          │  • Score details             │  │
│  │  • Hot/Warm/Cold tiers     │  • Session tracking          │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | Elastic Agent Builder |
| Search | Hybrid Search (BM25 + kNN dense vectors, 1536-dim, cosine similarity) |
| Analytics | ES\|QL with auto-generated visualizations |
| Orchestration | Elastic Workflows (scoring pipeline + audit trail logging) |
| LLM | Claude Sonnet 4.5 (via Agent Builder connector) |
| Embeddings | OpenAI text-embedding-3-small (1536 dimensions) |
| Data Ingestion | Python + elasticsearch-py |
| Dashboard | Kibana (4-panel lead intelligence dashboard) |

---

## Scoring Rubric

Every lead gets a transparent, deterministic score (0-100) across 4 equally-weighted dimensions:

| Dimension | Max Points | What It Measures | Scoring Logic |
|-----------|-----------|-----------------|---------------|
| **Employee Count** | 25 | Market reach & deal size | 25 (1000+), 22 (250+), 18 (100+), 14 (50+), 10 (25+), 6 (10+), 3 (<10) |
| **Funding Stage** | 25 | Budget availability | 25 (Series C/Public), 22 (Growth), 20 (Series B), 15 (Series A), 10 (Seed), 8 (Bootstrapped), 5 (Pre-Seed) |
| **Industry Fit** | 25 | Alignment with AI/automation | 25 (SaaS/FinTech), 22-23 (Cybersecurity/MarTech), 16-18 (HealthTech/EdTech/E-Commerce), 8-12 (others) |
| **Description Quality** | 25 | Company sophistication signals | Length (2-8) + AI/tech keywords (2-10) + Enterprise/B2B signals (2-7) |

**Tiers:** Hot (75-100) → Immediate outreach | Warm (45-74) → Nurture sequence | Cold (0-44) → Archive

---

## Features

### Core Intelligence
- **Batch Scoring Pipeline** — Process 100+ leads in seconds with deterministic, reproducible scoring
- **Hybrid Search** — BM25 keyword + kNN semantic vectors find leads that keyword-only search misses
- **ES|QL Analytics** — Pipeline funnel, industry intelligence, score distribution, cross-tab analysis
- **Find Similar Leads** — "Find me more leads like this one" using pure vector similarity

### Agent Capabilities
- **Multi-Step Reasoning** — Chains discover → research → score → compare → generate → log in one conversation
- **Explainable Scoring** — Every score comes with a 4-dimension breakdown and reasoning
- **Side-by-Side Comparison** — Compare 2-3 leads with transparent pros/cons
- **Personalized Outreach** — Emails reference specific company details (industry, size, tech stack, funding)
- **Full Audit Trail** — Every agent action logged to `agent-actions-log` index

### Pipeline Stats (from 100 seeded leads)
```
Total Leads:  100
🔥 Hot:       25 (25%) — Ready for outreach
🟡 Warm:      72 (72%) — Nurture sequence
🔵 Cold:       3 (3%)  — Archive for review

Top Lead: Wang-Bass (SaaS, 2500 emp, Growth) — 94/100
Score Range: 34–94 | Avg: 64.7 | Median: 64
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Elasticsearch Cloud account ([free trial](https://cloud.elastic.co/registration?cta=hackathon))
- OpenAI API key (for embeddings — costs < $0.01 for 100 leads)

### 1. Clone & Install

```bash
git clone https://github.com/aiagentwithdhruv/salesforge-agent.git
cd salesforge-agent
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your Elastic Cloud credentials and OpenAI API key
```

### 3. Seed Data + Score Pipeline

```bash
# Step 1: Generate 100 leads with vector embeddings and index into Elasticsearch
python ingestion/seed_data.py

# Step 2: Score all leads with deterministic rubric (writes back to ES)
python ingestion/batch_score.py

# Step 3: View pipeline analytics
python ingestion/pipeline_analytics.py

# Step 4 (optional): Find leads similar to a company
python ingestion/find_similar.py "Wang-Bass"
python ingestion/find_similar.py --query "AI SaaS for enterprise teams"
```

### 4. Set Up Agent in Kibana

1. Open Kibana → **Agents** → Select **SalesForge**
2. Click **Edit** → Paste the system prompt from [`agent/system_prompt.md`](agent/system_prompt.md)
3. Select **Claude Sonnet 4.5** as the LLM
4. Start chatting:

```
"Show me the pipeline — how many Hot, Warm, and Cold leads do we have?"
"Find SaaS companies with AI automation for enterprise teams"
"Compare the top 3 Hot leads and recommend which to contact first"
"Generate a personalized outreach email for Wang-Bass"
"Show me all actions taken in today's session"
```

---

## Project Structure

```
salesforge-agent/
├── README.md
├── LICENSE                        # MIT License
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── ingestion/                     # Data pipeline scripts
│   ├── seed_data.py               # Generate & index 100 leads with embeddings
│   ├── batch_score.py             # Score all leads (deterministic rubric)
│   ├── pipeline_analytics.py      # ES|QL analytics dashboard
│   ├── find_similar.py            # Vector similarity search
│   ├── bulk_index.py              # Generic JSON bulk indexer
│   └── index_mappings.json        # Index field mappings (hybrid search)
├── agent/                         # Agent Builder configuration
│   ├── agent_config.json          # Agent definition
│   ├── system_prompt.md           # System prompt for Kibana
│   └── tools/                     # Custom tool definitions
│       ├── lead_scorer.json       # Scoring tool config
│       └── outreach_gen.json      # Email generation tool config
├── workflows/                     # Elastic Workflows (YAML)
│   ├── score_and_route.yml        # Score leads + route by tier
│   └── log_actions.yml            # Audit trail logging
├── esql/                          # ES|QL query templates
│   └── queries.md                 # 10 reusable ES|QL patterns
├── docs/                          # Documentation
│   ├── setup.md                   # Full setup guide
│   ├── architecture.md            # Technical architecture
│   ├── submission.md              # Devpost 400-word description
│   └── x_post.md                  # Social media posts
├── demo/                          # Demo materials
│   └── demo_script.md             # 3-min demo walkthrough
└── data/                          # Sample data
    └── sample_leads.json          # 10 sample leads (subset)
```

---

## Agent Builder Features Used

| Feature | How SalesForge Uses It |
|---------|----------------------|
| **Agent Builder** | Core reasoning engine — chains 6+ tool calls in one conversation |
| **Hybrid Search** | BM25 (keyword) + kNN (1536-dim vectors, cosine) for precise lead discovery |
| **ES\|QL** | Pipeline funnel, industry analytics, score distribution, cross-tab queries with auto-charts |
| **Elastic Workflows** | Batch scoring pipeline + audit trail logging to `agent-actions-log` index |

---

## What I Liked

The Agent Builder's native ES|QL integration is exceptional — the agent dynamically generates and executes analytical queries, then presents results as interactive visualizations without any custom frontend code. The built-in chart generation from ES|QL results made the demo significantly more compelling.

The hybrid search combining BM25 with dense vectors is powerful for sales intelligence — keyword search finds exact matches while vector search discovers semantically similar companies that wouldn't surface with keywords alone.

## Challenges

Configuring custom agents via the API required experimentation — the system prompt field isn't supported in the REST API, so agent customization happens through the Kibana UI. The hybrid search setup with dense vectors required careful index mapping design to support both keyword and semantic queries on the same field.

---

## Demo

[Watch the 3-minute demo →](#) *(link to be added)*

---

## Built By

**Dhruv** ([@aiwithdhruv](https://www.linkedin.com/in/aiwithdhruv/))
- Applied AI Engineer & Solutions Architect
- Multi-agent systems builder
- 200+ production automation workflows

---

## License

MIT License — see [LICENSE](LICENSE) for details.
