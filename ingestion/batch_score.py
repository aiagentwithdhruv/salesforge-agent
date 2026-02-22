"""
SalesForge Agent — Batch Lead Scoring Pipeline
Processes ALL leads in Elasticsearch, applies deterministic scoring rubric,
writes scores + tiers + reasoning back to each document.

This is the CORE intelligence pipeline — transforms raw leads into scored pipeline data.

Scoring Rubric (0-100):
  - Employee Count:       0-25 points (scale = market reach)
  - Funding Stage:        0-25 points (money = ability to buy)
  - Industry Fit:         0-25 points (alignment with AI/automation services)
  - Description Quality:  0-25 points (sophistication of company positioning)

Tiers:
  - Hot  (75-100): Immediate outreach — high-value, ready to buy
  - Warm (45-74):  Nurture sequence — potential but needs cultivation
  - Cold (0-44):   Archive — low fit, revisit quarterly
"""

import os
import json
from datetime import datetime

from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers

load_dotenv()

ES_URL = os.getenv("ELASTICSEARCH_URL")
ES_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
INDEX_NAME = "leads-raw"
ACTIONS_INDEX = "agent-actions-log"


# --- Scoring Functions ---

def score_employee_count(count: int) -> tuple[int, str]:
    """Score based on employee count (proxy for market reach and deal size)."""
    if count >= 1000:
        return 25, f"Enterprise ({count} employees) — large deal potential"
    elif count >= 250:
        return 22, f"Mid-market ({count} employees) — strong deal potential"
    elif count >= 100:
        return 18, f"Growth-stage ({count} employees) — good opportunity"
    elif count >= 50:
        return 14, f"Small-mid ({count} employees) — moderate opportunity"
    elif count >= 25:
        return 10, f"Small business ({count} employees) — standard opportunity"
    elif count >= 10:
        return 6, f"Startup ({count} employees) — early stage"
    else:
        return 3, f"Micro ({count} employees) — very early stage"


def score_funding_stage(stage: str) -> tuple[int, str]:
    """Score based on funding stage (proxy for budget availability)."""
    scores = {
        "Series C": (25, "Series C — significant budget, actively scaling"),
        "Public": (25, "Public company — enterprise budgets available"),
        "Growth": (22, "Growth stage — investing in tools and automation"),
        "Series B": (20, "Series B — funded, building go-to-market"),
        "Series A": (15, "Series A — funded but selective spending"),
        "Seed": (10, "Seed — limited budget, early decisions"),
        "Pre-Seed": (5, "Pre-Seed — minimal budget, founder-led"),
        "Bootstrapped": (8, "Bootstrapped — profitable but cost-conscious"),
    }
    return scores.get(stage, (5, f"{stage} — unknown funding stage"))


def score_industry_fit(industry: str) -> tuple[int, str]:
    """Score based on industry alignment with AI automation services."""
    high_fit = {"SaaS": 25, "FinTech": 25, "Cybersecurity": 23, "MarTech": 22}
    medium_fit = {"HealthTech": 18, "EdTech": 17, "E-Commerce": 17, "HRTech": 16, "InsurTech": 16}
    lower_fit = {"PropTech": 12, "LegalTech": 12, "LogTech": 11, "FoodTech": 10, "AgriTech": 8, "CleanTech": 8}

    if industry in high_fit:
        return high_fit[industry], f"{industry} — high alignment with AI/automation services"
    elif industry in medium_fit:
        return medium_fit[industry], f"{industry} — moderate alignment, automation opportunities exist"
    elif industry in lower_fit:
        return lower_fit[industry], f"{industry} — niche fit, specific use cases only"
    else:
        return 8, f"{industry} — unknown industry alignment"


def score_description_quality(description: str, keywords: str) -> tuple[int, str]:
    """Score based on company description sophistication and keyword signals."""
    score = 0
    reasons = []

    # Length indicates sophistication
    if len(description) > 80:
        score += 8
        reasons.append("detailed positioning")
    elif len(description) > 40:
        score += 5
        reasons.append("adequate positioning")
    else:
        score += 2
        reasons.append("minimal positioning")

    # AI/automation keywords signal readiness
    ai_keywords = ["AI", "automation", "machine learning", "analytics", "data", "platform"]
    keyword_matches = [kw for kw in ai_keywords if kw.lower() in (description + " " + keywords).lower()]
    if len(keyword_matches) >= 3:
        score += 10
        reasons.append(f"strong tech signals ({', '.join(keyword_matches[:3])})")
    elif len(keyword_matches) >= 1:
        score += 6
        reasons.append(f"some tech signals ({', '.join(keyword_matches)})")
    else:
        score += 2
        reasons.append("no tech signals")

    # Enterprise/B2B signals
    enterprise_signals = ["enterprise", "B2B", "scale", "compliance", "security"]
    enterprise_matches = [s for s in enterprise_signals if s.lower() in (description + " " + keywords).lower()]
    if enterprise_matches:
        score += 7
        reasons.append(f"enterprise signals ({', '.join(enterprise_matches[:2])})")
    else:
        score += 2
        reasons.append("no enterprise signals")

    return min(score, 25), "; ".join(reasons)


