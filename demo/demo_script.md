# SalesForge Agent — 3-Minute Demo Script

**Target:** Under 3 minutes. Show multi-step reasoning, all 3 required tools (Search + ES|QL + Workflows).

---

## Intro (15 sec)

> "SalesForge is an AI agent that turns raw lead data into actionable sales intelligence. It researches, scores, and writes personalized outreach — all powered by Elasticsearch."

*Show: Kibana Agent Builder with SalesForge loaded*

---

## Demo Step 1: Data Overview (20 sec)

**Prompt to agent:**
> "How many leads do we have? Show me a breakdown by industry."

*Agent uses ES|QL:*
```
FROM leads-raw | STATS count = COUNT(*) BY industry | SORT count DESC
```

*Show: Table of industries with counts*

> "100 leads across 15 industries. Let's find the best ones."

---

## Demo Step 2: Hybrid Search (30 sec)

**Prompt to agent:**
> "Find SaaS companies that do AI-powered automation for enterprise teams"

*Agent uses hybrid search — keyword match on "SaaS" + vector similarity on "AI-powered automation for enterprise"*

*Show: Results with relevance scores, company details*

> "Notice how hybrid search combines exact keyword matching with semantic understanding — it finds companies even when they don't use the exact words."

---

## Demo Step 3: Multi-Step Scoring (45 sec)

**Prompt to agent:**
> "Score the top 5 results and tell me which ones are hot leads"

*Agent chains:*
1. Gets each lead's full details (Search)
2. Calls `score_and_route` workflow for each (Workflow)
3. Returns table with scores + reasoning

*Show: Agent's multi-step reasoning visible in the chat*

> "Each lead gets a transparent score — employee count, funding stage, industry fit — no black box. Three scored Hot, two Warm."

---

## Demo Step 4: Personalized Outreach (40 sec)

**Prompt to agent:**
> "Generate a personalized outreach email for the highest-scoring hot lead. I'm Dhruv from AIwithDhruv, offering AI automation services."

*Agent:*
1. Fetches lead details
2. References specific company attributes (industry, size, tech stack)
3. Generates personalized email
4. Logs the action via workflow

*Show: The generated email with highlighted personalization*

> "Not a template — the email references their specific industry, company size, and tech stack."

---

## Demo Step 5: Audit Trail (20 sec)

**Prompt to agent:**
> "Show me all actions taken on this lead"

*Agent uses ES|QL to query agent_actions:*

*Show: Timeline of researched → scored → outreach_generated*

> "Every action is logged. Full transparency for compliance and team handoffs."

---

## Closing (10 sec)

> "SalesForge: research, score, and personalize outreach — all from a single conversation in Elasticsearch Agent Builder. Built with hybrid search, ES|QL, and Elastic Workflows."

*Show: GitHub repo URL + X post*

---

## Total: ~3:00

### Recording Tips:
- Use Kibana in full screen, dark mode
- Zoom into agent responses
- Pre-load data so responses are fast
- Record with OBS or QuickTime
- Add captions in post if time allows
