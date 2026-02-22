"""
SalesForge Agent — Seed Data Generator
Generates 100 realistic synthetic leads and indexes them into Elasticsearch.
Uses Faker for data generation + OpenAI for embeddings.
"""

import json
import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers
from faker import Faker
from openai import OpenAI

load_dotenv()

fake = Faker()

# --- Configuration ---
ES_URL = os.getenv("ELASTICSEARCH_URL")
ES_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "leads-raw"
NUM_LEADS = 100

# --- Industry & Company Templates ---
INDUSTRIES = [
    "SaaS", "FinTech", "HealthTech", "E-Commerce", "EdTech",
    "Cybersecurity", "MarTech", "HRTech", "PropTech", "LegalTech",
    "InsurTech", "AgriTech", "CleanTech", "LogTech", "FoodTech",
]

FUNDING_STAGES = [
    "Pre-Seed", "Seed", "Series A", "Series B", "Series C",
    "Growth", "Bootstrapped", "Public",
]

TECH_STACKS = [
    ["Python", "Django", "PostgreSQL", "AWS"],
    ["TypeScript", "React", "Node.js", "GCP"],
    ["Java", "Spring Boot", "MySQL", "Azure"],
    ["Go", "Kubernetes", "MongoDB", "AWS"],
    ["Ruby", "Rails", "Redis", "Heroku"],
    ["Python", "FastAPI", "Elasticsearch", "Docker"],
    ["Rust", "WebAssembly", "Cloudflare Workers"],
    ["PHP", "Laravel", "MySQL", "DigitalOcean"],
]

JOB_TITLES = [
    "CEO", "CTO", "VP of Sales", "Head of Growth",
    "Director of Engineering", "VP of Marketing",
    "Chief Revenue Officer", "Head of Product",
    "Director of Operations", "VP of Business Development",
]

COMPANY_TEMPLATES = [
    "{industry} platform that helps {target} {action}",
    "AI-powered {industry} solution for {target}",
    "Next-gen {industry} tools for modern {target}",
    "{industry} automation platform enabling {target} to {action}",
    "Enterprise {industry} software transforming how {target} {action}",
]

TARGETS = [
    "small businesses", "enterprise teams", "startups",
    "healthcare providers", "financial institutions",
    "e-commerce brands", "sales teams", "HR departments",
    "marketing agencies", "real estate firms",
]

ACTIONS = [
    "scale operations", "reduce costs by 40%", "automate workflows",
    "improve customer retention", "accelerate growth",
    "streamline compliance", "boost revenue", "optimize hiring",
    "personalize experiences", "manage risk",
]


def generate_company_description(industry: str) -> str:
    template = random.choice(COMPANY_TEMPLATES)
    return template.format(
        industry=industry,
        target=random.choice(TARGETS),
        action=random.choice(ACTIONS),
    )


def generate_lead() -> dict:
    industry = random.choice(INDUSTRIES)
    founded = random.randint(2010, 2025)
    employee_count = random.choice([5, 10, 25, 50, 100, 250, 500, 1000, 2500])
    revenue_ranges = [
        "<$1M", "$1M-$5M", "$5M-$10M", "$10M-$50M", "$50M-$100M", "$100M+",
    ]

    first_name = fake.first_name()
    last_name = fake.last_name()
    company = fake.company()
    domain = company.lower().replace(" ", "").replace(",", "").replace("-", "") + ".com"

    return {
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}",
        "email": f"{first_name.lower()}.{last_name.lower()}@{domain}",
        "phone": fake.phone_number(),
        "job_title": random.choice(JOB_TITLES),
        "company_name": company,
        "company_domain": domain,
        "industry": industry,
        "company_description": generate_company_description(industry),
        "keywords": ", ".join(random.sample(
            ["AI", "automation", "analytics", "cloud", "API", "mobile",
             "enterprise", "B2B", "B2C", "marketplace", "platform", "SaaS",
             "machine learning", "data", "security", "compliance", "payments"],
            k=random.randint(3, 6)
        )),
        "location": fake.city() + ", " + fake.country(),
        "employee_count": employee_count,
        "annual_revenue": random.choice(revenue_ranges),
        "founded_year": founded,
        "funding_stage": random.choice(FUNDING_STAGES),
        "tech_stack": random.choice(TECH_STACKS),
        "score": None,
        "score_tier": None,
        "score_reasoning": None,
        "outreach_email": None,
        "agent_actions": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "source": "synthetic-seed",
    }


def generate_embeddings(texts: list[str], client: OpenAI) -> list[list[float]]:
    """Generate embeddings for company descriptions using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]


def create_index(es: Elasticsearch):
    """Create the leads-raw index with proper mappings."""
    with open(os.path.join(os.path.dirname(__file__), "index_mappings.json")) as f:
        mappings = json.load(f)

    if es.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Deleting...")
        es.indices.delete(index=INDEX_NAME)

    es.indices.create(
        index=INDEX_NAME,
        body=mappings[INDEX_NAME],
    )
    print(f"Created index '{INDEX_NAME}'")


def bulk_index_leads(es: Elasticsearch, leads: list[dict]):
    """Bulk index leads into Elasticsearch."""
    actions = [
        {
            "_index": INDEX_NAME,
            "_source": lead,
        }
        for lead in leads
    ]
    success, errors = helpers.bulk(es, actions)
    print(f"Indexed {success} leads, {len(errors)} errors")
    return success, errors


def main():
    print("=== SalesForge Agent — Seed Data Generator ===\n")

    # Connect to Elasticsearch
    es = Elasticsearch(
        ES_URL,
        api_key=ES_API_KEY,
    )
    info = es.info()
    print(f"Connected to Elasticsearch: {info['version']['number']}\n")

    # Create index
    create_index(es)

    # Generate leads
    print(f"Generating {NUM_LEADS} synthetic leads...")
    leads = [generate_lead() for _ in range(NUM_LEADS)]

    # Generate embeddings for company descriptions
    if OPENAI_API_KEY:
        print("Generating vector embeddings for hybrid search...")
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        descriptions = [lead["company_description"] for lead in leads]

        # Batch embeddings (max 2048 per request)
        batch_size = 100
        for i in range(0, len(descriptions), batch_size):
            batch = descriptions[i:i + batch_size]
            embeddings = generate_embeddings(batch, openai_client)
            for j, embedding in enumerate(embeddings):
                leads[i + j]["company_description_vector"] = embedding
        print(f"Generated {len(leads)} embeddings")
    else:
        print("WARNING: No OPENAI_API_KEY — skipping vector embeddings")
        for lead in leads:
            lead.pop("company_description_vector", None)

    # Bulk index
    print("\nIndexing into Elasticsearch...")
    bulk_index_leads(es, leads)

    # Save sample data locally
    sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_leads.json")
    # Strip vectors for readability in the sample file
    sample_leads = []
    for lead in leads[:10]:
        sample = {k: v for k, v in lead.items() if k != "company_description_vector"}
        sample_leads.append(sample)

    with open(sample_path, "w") as f:
        json.dump(sample_leads, f, indent=2, default=str)
    print(f"\nSaved 10 sample leads to {sample_path}")

    # Verify
    es.indices.refresh(index=INDEX_NAME)
    count = es.count(index=INDEX_NAME)["count"]
    print(f"\nTotal documents in '{INDEX_NAME}': {count}")
    print("\n=== Seed complete! Open Kibana → Agent Builder to start using SalesForge. ===")


if __name__ == "__main__":
    main()
