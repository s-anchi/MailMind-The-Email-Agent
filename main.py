"""
Runs the Level 1 classifier agent over every email in emails/,
prints a triage summary, and saves results to results.json.

Usage:
    python main.py
"""

import glob
import json
import os
import sys

from classifier import classify_email
from groq_client import GroqError, GROQ_MODEL

EMAILS_DIR = os.path.join(os.path.dirname(__file__), "emails")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.json")

URGENCY_ICON = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}


def load_inbox():
    paths = sorted(glob.glob(os.path.join(EMAILS_DIR, "*.json")))
    emails = []
    for path in paths:
        with open(path) as f:
            emails.append(json.load(f))
    return emails


def main():
    emails = load_inbox()
    if not emails:
        print(f"No emails found in {EMAILS_DIR}")
        return

    print(f"Using model: {GROQ_MODEL}")
    print(f"Loaded {len(emails)} emails from fake inbox\n")
    print("-" * 70)

    results = []
    for email in emails:
        print(f"Processing {email['id']}: \"{email['subject']}\"...")
        try:
            classification = classify_email(email)
        except GroqError as e:
            print(f"  ERROR: {e}")
            sys.exit(1)

        results.append({**email, **classification})

        icon = URGENCY_ICON.get(classification["urgency"], "⚪")
        print(f"  {icon} {classification['category']} | urgency={classification['urgency']} "
              f"| action_required={classification['action_required']}")
        print(f"  reasoning: {classification['reasoning']}")
        print("-" * 70)

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    urgent = sum(1 for r in results if r["urgency"] == "High")
    needs_action = sum(1 for r in results if r["action_required"])
    print(f"\nSummary: {urgent} urgent | {needs_action} need action | {len(results)} total")
    print(f"Full results saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
