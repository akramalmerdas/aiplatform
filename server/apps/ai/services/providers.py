# providers.py
import os
import requests
from openai import OpenAI

PROVIDER = os.getenv("LLM_PROVIDER", "paid")   # "paid" or "oss"

# --- Paid API (OpenAI) ---
PAID_MODEL = os.getenv("PAID_MODEL", "gpt-4o-mini")
openai_client = OpenAI()  # reads OPENAI_API_KEY from environment

# --- OSS (Ollama) optional fallback ---
OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct-q4_K_M")

def call_llm(messages, temperature=0.2, num_ctx=4096, num_predict=1200):
    """
    Single entry point for LLM calls.
    Switch provider via env: LLM_PROVIDER=paid|oss
    """
    if PROVIDER == "paid":
        resp = openai_client.chat.completions.create(
            model=PAID_MODEL,
            messages=messages,
            temperature=temperature
        )
        return resp.choices[0].message.content

    elif PROVIDER == "oss":
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx,
                "num_predict": num_predict
            }
        }
        r = requests.post(OLLAMA_URL, json=payload, timeout=180)
        r.raise_for_status()
        return r.json()["message"]["content"]

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER}")
