# openai_code.py
import os
import requests
import re
from dotenv import load_dotenv
import certifi

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

HEADERS = {
    "Content-Type": "application/json",
    "api-key": AZURE_KEY,
}

def generate_code_from_user_input(language: str, question: str) -> str:
    prompt = f"""
Language: {language}

Question:
{question}

Generate the complete {language} code to solve the question above.
Only respond with raw code — no markdown, no explanation, no comments.
"""

    url = f"{AZURE_ENDPOINT}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"

    payload = {
        "messages": [
            {"role": "system", "content": f"You are an expert {language} developer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload, verify=certifi.where())
        response.raise_for_status()
        code_raw = response.json()["choices"][0]["message"]["content"].strip()
        code_clean = re.sub(r"^```[\w]*\s*|```$", "", code_raw, flags=re.IGNORECASE | re.MULTILINE).strip()
        return code_clean
    except requests.RequestException as e:
        raise Exception(f"Failed to generate code: {e}")
def explain_code(language: str, code: str) -> str:
    prompt = f"""
You are a programming expert. Explain the following {language} code in simple, clear terms:

{code}
"""

    url = f"{AZURE_ENDPOINT}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
    payload = {
        "messages": [
            {"role": "system", "content": f"You are a helpful {language} programming tutor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(url, headers=HEADERS, json=payload, verify=certifi.where())
    response.raise_for_status()
    explanation = response.json()["choices"][0]["message"]["content"].strip()
    return explanation

