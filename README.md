# SalesForge Agent

> AI-powered sales intelligence agent that researches, scores, and generates personalized outreach for leads — built on Elasticsearch Agent Builder.

**Built for the [Elasticsearch Agent Builder Hackathon](https://elasticsearch.devpost.com/) ($20K prize pool)**

---

## What It Does

SalesForge Agent is a multi-step AI agent that transforms raw company data into actionable sales intelligence:

1. **Ingest** — Bulk-loads lead and company data into Elasticsearch with hybrid search (vector + keyword)
2. **Research** — Agent queries Elasticsearch to surface relevant company intel, news, and patterns
3. **Score** — Multi-step reasoning classifies leads as Hot/Warm/Cold with evidence-backed explanations
4. **Generate** — Creates personalized outreach emails using research context
5. **Log** — Records all agent actions via Elastic Workflows for full audit trail

### Why SalesForge?

Sales teams waste 40% of their time on lead research and manual scoring. SalesForge automates the entire intelligence pipeline — from raw data to ready-to-send outreach — with transparent, explainable AI reasoning at every step.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  SalesForge Agent                     │
│              (Elastic Agent Builder)                  │
│                                                       │
│  ┌─────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │ Search   │  │ ES|QL    │  │ Elastic Workflows  │  │
│  │ (Hybrid) │  │ Queries  │  │ (Score + Route)    │  │
│  └────┬─────┘  └────┬─────┘  └────────┬───────────┘  │
│       │              │                  │              │
│  ┌────▼──────────────▼──────────────────▼───────────┐│
│  │            Elasticsearch Indices                   ││
│  │  leads-raw │ leads-enriched │ agent-actions-log   ││
│  └────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | Elastic Agent Builder |
| Search | Elasticsearch Hybrid Search (BM25 + kNN vectors) |
| Query Language | ES|QL for structured lead analysis |
| Orchestration | Elastic Workflows (YAML-based) |
| LLM | Connected via Agent Builder (OpenAI / Anthropic) |
| Data Ingestion | Python + Elasticsearch client |
| Protocol | MCP (Model Context Protocol) for tool integration |

---

## Features

- **Hybrid Search** — Combines keyword matching with semantic vector search for precise lead discovery
- **Multi-Step Reasoning** — Agent chains research → analysis → scoring → generation in a single conversation
- **ES|QL Analytics** — Complex lead queries like "show me SaaS companies in fintech with >50 employees"
- **Explainable Scoring** — Every Hot/Warm/Cold classification comes with evidence and reasoning
- **Personalized Outreach** — Emails reference specific company details, not generic templates
- **Full Audit Trail** — Every agent action logged via Elastic Workflows
- **Bulk Processing** — Score hundreds of leads in batch mode

---

## Quick Start

### Prerequisites

- Python 3.10+
- Elasticsearch Cloud account ([free trial](https://cloud.elastic.co/registration?cta=hackathon))
- OpenAI or Anthropic API key (for LLM)

### 1. Clone & Install

```bash
git clone https://github.com/aiagentwithdhruv/salesforge-agent.git
cd salesforge-agent
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your Elastic Cloud credentials and LLM API key
```

### 3. Ingest Sample Data

```bash
python ingestion/seed_data.py
```

### 4. Set Up Agent in Kibana

Follow [docs/setup.md](docs/setup.md) for Agent Builder configuration.

### 5. Run the Agent

Open Kibana → Agent Builder → Select "SalesForge Agent" → Start chatting:

```
"Research and score the top 10 SaaS companies in our leads database"
```

---

## Project Structure

```
salesforge-agent/
├── README.md
├── LICENSE                    # MIT License
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── ingestion/                 # Data ingestion scripts
│   ├── seed_data.py           # Generate & index sample leads
│   ├── bulk_index.py          # Elasticsearch bulk indexer
│   └── index_mappings.json    # Index field mappings
├── agent/                     # Agent Builder configuration
│   ├── agent_config.json      # Agent definition for Kibana API
│   └── tools/                 # Custom tool definitions
│       ├── lead_scorer.json   # Scoring tool config
│       └── outreach_gen.json  # Email generation tool config
├── workflows/                 # Elastic Workflows (YAML)
│   ├── score_and_route.yml    # Score leads + route by tier
│   └── log_actions.yml        # Audit trail logging
├── esql/                      # ES|QL query templates
│   └── queries.md             # Reusable ES|QL patterns
├── docs/                      # Documentation
│   ├── setup.md               # Full setup guide
│   └── architecture.md        # Technical architecture
├── demo/                      # Demo materials
│   ├── demo_script.md         # 3-min demo walkthrough
│   └── screenshots/           # Demo screenshots
└── data/                      # Sample data
    └── sample_leads.json      # 100 synthetic leads
```

---

## Demo

[Watch the 3-minute demo →](#) *(link to be added)*

---

## Submission

- **Hackathon:** [Elasticsearch Agent Builder Hackathon](https://elasticsearch.devpost.com/)
- **Prize Pool:** $20,000
- **Deadline:** February 27, 2026

---

## Built By

**Dhruv** ([@aiwithdhruv](https://www.linkedin.com/in/aiwithdhruv/))
- AI Automation Engineer
- 200+ production n8n workflows
- Multi-agent systems architect

---

## License

MIT License — see [LICENSE](LICENSE) for details.
