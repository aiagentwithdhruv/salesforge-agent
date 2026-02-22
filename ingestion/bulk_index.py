"""
SalesForge Agent — Bulk Indexer
Index any JSON file of leads into Elasticsearch.
Usage: python bulk_index.py --file data/my_leads.json
"""

import argparse
import json
import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers
from openai import OpenAI

load_dotenv()

ES_URL = os.getenv("ELASTICSEARCH_URL")
ES_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "leads-raw"


def load_leads(file_path: str) -> list[dict]:
    with open(file_path) as f:
        data = json.load(f)

    if isinstance(data, dict) and "leads" in data:
        return data["leads"]
    if isinstance(data, list):
        return data
    raise ValueError("JSON must be a list of leads or {leads: [...]}")


def add_embeddings(leads: list[dict]) -> list[dict]:
    if not OPENAI_API_KEY:
        print("No OPENAI_API_KEY — skipping embeddings")
        return leads

    client = OpenAI(api_key=OPENAI_API_KEY)
    descriptions = [
        lead.get("company_description", lead.get("description", ""))
        for lead in leads
    ]

    # Filter out empty descriptions
    non_empty = [(i, d) for i, d in enumerate(descriptions) if d.strip()]
    if not non_empty:
        return leads

    texts = [d for _, d in non_empty]
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    for idx, (lead_idx, _) in enumerate(non_empty):
        leads[lead_idx]["company_description_vector"] = response.data[idx].embedding

    print(f"Added embeddings for {len(non_empty)} leads")
    return leads


def bulk_index(es: Elasticsearch, leads: list[dict]):
    actions = [{"_index": INDEX_NAME, "_source": lead} for lead in leads]
    success, errors = helpers.bulk(es, actions, raise_on_error=False)
    print(f"Indexed: {success}, Errors: {len(errors)}")
    if errors:
        for err in errors[:5]:
            print(f"  Error: {err}")


def main():
    parser = argparse.ArgumentParser(description="Bulk index leads into Elasticsearch")
    parser.add_argument("--file", required=True, help="Path to JSON file with leads")
    parser.add_argument("--no-embeddings", action="store_true", help="Skip embedding generation")
    args = parser.parse_args()

    es = Elasticsearch(ES_URL, api_key=ES_API_KEY)
    print(f"Connected to Elasticsearch: {es.info()['version']['number']}")

    leads = load_leads(args.file)
    print(f"Loaded {len(leads)} leads from {args.file}")

    if not args.no_embeddings:
        leads = add_embeddings(leads)

    bulk_index(es, leads)

    es.indices.refresh(index=INDEX_NAME)
    count = es.count(index=INDEX_NAME)["count"]
    print(f"Total documents in '{INDEX_NAME}': {count}")


if __name__ == "__main__":
    main()
