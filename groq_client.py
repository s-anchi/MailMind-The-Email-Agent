"""
Thin wrapper around the Groq API (OpenAI-compatible endpoint).

Groq's free tier requires no credit card and gives you access to fast
open-source models (Llama, etc). Get a key in ~30 seconds at:
    https://console.groq.com/keys

Then set it as an environment variable:
    Windows (PowerShell):  $env:GROQ_API_KEY="your-key-here"
    Mac/Linux:              export GROQ_API_KEY="your-key-here"
"""

import json
import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqError(Exception):
    pass


def generate_json(prompt: str, system: str = "", temperature: float = 0.1) -> dict:
    """
    Calls the Groq API and asks for structured JSON output via
    response_format={"type": "json_object"}. Retries once with a
    stricter reminder if parsing fails.
    """
    if not GROQ_API_KEY:
        raise GroqError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys "
            "and set it as an environment variable before running this script."
        )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }

    for attempt in range(2):
        try:
            resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        except requests.exceptions.ConnectionError as e:
            raise GroqError("Could not reach Groq's API. Check your internet connection.") from e

        if resp.status_code == 401:
            raise GroqError("Groq rejected the API key (401 Unauthorized). Double check GROQ_API_KEY.")
        if resp.status_code == 429:
            raise GroqError(
                "Hit Groq's free-tier rate limit (429). Wait a bit and try again, "
                "or slow down how many emails you process per run."
            )
        resp.raise_for_status()

        raw_text = resp.json()["choices"][0]["message"]["content"]

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            if attempt == 0:
                payload["messages"][-1]["content"] = (
                    prompt
                    + "\n\nIMPORTANT: Respond with ONLY valid JSON. "
                    "No markdown fences, no explanation, no extra text."
                )
                continue
            raise GroqError(
                f"Model did not return valid JSON after 2 attempts. Raw output:\n{raw_text}"
            )























