"""
Level 1 agent: given one email, decide:
  - category   (Work / Personal / Finance / Job / Newsletter / Spam)
  - urgency    (Low / Medium / High)
  - action_required (true/false)
  - reasoning  (short explanation, for transparency/debugging)

This is deliberately the *simplest* possible agent: one LLM call, no tools,
no memory. Levels 2+ build on top of this.
"""

from ollama_client import generate_json

CATEGORIES = ["Work", "Personal", "Finance", "Job", "Newsletter", "Spam"]

SYSTEM_PROMPT = f"""You are an email triage assistant. Classify each email precisely.

Valid categories: {", ".join(CATEGORIES)}
Valid urgency levels: Low, Medium, High

Respond with ONLY a JSON object in this exact shape:
{{
  "category": "<one of the valid categories>",
  "urgency": "<Low|Medium|High>",
  "action_required": <true|false>,
  "reasoning": "<one short sentence explaining the classification>"
}}
"""


def classify_email(email: dict) -> dict:
    prompt = f"""Classify this email:

From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}
"""
    result = generate_json(prompt=prompt, system=SYSTEM_PROMPT)

    # Basic validation — local models sometimes drift from the schema,
    # so don't trust the output blindly.
    result.setdefault("category", "Work")
    result.setdefault("urgency", "Medium")
    result.setdefault("action_required", False)
    result.setdefault("reasoning", "")

    if result["category"] not in CATEGORIES:
        result["category"] = "Work"

    if result["urgency"] not in ("Low", "Medium", "High"):
        result["urgency"] = "Medium"

    return result
