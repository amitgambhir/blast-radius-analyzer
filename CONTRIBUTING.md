# Contributing to Blast Radius Analyzer

Thank you for your interest in contributing. This document covers how to get started.

## Development Setup

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Pull Request Guidelines

- Open an issue before starting significant work
- Keep PRs focused — one feature or fix per PR
- Run `ruff check` and `ruff format` before submitting backend changes
- Ensure the three example scenarios still run end-to-end after your change
- The confidence note (`is_inferred` + ◈ marker) must remain present on all analysis outputs
- The About panel POC vs Production tab content must remain accurate

## Architecture Principles

- No database, no auth, no external storage in the POC
- All analysis passes must stream SSE events — never block
- Every ImpactNode must carry `is_inferred: bool`
- NetworkX graph traversal must happen before Claude reasoning, not after

## Reporting Issues

Use the GitHub issue templates. For security vulnerabilities, email directly rather than opening a public issue.
