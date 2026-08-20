# AI Email Management Agent — Level 1

A fake-inbox email classifier agent running on a **local model via Ollama**.
No API keys, no real inbox risk — you can break things freely.

## What it does

For every email in `emails/`, the agent decides:
- **category**: Work / Personal / Finance / Job / Newsletter / Spam
- **urgency**: Low / Medium / High
- **action_required**: true/false
- **reasoning**: one-sentence explanation

This is intentionally the simplest possible agent — one LLM call per email,
no tools, no memory yet. Levels 2+ (summarizer, tool calling, autonomous
workflow, memory, multi-agent) build on top of this foundation.

## Setup

### 1. Install Ollama
Download from https://ollama.com (Mac/Windows/Linux all supported).

### 2. Pull a model
```bash
ollama pull llama3.1:8b
```
Any instruction-tuned model works — `qwen2.5:7b` and `mistral:7b` are good
alternatives if `llama3.1:8b` is too slow/large for your machine. Smaller
models (`llama3.2:3b`) will run faster but classify less reliably.

### 3. Start Ollama (if not already running as a service)
```bash
ollama serve
```

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the agent
```bash
python main.py
```

## Configuration

Environment variables (optional):
- `OLLAMA_HOST` — default `http://localhost:11434`
- `OLLAMA_MODEL` — default `llama3.1:8b`

Example using a different model:
```bash
OLLAMA_MODEL=qwen2.5:7b python main.py
```

## Project structure

```
email-agent/
├── emails/              # fake inbox — 6 sample emails covering every category
│   ├── email_001.json
│   └── ...
├── ollama_client.py      # HTTP wrapper around local Ollama API, forces JSON output
├── classifier.py         # the actual "agent" — one function, one LLM call
├── main.py                # loads inbox, runs classifier, prints + saves results
├── requirements.txt
└── results.json           # generated after running — full classification output
```

## Try it yourself

- Add your own email to `emails/` (copy the JSON shape) and re-run.
- Try a smaller/larger model and compare classification quality.
- Break the JSON parsing on purpose (lower-quality model) and watch the
  retry logic in `ollama_client.py` kick in.

## What's next (Level 2+)

Once this feels solid:
- **Level 2 — Summarizer**: feed it a long thread instead of one email,
  extract action items / deadlines / people involved.
- **Level 3 — Tool calling**: give the agent `search_emails()`,
  `create_task()`, `search_calendar()` and let it decide when to call them.
- **Level 4 — Autonomous workflow**: "Schedule a meeting with Rahul next
  week" → agent chains multiple tool calls together.
- **Level 5 — Memory**: agent remembers preferences ("Rahul prefers
  afternoon meetings") across runs.
- **Level 6 — Multi-agent**: a supervisor routes work to specialized
  Email / Calendar / Task agents.

Say the word when you're ready for Level 2 and I'll build it on top of this.
