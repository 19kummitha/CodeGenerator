import os
import re
import ssl
import requests
import streamlit as st
import urllib3
from dotenv import load_dotenv

# Load environment variables (only needed locally)
load_dotenv()

# Disable SSL verification (not recommended in production)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Constants
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"

def get_api_key():
    """Load API key from Streamlit secrets or fallback to .env"""
    try:
        return st.secrets["GROQ_API_KEY"]
    except (AttributeError, KeyError):
        return os.getenv("GROQ_API_KEY")

def get_headers():
    """Construct headers with API key"""
    api_key = get_api_key()
    if not api_key:
        raise Exception("GROQ API key not found. Please set it in .env or Streamlit secrets.")
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

def generate_code_from_user_input(language: str, question: str) -> str:
    prompt = f"""
Language: {language}

Question:
{question}

Generate the complete {language} code to solve the question above.
Only respond with raw code — no markdown, no explanation, no comments.
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": f"You are an expert {language} developer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        response = requests.post(GROQ_ENDPOINT, headers=get_headers(), json=payload, verify=False)
        response.raise_for_status()

        code_raw = response.json()["choices"][0]["message"]["content"].strip()
        code_clean = re.sub(r"^```[\w]*\s*|```$", "", code_raw, flags=re.IGNORECASE | re.MULTILINE).strip()

        return code_clean
    except requests.RequestException as e:
        raise Exception(f"Failed to generate code: {e}")
    except KeyError as e:
        raise Exception(f"Unexpected response format: {e}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

def explain_code(language: str, code: str) -> str:
    prompt = f"""
You are a programming expert. Explain the following {language} code in simple, clear terms:

{code}
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": f"You are a helpful {language} programming tutor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1500
    }

    try:
        response = requests.post(GROQ_ENDPOINT, headers=get_headers(), json=payload, verify=False)
        response.raise_for_status()

        explanation = response.json()["choices"][0]["message"]["content"].strip()
        return explanation
    except requests.RequestException as e:
        raise Exception(f"Failed to explain code: {e}")
    except KeyError as e:
        raise Exception(f"Unexpected response format: {e}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")
