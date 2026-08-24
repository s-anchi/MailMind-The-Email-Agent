"""
Runs the email agent.

Level 1:
    Classifies every email in emails/

Level 2:
    Summarizes complete email threads from threads/

Usage:
    python main.py email
    python main.py thread
"""

import glob
import json
import os
import sys

from classifier import classify_email
from thread_summarizer import summarize_thread
from groq_client import GroqError, GROQ_MODEL


BASE_DIR = os.path.dirname(__file__)

EMAILS_DIR = os.path.join(BASE_DIR, "emails")
THREADS_DIR = os.path.join(BASE_DIR, "threads")

RESULTS_PATH = os.path.join(BASE_DIR, "results.json")
THREAD_RESULTS_PATH = os.path.join(BASE_DIR, "thread_results.json")


URGENCY_ICON = {
    "High": "🔴",
    "Medium": "🟡",
    "Low": "🟢",
}


def load_inbox():
    """Load individual emails from emails/."""

    paths = sorted(
        glob.glob(os.path.join(EMAILS_DIR, "*.json"))
    )

    emails = []

    for path in paths:
        with open(path, encoding="utf-8") as f:
            emails.append(json.load(f))

    return emails


def load_threads():
    """Load complete email threads from threads/."""

    paths = sorted(
        glob.glob(os.path.join(THREADS_DIR, "*.json"))
    )

    threads = []

    for path in paths:
        with open(path, encoding="utf-8") as f:
            threads.append(json.load(f))

    return threads


def run_email_classifier():
    """Level 1: classify individual emails."""

    emails = load_inbox()

    if not emails:
        print(f"No emails found in {EMAILS_DIR}")
        return

    print(f"Using model: {GROQ_MODEL}")
    print(f"Loaded {len(emails)} emails from fake inbox\n")
    print("-" * 70)

    results = []

    for email in emails:

        print(
            f"Processing {email['id']}: "
            f"\"{email['subject']}\"..."
        )

        try:
            classification = classify_email(email)

        except GroqError as e:
            print(f"  ERROR: {e}")
            sys.exit(1)

        results.append({
            **email,
            **classification
        })

        icon = URGENCY_ICON.get(
            classification["urgency"],
            "⚪"
        )

        print(
            f"  {icon} "
            f"{classification['category']} "
            f"| urgency={classification['urgency']} "
            f"| action_required="
            f"{classification['action_required']}"
        )

        print(
            f"  reasoning: "
            f"{classification['reasoning']}"
        )

        print("-" * 70)

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    # Summary
    urgent = sum(
        1
        for r in results
        if r["urgency"] == "High"
    )

    needs_action = sum(
        1
        for r in results
        if r["action_required"]
    )

    print(
        f"\nSummary: "
        f"{urgent} urgent | "
        f"{needs_action} need action | "
        f"{len(results)} total"
    )

    print(
        f"Full results saved to {RESULTS_PATH}"
    )


