import os
import re
import ssl
import requests
import streamlit as st
import urllib3
from dotenv import load_dotenv

# Disable SSL verification (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load local .env file (only needed locally)
load_dotenv()

# Constants
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"

def get_api_key():
    """Load API key from Streamlit secrets or fallback to .env"""
    try:
        return st.secrets["GROQ_API_KEY"]
    except (AttributeError, KeyError):
        return os.getenv("GROQ_API_KEY")


def generate_sql_from_user_input(schema: str, question: str) -> str:
    api_key = get_api_key()
    
    if not api_key:
        raise Exception("GROQ API key not found. Set it in Streamlit secrets or .env")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = f"""
Schema: {schema}

Question: {question}

Convert the question into a SQL query using the given schema. Respond with only the raw SQL code. Do not include any markdown, explanations, or comments.
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that generates SQL from user questions and schema."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1000
    }

    try:
        response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, verify=False)
        response.raise_for_status()

        raw_sql = response.json()["choices"][0]["message"]["content"].strip()
        clean_sql = re.sub(r"^```sql\s*|```$", "", raw_sql, flags=re.IGNORECASE | re.MULTILINE).strip()

        return clean_sql
    except requests.RequestException as e:
        raise Exception(f"Failed to generate SQL: {e}")
    except KeyError as e:
        raise Exception(f"Unexpected response format: {e}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")
