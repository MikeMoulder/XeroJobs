# XeroJobs

A lightweight job-search assistant built on top of the Sentient Agent Framework. XeroJobs is an agent that analyzes user prompts to determine if the user is looking for a job, extracts search parameters (keywords, location, radius, salary), queries a job API, and streams structured results back to the client.

This repository contains the core agent logic, helper modules for analysis and job-API calls, and streaming response helpers.

## Table of contents

- About
- Features
- Repository layout
- Requirements
- Environment variables
- Quickstart — clone, setup, run
- How conversation history (previous interactions) is obtained
- Extending / persistence options
- Development notes
- Troubleshooting

## About

XeroJobs is an experimental assistant focused on job search and career-related queries. It integrates with an LLM backend (via OpenRouter/OpenAI-compatible clients) and a job search API to find and format job listings for the user.

## Features

- Intent analysis to determine whether the user is searching for jobs
- Structured JSON outputs describing required search parameters
- Query to a job-search API (example: Jooble) with conditional parameter inclusion
- Streaming, chunked responses for final result formatting
- Helpers to extract recent conversational context from the session interaction history

## Repository layout

Top-level files

- `README.md` — this file

Source code

- `Xero Jobs/src/agents.py` — main agent implementation and server runner (creates `JobAgent` and starts `DefaultServer`).
- `Xero Jobs/src/analyzer.py` — prompt analysis code, helpers for extracting context from `Session.get_interactions()` and building LLM prompts.
- `Xero Jobs/src/call_jobs.py` — example code that calls a job search API (Jooble) and returns the raw results.
- `Xero Jobs/src/general.py` — fallback/general job-related query code that also demonstrates streaming LLM completions.
- `Xero Jobs/src/stream_response.py` — formats job API results via LLM streaming to produce user-friendly output.

The project depends on `sentient_agent_framework` as the agent runtime and uses OpenAI/OpenRouter-compatible client libraries for LLM access.

## Requirements

- Python 3.10+ (recommended)
- The project expects these Python packages (install with pip):

	- `openai` or the OpenAI-compatible client used in this repo (the code imports `openai.AsyncOpenAI` and `openai.OpenAI`)
	- `python-dotenv` (for loading `.env` file values)
	- `sentient_agent_framework` (the agent runtime this project uses)

Because there is no `requirements.txt` currently committed, install packages manually (instructions below).

## Environment variables

Create a `.env` file in the repository root (or export env vars in your shell) with the following keys:

- `OPENROUTER_API_KEY` — API key for the OpenRouter/OpenAI-compatible service used by the `openai` client in this repo.
- `JOBBLE_API_KEY` — (optional) API key for the job search service (the code references `JOBBLE_API_KEY` / `jooble.org`). Adjust as required by your job API provider.

Example `.env` file:

```
OPENROUTER_API_KEY=sk-...
JOBBLE_API_KEY=your_jooble_key_here
```

Note: The code references the environment variable `JOBBLE_API_KEY` (in `call_jobs.py`) when making the Jooble request. Ensure the name matches your provider's key or update the code accordingly.

## Quickstart — clone, setup, run

These commands assume you're using Bash on Windows (WSL, Git Bash, or Git for Windows). Run them from a terminal in the folder where you want to clone the repository.

1) Clone the repository

```bash
git clone https://github.com/<your-username>/XeroJobs.git
cd "Xero Jobs"
```

2) Create and activate a Python virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows `cmd.exe` you would run:

```bash
.venv\Scripts\activate
```

3) Install dependencies (example)

```bash
pip install --upgrade pip
pip install openai python-dotenv
# install sentient_agent_framework according to its installation instructions
```

If you have a private wheel or alternate package name for `sentient_agent_framework`, install it in the same environment.

4) Create `.env` with keys (see above).

5) Run the agent server

```bash
python "Xero Jobs/src/agents.py"
```

When run, `agents.py` constructs a `JobAgent`, wraps it in a `DefaultServer`, and calls `server.run()` — check console output for logs from the agent and the LLM client.

