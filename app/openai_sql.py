import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

HEADERS = {
    "Content-Type": "application/json",
    "api-key": AZURE_KEY
}

def generate_sql_from_user_input(schema: str, question: str) -> str:
    prompt = f"""
Schema:
{schema}

Question:
{question}

Convert the question into a SQL query using the given schema.
Respond with only the raw SQL code. Do not include any markdown, explanations, or comments.
"""

    url = f"{AZURE_ENDPOINT}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"

    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant that generates SQL from user questions and schema."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    
    raw_sql = response.json()["choices"][0]["message"]["content"].strip()

    # Remove markdown wrapping if accidentally included
    clean_sql = re.sub(r"^```sql\s*|```$", "", raw_sql, flags=re.IGNORECASE | re.MULTILINE).strip()
    
    return clean_sql
