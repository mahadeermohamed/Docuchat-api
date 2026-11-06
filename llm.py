from fastapi import HTTPException
import requests, os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")

def call_llm(messages: list[dict]) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={API_KEY}"
    body = {"contents": [{"role": m["role"], "parts": [{"text": m["text"]}]} for m in messages]}

    try:
        r = requests.post(url, json=body, timeout=30)
        r.raise_for_status()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="The AI service took too long. Try again.")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=502, detail="The AI service is unavailable.")

    try:
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise HTTPException(status_code=502, detail="The AI service returned an unexpected response.")