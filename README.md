# ✦ MailMind — AI Email Management Agent

An AI-powered email management agent that turns email conversations into
structured information and actionable tasks.

MailMind starts with a simple email classifier and progressively evolves
into an agent capable of understanding complete email threads, extracting
action items and deadlines, generating calendar events, and drafting
follow-up emails.

The project is intentionally built in levels so that each stage teaches a
different concept in Agentic AI.

---

## 🚀 Current Capabilities

### Level 1 — Email Triage

Classifies individual emails based on:

- **Category** — Work / Personal / Finance / Job / Newsletter / Spam
- **Urgency** — Low / Medium / High
- **Action Required** — true / false
- **Reasoning** — one-sentence explanation

### Agent Architecture
                    ┌──────────────────┐
                    │    Email Inbox   │
                    └────────┬─────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │   Email Classifier   │
                 │       Level 1       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Email Threads     │
                 │       Level 2       │
                 └──────────┬───────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │    Thread Summarizer        │
              │                             │
              │ • Summary                   │
              │ • People                    │
              │ • Action Items              │
              │ • Deadlines                 │
              │ • Decisions                 │
              │ • Pending Questions         │
              │ • Priority                  │
              └──────────────┬──────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
       ┌─────────────────┐       ┌──────────────────┐
       │ Calendar Action │       │ Follow-up Agent  │
       │                 │       │                  │
       │ Generate .ics   │       │ Draft email      │
       └─────────────────┘       └──────────────────┘

---

### Level 2 — Thread Intelligence

Instead of analyzing a single email, MailMind can analyze an entire
conversation thread.

It extracts:

- **Thread summary**
- **People involved**
- **Action items**
- **Action owners**
- **Deadlines**
- **Decisions**
- **Pending questions**
- **Priority**

Example:

```text
Thread:
"Client Demo Preparation"

AI Summary:
The team is preparing for a client demo scheduled for Friday.

Action Items:
• Rahul → Complete API integration → Wednesday
• Sanchitha → Update presentation → Thursday
• Priya → Confirm attendees → Before Friday

Decision:
• Client demo confirmed for Friday at 3 PM.

Priority:
High