def run_thread_summarizer():
    """Level 2: summarize complete email threads."""

    threads = load_threads()

    if not threads:
        print(f"No threads found in {THREADS_DIR}")
        print(
            "\nCreate a threads/ folder and add "
            "thread JSON files."
        )
        return

    print(f"Using model: {GROQ_MODEL}")
    print(
        f"Loaded {len(threads)} email threads\n"
    )

    print("-" * 70)

    results = []

    for thread in threads:

        thread_id = thread.get(
            "thread_id",
            "unknown"
        )

        subject = thread.get(
            "subject",
            "No subject"
        )

        messages = thread.get(
            "messages",
            []
        )

        print(
            f"Processing {thread_id}: "
            f"\"{subject}\"..."
        )

        print(
            f"  Messages in thread: "
            f"{len(messages)}"
        )

        try:
            summary = summarize_thread(messages)

        except GroqError as e:
            print(f"  ERROR: {e}")
            sys.exit(1)

        except Exception as e:
            print(
                f"  ERROR while summarizing "
                f"thread: {e}"
            )
            sys.exit(1)

        result = {
            "thread_id": thread_id,
            "subject": subject,
            **summary,
        }

        results.append(result)

        # Print summary
        print("\n  📌 Summary:")
        print(
            f"  {summary.get('summary', '')}"
        )

        # Print people
        print("\n  👥 People involved:")

        people = summary.get("people", [])

        if people:
            for person in people:
                name = person.get(
                    "name",
                    "Unknown"
                )

                role = person.get(
                    "role",
                    ""
                )

                if role:
                    print(
                        f"    • {name} — {role}"
                    )
                else:
                    print(
                        f"    • {name}"
                    )
        else:
            print("    • None identified")

        # Print action items
        print("\n  ✅ Action items:")

        action_items = summary.get(
            "action_items",
            []
        )

        if action_items:

            for item in action_items:

                task = item.get(
                    "task",
                    "Unknown task"
                )

                owner = item.get(
                    "owner"
                ) or "Unassigned"

                deadline = item.get(
                    "deadline"
                ) or "No deadline"

                status = item.get(
                    "status",
                    "pending"
                )

                print(
                    f"    • {task}"
                )

                print(
                    f"      Owner: {owner}"
                )

                print(
                    f"      Deadline: {deadline}"
                )

                print(
                    f"      Status: {status}"
                )

        else:
            print("    • No action items")

        # Print deadlines
        print("\n  ⏰ Deadlines:")

        deadlines = summary.get(
            "deadlines",
            []
        )

        if deadlines:

            for deadline in deadlines:

                description = deadline.get(
                    "description",
                    ""
                )

                date = deadline.get(
                    "date",
                    ""
                )

                owner = deadline.get(
                    "owner"
                ) or "Unassigned"

                print(
                    f"    • {description}"
                )

                print(
                    f"      Date: {date}"
                )

                print(
                    f"      Owner: {owner}"
                )

        else:
            print("    • No deadlines identified")

        # Print decisions
        print("\n  🎯 Decisions:")

        decisions = summary.get(
            "decisions",
            []
        )

        if decisions:

            for decision in decisions:
                print(
                    f"    • {decision}"
                )

        else:
            print("    • No decisions identified")

        # Print pending questions
        print("\n  ❓ Pending questions:")

        questions = summary.get(
            "pending_questions",
            []
        )

        if questions:

            for question in questions:
                print(
                    f"    • {question}"
                )

        else:
            print("    • None")

        # Priority
        priority = summary.get(
            "priority",
            "Medium"
        )

        print(
            f"\n  Priority: {priority}"
        )

        print("-" * 70)

    # Save all thread results
    with open(
        THREAD_RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    # Final summary
    total_action_items = sum(
        len(r.get("action_items", []))
        for r in results
    )

    total_deadlines = sum(
        len(r.get("deadlines", []))
        for r in results
    )

    high_priority = sum(
        1
        for r in results
        if r.get("priority") == "High"
    )

    print("\nThread Summary")
    print("=" * 70)

    print(
        f"Threads processed: {len(results)}"
    )

    print(
        f"Action items found: "
        f"{total_action_items}"
    )

    print(
        f"Deadlines found: "
        f"{total_deadlines}"
    )

    print(
        f"High priority threads: "
        f"{high_priority}"
    )

    print(
        f"\nFull thread results saved to "
        f"{THREAD_RESULTS_PATH}"
    )


def main():
    """Select which level of the agent to run."""

    mode = (
        sys.argv[1].lower()
        if len(sys.argv) > 1
        else "email"
    )

    if mode == "email":

        run_email_classifier()

    elif mode == "thread":

        run_thread_summarizer()

    else:

        print("Invalid mode.")
        print("\nUsage:")
        print("  python main.py email")
        print("  python main.py thread")


if __name__ == "__main__":
    main()