## How conversation history (previous interactions) is obtained

This project uses the `sentient_agent_framework` `Session` object to obtain past interactions via `session.get_interactions()`:

- `session.get_interactions()` may return either a Python `list` or an async iterable of interaction objects, depending on the platform's implementation.
- `Xero Jobs/src/analyzer.py` already includes a helper `get_recent_context(interactions, depth=5)` that converts recent interactions into a compact list of text lines ("User: ...", "Assistant: ...").
- There is also an `async get_interaction(session)` helper that resolves `session.get_interactions()` into a list, prints debug info, and returns a combined context string.

How to enable conversation-aware prompts (minimal change):

1. In `Xero Jobs/src/analyzer.py`, modify `analyze_prompt()` and `generalQuery()` to call the context helper and include it in the LLM prompt. For example:

```python
# inside analyze_prompt
context = await get_interaction(session)
user_prompt = f"Context: {context}\nUser: {new_prompt}"
```

2. Similarly in `generalQuery()`:

```python
context = await get_interaction(session)
user_prompt = f"Context: {context}\nUser: {prompt}"
```

The `get_interaction()` helper already returns a string built from the last 5 exchanges by default. This is the low-friction way to feed previous interactions to your LLM prompt.

Edge cases to consider:

- Token budgets: Trim the number of interactions or characters included (your helper accepts a `depth` parameter).
- Streaming responses: Some interactions are partial deltas — ensure you use the final assistant text or aggregate deltas.
- Privacy: Avoid sending PII to third-party LLM services; sanitize or redact sensitive fields before including them.

## Persisting history across sessions (optional)

If you want history to survive process restarts (so previous user-agent interactions remain available later), add a persistence layer. Simple options:

- File-based logs: append compact JSON objects (session id, timestamp, role, text) to a per-session file.
- SQLite: create a table (`interactions`) with columns for `session_id`, `ts`, `role`, `content`, `metadata` and insert entries when requests/responses occur. Query the last N rows for a session when building context.
- Redis: quick in-memory store for active session histories, but you'll need a backing store for long-term history.

Where to hook persistence:

- Wrap or extend the `ResponseHandler` so every `emit_text_block`, `emit_json`, `emit_chunk`, and incoming `query.prompt` also writes a compact record to your store with the `session.id`.
- If the `sentient_agent_framework` provides lifecycle hooks (on_request/on_response), prefer those.

## Development notes

- The code imports `openai.AsyncOpenAI` / `openai.OpenAI` and uses `openrouter.ai` as the `base_url`. If you swap providers, adjust the client initialization accordingly.
- `call_jobs.py` currently constructs a POST to `jooble.org`. Confirm the endpoint path and the API key name for your provider. The code uses `JOBBLE_API_KEY` env var; rename if necessary.
- There are multiple places where `context = ""` is commented out. Re-enabling the `await get_interaction(session)` calls will make prompts context-aware.

## Troubleshooting

- If you get import errors for `sentient_agent_framework`, ensure the package is installed in the active virtual environment and the import path matches the package name/version you installed.
- If the LLM client fails with authentication errors, check `OPENROUTER_API_KEY` and that the `base_url` used in the code matches the provider's endpoint.
- If job API requests fail, verify the host and API key (`JOBBLE_API_KEY`) and confirm required request headers and JSON body format for your provider.

## Next steps / suggestions

- Wire `get_interaction(session)` into `analyze_prompt()` and `generalQuery()` to enable immediate conversation-aware prompts.
- Add optional persistence (SQLite) if you want history across restarts.
- Add tests to validate `get_recent_context()` behavior with the different `Interaction` shapes returned by `sentient_agent_framework`.

If you want, I can make the minimal code edits now (uncomment/wire `get_interaction` into `analyze_prompt` and `generalQuery`) and add a tiny test demonstrating context extraction.

---

Generated on 2025-11-05 — please adapt API key names and provider endpoints to match your actual accounts.
