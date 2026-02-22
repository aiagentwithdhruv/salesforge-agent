"""
SalesForge Agent — Pipeline Analytics
Runs ES|QL queries to show the full sales pipeline after batch scoring.
Demonstrates the analytics power of ES|QL with scored lead data.
"""

import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

ES_URL = os.getenv("ELASTICSEARCH_URL")
ES_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")


def run_esql(es: Elasticsearch, query: str, label: str):
    """Run an ES|QL query and display results."""
    print(f"\n{'─' * 60}")
    print(f"  {label}")
    print(f"  Query: {query}")
    print(f"{'─' * 60}")

    try:
        result = es.esql.query(body={"query": query})
        columns = result.get("columns", [])
        values = result.get("values", [])

        if not values:
            print("  (no results)")
            return

        # Print header
        col_names = [c["name"] for c in columns]
        widths = [max(len(str(name)), max(len(str(row[i])) for row in values)) for i, name in enumerate(col_names)]
        header = " | ".join(f"{name:{widths[i]}}" for i, name in enumerate(col_names))
        print(f"  {header}")
        print(f"  {'─' * len(header)}")

        # Print rows
        for row in values:
            line = " | ".join(f"{str(val):{widths[i]}}" for i, val in enumerate(row))
            print(f"  {line}")

        print(f"\n  ({len(values)} rows)")
    except Exception as e:
        print(f"  Error: {e}")


def main():
    print("=" * 60)
    print("  SalesForge Agent — Pipeline Analytics")
    print("=" * 60)

    es = Elasticsearch(ES_URL, api_key=ES_API_KEY)

    # 1. Pipeline Funnel
    run_esql(es,
        'FROM leads-raw | STATS count = COUNT(*) BY score_tier | SORT count DESC',
        "📊 PIPELINE FUNNEL — Lead Distribution by Tier"
    )

    # 2. Average Score by Industry
    run_esql(es,
        'FROM leads-raw | STATS avg_score = AVG(score), count = COUNT(*) BY industry | SORT avg_score DESC',
        "🏢 INDUSTRY INTELLIGENCE — Average Score by Industry"
    )

    # 3. Hot Leads by Funding Stage
    run_esql(es,
        'FROM leads-raw | WHERE score_tier == "Hot" | STATS count = COUNT(*) BY funding_stage | SORT count DESC',
        "🔥 HOT LEADS — Distribution by Funding Stage"
    )

    # 4. Top 10 Highest Scoring Leads
    run_esql(es,
        'FROM leads-raw | SORT score DESC | LIMIT 10 | KEEP company_name, industry, score, score_tier, employee_count, funding_stage',
        "🏆 TOP 10 — Highest Scoring Leads"
    )

    # 5. Score Distribution
    run_esql(es,
        'FROM leads-raw | STATS min_score = MIN(score), max_score = MAX(score), avg_score = AVG(score), median_score = MEDIAN(score)',
        "📈 SCORE DISTRIBUTION — Statistical Summary"
    )

    # 6. Hot Leads Ready for Outreach (no email generated yet)
    run_esql(es,
        'FROM leads-raw | WHERE score_tier == "Hot" | SORT score DESC | KEEP company_name, full_name, job_title, email, score, industry',
        "📧 OUTREACH QUEUE — Hot Leads Ready for Contact"
    )

    # 7. Industry × Funding Cross-Tab
    run_esql(es,
        'FROM leads-raw | WHERE score_tier == "Hot" | STATS count = COUNT(*) BY industry, funding_stage | SORT count DESC',
        "🔀 CROSS-TAB — Hot Leads by Industry × Funding"
    )

    # 8. Audit Trail Summary
    run_esql(es,
        'FROM agent-actions-log | STATS count = COUNT(*) BY action_type | SORT count DESC',
        "📋 AUDIT TRAIL — Actions Logged"
    )

    print(f"\n{'=' * 60}")
    print("  Pipeline analytics complete.")
    print("  These queries can all be run by the SalesForge agent in Kibana.")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
