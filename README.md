# XeroJobs

A sophisticated job-search agent built on top of the Sentient Agent Framework. XeroJobs is an agent that analyzes user prompts to determine if the user is looking for a job, extracts search parameters, queries a job API, and streams structured results back to the client. It is designed to assist the user with all forms of carrer assistant, be it career tips, jobs recommendations, interview preparations.

This repository contains the core agent logic, helper modules for analysis and job-API calls, and streaming response helpers.

## Table of contents

- About
- Features
- Repository layout
- Requirements
- Environment variables
- Quickstart — clone, setup, run
- Testing

## About

XeroJobs is an experimental assistant focused on job search and career-related queries. It runs on the Sentient Agent Framework which makes it ready for integration into Sentient Chat.

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

## Environment variables

Open the `.env` file in the repository at ./XeroJobs and supply the required API keys:

Example `.env` file:

```
OPENROUTER_API_KEY=sk-...
JOBBLE_API_KEY=your_jooble_key_here
```

## Quickstart — clone, setup, run

These commands assume you're using Bash on Windows (WSL, Git Bash, or Git for Windows). Run them from a terminal in the folder where you want to clone the repository.

1) Clone the repository

```bash
git clone https://github.com/MikeMoulder/XeroJobs.git
cd "Xero Jobs"
```

2) Create and activate a Python virtual environment

On Mac, you would run:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows, you would run:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3) Install dependencies (example)

```bash
pip install --upgrade pip
cd 'Xero Jobs'
pip install -r requirements.txt
```

4) Create `.env` with keys (see above).

5) Run the agent server

```bash
python "Xero Jobs/src/agents.py"
```

When run, `agents.py` constructs a `JobAgent`, wraps it in a `DefaultServer`, and calls `server.run()` — check console output for logs from the agent and the LLM client.

## Testing

You can test this agent using the official `Sentient Agent Framework`, you can clone the official repo using the link below
- Link: https://github.com/sentient-agi/Sentient-Agent-Client

That will be all for now, if you have any question, you can reach me at:
- xero.dev.ai@gmail.com
- mike.moulder.dev@gmail.ocm
- https://x.com/moulderofweb3
