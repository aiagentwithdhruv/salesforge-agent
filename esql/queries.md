# SalesForge — ES|QL Query Templates

Reusable ES|QL queries for the SalesForge Agent. These are registered as tools
in the Agent Builder so the agent can dynamically query lead data.

---

## Lead Discovery Queries

### Find leads by industry
```esql
FROM leads-raw
| WHERE industry == "SaaS"
| KEEP full_name, company_name, industry, employee_count, funding_stage, score_tier
| SORT employee_count DESC
| LIMIT 20
```

### Find high-employee companies
```esql
FROM leads-raw
| WHERE employee_count > 100
| KEEP company_name, industry, employee_count, annual_revenue, funding_stage
| SORT employee_count DESC
| LIMIT 20
```

### Search by keywords
```esql
FROM leads-raw
| WHERE MATCH(keywords, "AI automation")
| KEEP full_name, company_name, keywords, industry
| LIMIT 20
```

---

## Scoring & Analytics Queries

### Score distribution
```esql
FROM leads-raw
| WHERE score IS NOT NULL
| STATS count = COUNT(*), avg_score = AVG(score) BY score_tier
| SORT avg_score DESC
```

### Unscored leads (need processing)
```esql
FROM leads-raw
| WHERE score IS NULL
| KEEP full_name, company_name, industry, employee_count
| SORT created_at DESC
| LIMIT 50
```

### Hot leads ready for outreach
```esql
FROM leads-raw
| WHERE score_tier == "Hot" AND outreach_email IS NOT NULL
| KEEP full_name, company_name, email, score, outreach_email
| SORT score DESC
```

### Leads by funding stage
```esql
FROM leads-raw
| STATS count = COUNT(*), avg_employees = AVG(employee_count) BY funding_stage
| SORT count DESC
```

---

## Outreach Queries

### Leads needing outreach generation
```esql
FROM leads-raw
| WHERE score_tier IN ("Hot", "Warm") AND outreach_email IS NULL
| KEEP full_name, company_name, email, score, score_tier, industry
| SORT score DESC
| LIMIT 20
```

### Recently scored leads
```esql
FROM leads-raw
| WHERE score IS NOT NULL
| KEEP full_name, company_name, score, score_tier, updated_at
| SORT updated_at DESC
| LIMIT 20
```

---

## Agent Action Audit

### Recent agent actions
```esql
FROM leads-raw
| WHERE agent_actions IS NOT NULL
| KEEP company_name, agent_actions, updated_at
| SORT updated_at DESC
| LIMIT 20
```
