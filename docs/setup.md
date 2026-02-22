# SalesForge Agent — Setup Guide

## 1. Elastic Cloud Setup

### Create Free Trial
1. Go to https://cloud.elastic.co/registration?cta=hackathon
2. Sign up with email/Google
3. Create a new **Elasticsearch Serverless** project
4. Save these values to your `.env`:
   - `ELASTICSEARCH_URL` — the Elasticsearch endpoint
   - `ELASTICSEARCH_API_KEY` — create one in Kibana → Stack Management → API Keys
   - `KIBANA_URL` — your Kibana endpoint

### Create API Key
In Kibana:
1. Go to **Stack Management → API Keys**
2. Click **Create API Key**
3. Name: `salesforge-agent`
4. Set permissions:
```json
{
  "salesforge": {
    "cluster": ["all"],
    "indices": [
      {
        "names": ["leads-*"],
        "privileges": ["all"]
      }
    ]
  }
}
```
5. Copy the encoded API key to `.env`

---

## 2. Local Setup

```bash
# Clone
git clone https://github.com/aiagentwithdhruv/salesforge-agent.git
cd salesforge-agent

# Install Python dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Seed data
python ingestion/seed_data.py
```

---

## 3. Agent Builder Setup (in Kibana)

### Step 1: Open Agent Builder
1. In Kibana, go to **Machine Learning → AI Agent Builder**
2. Click **Create Agent**

### Step 2: Configure Agent
- **Name:** SalesForge Agent
- **Description:** AI sales intelligence agent for lead research, scoring, and outreach
- **System Prompt:** Copy from `agent/agent_config.json` → `system_prompt`

### Step 3: Add Tools

#### Built-in Tools (enable these):
- `platform.core.search` — Search leads index
- `platform.core.list_indices` — List available indices
- `platform.core.get_index_mapping` — View index structure
- `platform.core.get_document_by_id` — Fetch specific lead

#### ES|QL Tool:
Enable ES|QL so the agent can run structured queries against lead data.

#### Workflow Tools:
1. Import `workflows/score_and_route.yml` as a workflow tool
2. Import `workflows/log_actions.yml` as a workflow tool

### Step 4: Connect LLM
- Add your OpenAI API key (or use Elastic's built-in connector)
- Model: `gpt-4o` recommended for multi-step reasoning

### Step 5: Test
Ask the agent:
```
"Show me all SaaS companies in our leads database with more than 50 employees"
```

Then try multi-step:
```
"Research and score the top 10 FinTech leads, then generate outreach for the Hot ones"
```

---

## 4. Verify Everything Works

### Check data is indexed:
```bash
curl -X GET "$ELASTICSEARCH_URL/leads-raw/_count" \
  -H "Authorization: ApiKey $ELASTICSEARCH_API_KEY"
```

### Test hybrid search:
```bash
curl -X POST "$ELASTICSEARCH_URL/leads-raw/_search" \
  -H "Authorization: ApiKey $ELASTICSEARCH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "match": {
        "company_description": "AI automation platform"
      }
    },
    "size": 5
  }'
```

### Test ES|QL:
```bash
curl -X POST "$ELASTICSEARCH_URL/_query" \
  -H "Authorization: ApiKey $ELASTICSEARCH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "FROM leads-raw | STATS count = COUNT(*) BY industry | SORT count DESC"
  }'
```
