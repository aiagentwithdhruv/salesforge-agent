"""
SalesForge Agent — Find Similar Leads
Given a lead (by company name or description), finds the N most similar leads
using Elasticsearch kNN vector search on company description embeddings.

This is the WOW FEATURE — "Find me more leads like this one"
Uses pure vector similarity to discover leads the agent wouldn't find with keywords alone.
"""

import os
import sys
import json
from datetime import datetime

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from openai import OpenAI

load_dotenv()

ES_URL = os.getenv("ELASTICSEARCH_URL")
ES_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "leads-raw"


def get_embedding(text: str, client: OpenAI) -> list[float]:
    """Generate embedding for a text query."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def find_by_company_name(es: Elasticsearch, company_name: str) -> dict | None:
    """Find a lead by company name."""
    result = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "match": {"company_name": company_name}
            },
            "size": 1,
        },
    )
    hits = result["hits"]["hits"]
    return hits[0] if hits else None


def find_similar_by_vector(es: Elasticsearch, vector: list[float],
                           exclude_id: str = None, top_k: int = 5) -> list[dict]:
    """Find similar leads using kNN vector search."""
    query = {
        "knn": {
            "field": "company_description_vector",
            "query_vector": vector,
            "k": top_k + (1 if exclude_id else 0),
            "num_candidates": 50,
        },
        "_source": {
            "excludes": ["company_description_vector"]
        },
        "size": top_k + (1 if exclude_id else 0),
    }

    result = es.search(index=INDEX_NAME, body=query)
    hits = result["hits"]["hits"]

    # Exclude the source lead
    if exclude_id:
        hits = [h for h in hits if h["_id"] != exclude_id]

    return hits[:top_k]


def find_similar_by_description(es: Elasticsearch, openai_client: OpenAI,
                                 description: str, top_k: int = 5) -> list[dict]:
    """Find leads similar to a description using embedding search."""
    vector = get_embedding(description, openai_client)
    return find_similar_by_vector(es, vector, top_k=top_k)


def display_results(source_lead: dict, similar_leads: list[dict]):
    """Display similar leads in a formatted table."""
    print(f"\n{'=' * 70}")
    print(f"  SIMILAR LEADS TO: {source_lead.get('company_name', 'Query')}")
    print(f"  Industry: {source_lead.get('industry', 'N/A')} | "
          f"Employees: {source_lead.get('employee_count', 'N/A')} | "
          f"Funding: {source_lead.get('funding_stage', 'N/A')}")
    print(f"  Description: {source_lead.get('company_description', 'N/A')}")
    print(f"{'=' * 70}\n")

    for i, hit in enumerate(similar_leads, 1):
        lead = hit["_source"]
        similarity = hit.get("_score", 0)
        tier = lead.get("score_tier", "Unscored")
        score = lead.get("score", "N/A")

        tier_marker = {"Hot": "🔥", "Warm": "🟡", "Cold": "🔵"}.get(tier, "⚪")

        print(f"  #{i} {tier_marker} {lead['company_name']}")
        print(f"     Similarity: {similarity:.4f} | Score: {score}/100 ({tier})")
        print(f"     Industry: {lead.get('industry')} | Employees: {lead.get('employee_count')} | "
              f"Funding: {lead.get('funding_stage')}")
        print(f"     {lead.get('company_description', '')}")
        print(f"     Contact: {lead.get('full_name')} ({lead.get('job_title')}) — {lead.get('email')}")
        print()


def main():
    print("=" * 60)
    print("  SalesForge Agent — Find Similar Leads")
    print("=" * 60)

    es = Elasticsearch(ES_URL, api_key=ES_API_KEY)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    # Parse args
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python find_similar.py 'Company Name'         # Find leads like this company")
        print("  python find_similar.py --query 'AI SaaS for enterprise'  # Find by description")
        print()
        # Default: interactive mode - show all Hot leads and let user pick
        print("No company specified. Showing all Hot leads to choose from:\n")

        result = es.search(
            index=INDEX_NAME,
            body={
                "query": {"term": {"score_tier": "Hot"}},
                "sort": [{"score": "desc"}],
                "size": 20,
                "_source": {"excludes": ["company_description_vector"]},
            },
        )

        for i, hit in enumerate(result["hits"]["hits"], 1):
            lead = hit["_source"]
            print(f"  {i}. 🔥 {lead['company_name']:35s} — {lead.get('score', 'N/A')}/100 "
                  f"({lead.get('industry')}, {lead.get('employee_count')} emp)")

        print(f"\nRun: python find_similar.py 'COMPANY_NAME'")
        return

    if sys.argv[1] == "--query":
        # Search by description
        query = " ".join(sys.argv[2:])
        print(f"\nSearching for leads similar to: '{query}'")
        similar = find_similar_by_description(es, openai_client, query, top_k=5)
        display_results({"company_name": f"Query: {query}", "company_description": query}, similar)
    else:
        # Search by company name
        company_name = " ".join(sys.argv[1:])
        print(f"\nLooking up: '{company_name}'...")

        source = find_by_company_name(es, company_name)
        if not source:
            print(f"Company '{company_name}' not found. Try a different name.")
            return

        source_lead = source["_source"]
        vector = source_lead.get("company_description_vector")

        if not vector:
            print("This lead has no vector embedding. Generating one...")
            vector = get_embedding(source_lead["company_description"], openai_client)

        similar = find_similar_by_vector(es, vector, exclude_id=source["_id"], top_k=5)
        display_results(source_lead, similar)


if __name__ == "__main__":
    main()
