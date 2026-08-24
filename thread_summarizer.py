"""
Level 2 agent: summarize an entire email thread.

Extracts:
- overall summary
- people involved
- action items
- deadlines
- decisions
- pending questions
- priority
"""

from groq_client import generate_json


SYSTEM_PROMPT = """
You are an intelligent email thread summarization agent.

You will receive an entire email thread containing multiple messages.

Your job is to understand the conversation as a whole and extract
important information.

IMPORTANT RULES:

1. Do not treat every statement as an action item.
2. Only create an action item when someone explicitly asks someone
   to do something or clearly commits to doing something.
3. Identify who is responsible for each action whenever possible.
4. Extract deadlines exactly as stated in the email.
5. Do not invent deadlines.
6. Distinguish between completed and pending actions.
7. Identify decisions that were actually agreed upon.
8. Identify questions that are still unanswered.
9. If information is unknown, use null or an empty list.
10. Do not invent people, dates, tasks, or decisions.

Return ONLY valid JSON in this exact structure:

{
  "summary": "2-4 sentence summary of the entire thread",

  "people": [
    {
      "name": "person name",
      "email": "email if available",
      "role": "their role in the conversation"
    }
  ],

  "action_items": [
    {
      "task": "what needs to be done",
      "owner": "person responsible or null",
      "deadline": "deadline exactly as stated or null",
      "status": "pending|completed"
    }
  ],

  "deadlines": [
    {
      "description": "what the deadline is for",
      "date": "deadline exactly as stated",
      "owner": "person responsible or null"
    }
  ],

  "decisions": [
    "decision that was agreed upon"
  ],

  "pending_questions": [
    "question that remains unanswered"
  ],

  "priority": "Low|Medium|High"
}
"""


def format_thread(thread: list[dict]) -> str:
    """Convert a list of emails into readable conversation text."""

    messages = []

    for i, email in enumerate(thread, start=1):
        messages.append(
            f"""
--- Message {i} ---
From: {email.get('from', '')}
Subject: {email.get('subject', '')}
Received: {email.get('received_at', '')}

{email.get('body', '')}
"""
        )

    return "\n".join(messages)


def summarize_thread(thread: list[dict]) -> dict:
    """
    Summarize an entire email thread with one LLM call.
    """

    if not thread:
        raise ValueError("Cannot summarize an empty thread.")

    thread_text = format_thread(thread)

    prompt = f"""
Analyze the following email thread.

{thread_text}

Return the complete structured JSON response requested in your
system instructions.
"""

    result = generate_json(
        prompt=prompt,
        system=SYSTEM_PROMPT,
        temperature=0.1,
    )

    # Defensive defaults
    result.setdefault("summary", "")
    result.setdefault("people", [])
    result.setdefault("action_items", [])
    result.setdefault("deadlines", [])
    result.setdefault("decisions", [])
    result.setdefault("pending_questions", [])
    result.setdefault("priority", "Medium")

    if result["priority"] not in ("Low", "Medium", "High"):
        result["priority"] = "Medium"

    return result