def score_lead(lead: dict) -> dict:
    """Apply full scoring rubric to a lead. Returns score details."""
    emp_score, emp_reason = score_employee_count(lead.get("employee_count", 0))
    fund_score, fund_reason = score_funding_stage(lead.get("funding_stage", "Unknown"))
    ind_score, ind_reason = score_industry_fit(lead.get("industry", ""))
    desc_score, desc_reason = score_description_quality(
        lead.get("company_description", ""),
        lead.get("keywords", "")
    )

    total_score = emp_score + fund_score + ind_score + desc_score

    if total_score >= 75:
        tier = "Hot"
    elif total_score >= 45:
        tier = "Warm"
    else:
        tier = "Cold"

    reasoning = (
        f"Score: {total_score}/100 → {tier}\n"
        f"  Employee ({emp_score}/25): {emp_reason}\n"
        f"  Funding ({fund_score}/25): {fund_reason}\n"
        f"  Industry ({ind_score}/25): {ind_reason}\n"
        f"  Description ({desc_score}/25): {desc_reason}"
    )

    return {
        "score": total_score,
        "score_tier": tier,
        "score_reasoning": reasoning,
        "score_breakdown": {
            "employee": {"score": emp_score, "max": 25, "reason": emp_reason},
            "funding": {"score": fund_score, "max": 25, "reason": fund_reason},
            "industry": {"score": ind_score, "max": 25, "reason": ind_reason},
            "description": {"score": desc_score, "max": 25, "reason": desc_reason},
        },
    }


# --- Action Logging ---

def create_actions_index(es: Elasticsearch):
    """Create the agent-actions-log index for audit trail."""
    mapping = {
        "mappings": {
            "properties": {
                "lead_id": {"type": "keyword"},
                "company_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "action_type": {"type": "keyword"},
                "action_details": {"type": "text"},
                "score": {"type": "float"},
                "score_tier": {"type": "keyword"},
                "agent_session": {"type": "keyword"},
                "timestamp": {"type": "date"},
            }
        }
    }

    if es.indices.exists(index=ACTIONS_INDEX):
        es.indices.delete(index=ACTIONS_INDEX)

    es.indices.create(index=ACTIONS_INDEX, body=mapping)
    print(f"Created index '{ACTIONS_INDEX}'")


def log_action(es: Elasticsearch, lead_id: str, company_name: str,
               action_type: str, details: str, score: float = None,
               score_tier: str = None, session_id: str = None):
    """Log an agent action to the audit trail."""
    doc = {
        "lead_id": lead_id,
        "company_name": company_name,
        "action_type": action_type,
        "action_details": details,
        "score": score,
        "score_tier": score_tier,
        "agent_session": session_id or "batch-scoring",
        "timestamp": datetime.utcnow().isoformat(),
    }
    es.index(index=ACTIONS_INDEX, body=doc)


# --- Main Pipeline ---

def main():
    print("=" * 60)
    print("  SalesForge Agent — Batch Scoring Pipeline")
    print("=" * 60)
    print()

    # Connect
    es = Elasticsearch(ES_URL, api_key=ES_API_KEY)
    info = es.info()
    print(f"Connected to Elasticsearch {info['version']['number']}")

    # Create actions index
    create_actions_index(es)

    # Fetch ALL leads
    print(f"\nFetching all leads from '{INDEX_NAME}'...")
    result = es.search(
        index=INDEX_NAME,
        body={"query": {"match_all": {}}, "size": 1000},
    )
    leads = result["hits"]["hits"]
    print(f"Found {len(leads)} leads to score\n")

    # Score each lead
    session_id = f"batch-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    hot_count = 0
    warm_count = 0
    cold_count = 0
    update_actions = []

    print("Scoring leads...")
    print("-" * 60)

    for hit in leads:
        lead_id = hit["_id"]
        lead = hit["_source"]
        company = lead.get("company_name", "Unknown")

        # Score the lead
        result = score_lead(lead)

        # Track counts
        if result["score_tier"] == "Hot":
            hot_count += 1
            marker = "🔥"
        elif result["score_tier"] == "Warm":
            warm_count += 1
            marker = "🟡"
        else:
            cold_count += 1
            marker = "🔵"

        print(f"  {marker} {company:40s} → {result['score']:3d}/100 ({result['score_tier']})")

        # Prepare bulk update
        update_actions.append({
            "_op_type": "update",
            "_index": INDEX_NAME,
            "_id": lead_id,
            "doc": {
                "score": result["score"],
                "score_tier": result["score_tier"],
                "score_reasoning": result["score_reasoning"],
                "score_breakdown": result["score_breakdown"],
                "updated_at": datetime.utcnow().isoformat(),
            },
        })

        # Log to audit trail
        log_action(
            es, lead_id, company,
            action_type="scored",
            details=result["score_reasoning"],
            score=result["score"],
            score_tier=result["score_tier"],
            session_id=session_id,
        )

    # Bulk update all leads
    print(f"\n{'=' * 60}")
    print("Writing scores back to Elasticsearch...")
    success, errors = helpers.bulk(es, update_actions)
    print(f"Updated {success} leads, {len(errors) if isinstance(errors, list) else errors} errors")

    # Refresh indices
    es.indices.refresh(index=INDEX_NAME)
    es.indices.refresh(index=ACTIONS_INDEX)

    # Pipeline summary
    total = hot_count + warm_count + cold_count
    print(f"\n{'=' * 60}")
    print("  PIPELINE SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Total Leads:  {total}")
    print(f"  🔥 Hot:       {hot_count} ({hot_count/total*100:.0f}%) — Ready for outreach")
    print(f"  🟡 Warm:      {warm_count} ({warm_count/total*100:.0f}%) — Nurture sequence")
    print(f"  🔵 Cold:      {cold_count} ({cold_count/total*100:.0f}%) — Archive for review")
    print(f"{'=' * 60}")
    print(f"  Session ID:   {session_id}")
    print(f"  Actions logged to '{ACTIONS_INDEX}'")
    print(f"\n  Next: Open Kibana → Agent Builder → Ask:")
    print(f'  "Show me all Hot leads sorted by score"')
    print(f'  "Compare the top 3 Hot leads and recommend which to contact first"')
    print(f'  "Generate personalized outreach for the highest-scoring lead"')
    print()


if __name__ == "__main__":
    main()
