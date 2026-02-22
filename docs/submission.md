# SalesForge Agent — Hackathon Submission

## 400-Word Description (for Devpost)

### The Problem

Sales teams waste 40% of their time on manual lead research, qualification, and outreach drafting. They jump between CRMs, LinkedIn, company databases, and email tools — piecing together information that should flow automatically. The result? Missed opportunities, generic outreach, and inconsistent lead scoring that varies from rep to rep.

### What SalesForge Does

SalesForge is a multi-step AI agent built on Elasticsearch Agent Builder that automates the entire sales intelligence pipeline — from raw data to ready-to-send personalized outreach.

Given a database of leads, SalesForge can:

1. **Discover** — Analyze the entire lead database using ES|QL to surface industry breakdowns, company distributions, and patterns (with auto-generated visualizations)
2. **Research** — Use hybrid search (BM25 keyword + kNN vector similarity) to find companies matching specific criteria like "AI SaaS companies serving enterprise teams"
3. **Score** — Apply a transparent, deterministic scoring rubric (0-100) across four dimensions: employee count, funding stage, industry fit, and description quality. Every lead is classified as Hot, Warm, or Cold with full reasoning shown
4. **Generate** — Write personalized outreach emails that reference specific company details — industry, team size, tech stack, funding stage — never generic templates
5. **Explain** — Every decision comes with transparent reasoning and score breakdowns, creating a full audit trail

### Agent Builder Features Used

- **Hybrid Search** — Combines Elasticsearch's BM25 lexical matching with dense vector kNN search (1536-dim OpenAI embeddings) for precise lead discovery
- **ES|QL** — Structured analytics queries for industry breakdowns, funding distribution, and employee count analysis with auto-generated charts
- **Agent Builder Tools** — 8 tools including search, ES|QL execution, document retrieval, and index exploration
- **Multi-Step Reasoning** — The agent chains discover → research → score → generate → explain in a single conversation, making tool selection decisions autonomously

### What I Liked

The Agent Builder's native ES|QL integration is exceptional — the agent can dynamically generate and execute analytical queries, then present results as interactive visualizations without any custom frontend code. The built-in chart generation from ES|QL results was an unexpected bonus that made the demo significantly more compelling.

### Challenges

Configuring custom agents via the API required experimentation — the system prompt field isn't supported in the REST API, so agent customization had to happen through the Kibana UI. The hybrid search setup with dense vectors required careful index mapping design to support both keyword and semantic queries on the same field.

### Impact

SalesForge demonstrates how Elasticsearch can power intelligent, explainable sales automation — turning hours of manual research into seconds of AI-driven intelligence with full transparency.

---

**Built by Dhruv ([@aiwithdhruv](https://linkedin.com/in/aiwithdhruv)) using Elasticsearch Agent Builder, ES|QL, and Hybrid Search.**
