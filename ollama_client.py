"""
Thin wrapper around the local Ollama HTTP API.

Ollama runs at http://localhost:11434 by default once you've done:
    ollama serve
    ollama pull llama3.1:8b   (or whatever OLLAMA_MODEL is set to)
"""

import json
import os
import requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")


class OllamaError(Exception):
    pass


def generate_json(prompt: str, system: str = "", temperature: float = 0.1) -> dict:
    """
    Calls the local model and forces structured JSON output using Ollama's
    `format: "json"` mode. Retries once with a stricter reminder if the
    first response isn't valid JSON — local models are less reliable at
    this than hosted frontier models, so don't assume the first try works.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system,
        "format": "json",
        "stream": False,
        "options": {"temperature": temperature},
    }

    for attempt in range(2):
        try:
            resp = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=120)
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise OllamaError(
                f"Could not reach Ollama at {OLLAMA_HOST}. "
                f"Is it running? Try `ollama serve` in another terminal."
            ) from e

        raw_text = resp.json().get("response", "")

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            if attempt == 0:
                # Second attempt: make the instruction more forceful
                payload["prompt"] = (
                    prompt
                    + "\n\nIMPORTANT: Respond with ONLY valid JSON. "
                    "No markdown fences, no explanation, no extra text."
                )
                continue
            raise OllamaError(
                f"Model did not return valid JSON after 2 attempts. Raw output:\n{raw_text}"
            )
