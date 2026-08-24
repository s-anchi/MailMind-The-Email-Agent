import re
from datetime import datetime, timedelta

from groq_client import generate_json


# =========================================================
# Date Helpers
# =========================================================

def resolve_deadline(deadline_text):
    """
    Convert common natural-language deadlines into a date.

    Examples:
        Wednesday -> next Wednesday
        Friday -> next Friday
        2026-08-28 -> 2026-08-28

    Returns:
        datetime.date or None
    """

    if not deadline_text:
        return None

    text = deadline_text.strip().lower()

    today = datetime.now().date()

    # -----------------------------------------------------
    # ISO date: 2026-08-28
    # -----------------------------------------------------

    iso_match = re.search(
        r"\b(\d{4})-(\d{2})-(\d{2})\b",
        text
    )

    if iso_match:
        try:
            return datetime.strptime(
                iso_match.group(0),
                "%Y-%m-%d"
            ).date()
        except ValueError:
            pass

    # -----------------------------------------------------
    # Weekdays
    # -----------------------------------------------------

    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    for day_name, day_number in weekdays.items():

        if day_name in text:

            days_ahead = (
                day_number - today.weekday()
            ) % 7

            # If the deadline is mentioned as
            # "today", don't move it forward.
            if days_ahead == 0 and "next" in text:
                days_ahead = 7

            return today + timedelta(
                days=days_ahead
            )

    return None


# =========================================================
# Calendar
# =========================================================

def create_calendar_event(
    task,
    deadline,
    owner=None,
    subject=None
):
    """
    Creates an all-day ICS calendar event.

    Returns:
        ICS content as a string.
    """

    event_date = resolve_deadline(
        deadline
    )

    if event_date is None:
        raise ValueError(
            f"Could not understand deadline: {deadline}"
        )

    event_title = task

    if subject:
        event_title = (
            f"{task} — {subject}"
        )

    date_string = event_date.strftime(
        "%Y%m%d"
    )

    created_at = datetime.utcnow().strftime(
        "%Y%m%dT%H%M%SZ"
    )

    description = (
        f"Action item: {task}\\n"
        f"Deadline: {deadline}"
    )

    if owner:
        description += (
            f"\\nOwner: {owner}"
        )

    if subject:
        description += (
            f"\\nEmail thread: {subject}"
        )

    # Escape ICS special characters
    event_title = event_title.replace(
        ",",
        "\\,"
    )

    event_title = event_title.replace(
        ";",
        "\\;"
    )

    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI Email Agent//EN
BEGIN:VEVENT
UID:email-agent-{created_at}@local
DTSTAMP:{created_at}
DTSTART;VALUE=DATE:{date_string}
DTEND;VALUE=DATE:{date_string}
SUMMARY:{event_title}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR
"""

    return ics


# =========================================================
# Follow-up Draft
# =========================================================

FOLLOWUP_SYSTEM_PROMPT = """
You are an email follow-up assistant.

Draft a concise, professional follow-up email based on an email
thread and a specific action item.

Rules:

1. Do not invent facts.
2. Do not invent dates.
3. Do not claim that something is completed unless the thread says so.
4. Clearly reference the relevant action item.
5. Keep the email concise.
6. Be polite but direct.
7. If the action is overdue or pending, ask for a status update.
8. If the action has not reached its deadline, make the tone a reminder
   rather than an escalation.

Return ONLY valid JSON:

{
    "recipient": "email address or null",
    "subject": "email subject",
    "body": "complete email body"
}
"""


def draft_followup(
    thread,
    action_item
):
    """
    Generate a follow-up email for a specific action item.
    """

    messages = thread.get(
        "messages",
        []
    )

    thread_text = []

    for index, message in enumerate(
        messages,
        start=1
    ):

        thread_text.append(
            f"""
--- Message {index} ---
From: {message.get('from', '')}
Subject: {message.get('subject', '')}

{message.get('body', '')}
"""
        )

    action_text = f"""
Task: {action_item.get('task', '')}
Owner: {action_item.get('owner') or 'Unknown'}
Deadline: {action_item.get('deadline') or 'No deadline'}
Status: {action_item.get('status', 'pending')}
"""

    prompt = f"""
Here is the email thread:

{"".join(thread_text)}

Here is the action item that needs a follow-up:

{action_text}

Draft an appropriate follow-up email.
"""

    return generate_json(
        prompt=prompt,
        system=FOLLOWUP_SYSTEM_PROMPT,
        temperature=0.2
    )