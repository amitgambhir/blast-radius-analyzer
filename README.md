<div align="center">

# 💥 Blast Radius Analyzer

**Map the impact of your decisions before they map you.**

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev)
[![LLM Agnostic](https://img.shields.io/badge/LLM-provider--agnostic-8b5cf6.svg)](#configuration)
[![Works with Claude](https://img.shields.io/badge/works%20with-Claude-d97706.svg)](https://anthropic.com)
[![Works with OpenAI](https://img.shields.io/badge/works%20with-OpenAI-412991.svg)](https://openai.com)

</div>

---

## Table of Contents

1. [The Problem](#the-problem)
2. [What It Does](#what-it-does)
3. [Demo](#demo)
4. [Key Features](#key-features)
5. [Built On](#built-on)
6. [Quick Start](#quick-start)
7. [How It Works — The 5-Pass Engine](#how-it-works--the-5-pass-engine)
8. [Architecture](#architecture)
9. [The 3 Example Scenarios](#the-3-example-scenarios)
10. [Step-by-Step Guide](#step-by-step-guide)
    - [Step 1 — Set Up Your Environment](#step-1--set-up-your-environment)
    - [Step 2 — Start the Backend](#step-2--start-the-backend)
    - [Step 3 — Start the Frontend](#step-3--start-the-frontend)
    - [Step 4 — Load an Example Scenario](#step-4--load-an-example-scenario)
    - [Step 5 — Analyze Your Own Decision](#step-5--analyze-your-own-decision)
    - [Step 6 — Use the API Directly](#step-6--use-the-api-directly)
    - [Step 7 — Run the Test Suite](#step-7--run-the-test-suite)
11. [Understanding Risk Verdicts](#understanding-risk-verdicts)
12. [Understanding the Graph](#understanding-the-graph)
13. [POC vs Production: Bridging the Gap](#poc-vs-production-bridging-the-gap)
14. [Key Design Decisions](#key-design-decisions)
15. [Extending the System](#extending-the-system)
16. [API Reference](#api-reference)
17. [Key Files](#key-files)
18. [Configuration](#configuration)
19. [Contributing](#contributing)

---

## The Problem

Every week, engineering organizations make decisions that seem contained but aren't.

A database migration becomes an auth outage. An API deprecation breaks a partner integration nobody remembered was still running. A team reorg creates an undocumented ownership gap that surfaces as a 3am incident six weeks later.

The blast radius of these decisions is predictable — if you look. The dependencies are in your service graph. The human impacts are in your org chart. The risk patterns are in your incident history. **The problem isn't that the information doesn't exist. It's that nobody sits down and traces all the second and third-order impacts before the change is approved.**

Most analysis tools stop at technical impact. They tell you which services break. They don't tell you which team is now overloaded, which Q3 roadmap just slipped, or which SLA commitment is now at risk.

This tool does all of that.

---

## What It Does

Blast Radius Analyzer is an open-source AI tool that runs a 5-pass sequential reasoning chain on your system description and proposed decision, then maps every technical and organizational impact — including the ones you didn't know to ask about.

```
Input:  Services + Dependencies + Teams + Decision
Output: An interactive blast radius map with risk scores, recommended actions,
        and a confidence-grounded executive summary
```

### What Gets Analyzed

| Pass | What It Does |
|------|-------------|
| **Decision Classification** | Identifies the decision class, risk category, playbook applicability, and key concerns |
| **First-Order Technical Impact** | Maps direct + 1-hop service impacts using real graph traversal |
| **Second-Order Propagation** | Traces dampened/amplified signals through the 2-hop neighborhood |
| **Organizational Impact** | Maps technical blast radius to team workload, roadmap disruption, and SLA risk |
| **Risk Scoring & Synthesis** | Scores 5 risk dimensions (technical, delivery, people, compliance, financial) and produces an executive summary |

---

## Demo

```bash
$ curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d @examples/db-migration.json | jq '.overall_verdict, .overall_risk_score'

"HIGH"
0.78

$ jq '.executive_summary' < result.json
"Migrating the auth database to Aurora during a maintenance window poses HIGH risk.
The hard dependency from session-manager — an undocumented direct DB connection —
creates a second blast radius that the original change plan does not address.
Three critical-path services will experience connection failures during cutover.
Recommend: audit all direct DB connections before scheduling the window,
and run a blue-green migration rather than a hard cutover."

$ jq '[.nodes[] | select(.risk_severity == "critical") | .name]' < result.json
[
  "Authentication Service",
  "Session Manager",
  "API Gateway"
]
```

---

## Key Features

- **5-pass reasoning chain** — each analysis pass receives structured JSON output of all previous passes; Pass 5 has seen everything Passes 1–4 found
- **Real graph traversal** — NetworkX directed dependency graph with betweenness centrality; not AI guessing at relationships
- **Organizational impact mapping** — maps technical blast radius to team workload, roadmap disruption, and SLA risk (the pass most tools skip entirely)
- **SSE streaming** — watch each pass complete in real time; full analysis takes 20–40 seconds
- **3 ready-to-run examples** — database migration, API deprecation, platform reorg; load and analyze in 30 seconds without entering any data
- **Interactive D3 force graph** — drag, zoom, hover for details, click to expand node; nodes sized by criticality, colored by impact severity
- **Inferred node marking** — every node inferred beyond your explicit intake is marked ◈ so you know what to verify
- **5 risk dimensions scored separately** — technical, delivery, people, compliance, financial; 0–100 each
- **Export to Markdown** — paste directly into Confluence, Notion, or a PR description

---

## Built On

- **AI model (your choice)** — the reasoning engine behind all 5 analysis passes. Defaults to Claude (`claude-sonnet-4-6`) but swappable to any OpenAI-compatible provider via a single env var
- **[NetworkX](https://networkx.org)** — directed dependency graph, hop-distance traversal, and betweenness centrality scoring
- **[FastAPI](https://fastapi.tiangolo.com)** — async Python backend with Server-Sent Events streaming
- **[React 18](https://react.dev) + [D3.js v7](https://d3js.org)** — interactive force-directed graph and results dashboard
- **[Tailwind CSS](https://tailwindcss.com)** — dark-theme UI with a mission-control aesthetic
- **[Pydantic v2](https://docs.pydantic.dev)** — request/response validation throughout

> The model provides the multi-pass reasoning. NetworkX provides the graph science.
> Blast Radius Analyzer provides the product layer that makes both usable in under a minute.

### Supported Models & Providers

| Provider | `LLM_PROVIDER` | Model env default | Notes |
|----------|---------------|-------------------|-------|
| **Anthropic** (default) | `anthropic` | `claude-sonnet-4-6` | Requires `ANTHROPIC_API_KEY` |
| **OpenAI** | `openai` | `gpt-4o` | Requires `OPENAI_API_KEY` |
| **Groq** | `openai` | set `LLM_MODEL=llama-3.3-70b-versatile` | `OPENAI_BASE_URL=https://api.groq.com/openai/v1` |
| **Together.ai** | `openai` | set `LLM_MODEL=meta-llama/Llama-3-70b-chat-hf` | `OPENAI_BASE_URL=https://api.together.xyz/v1` |
| **Ollama** (local) | `openai` | set `LLM_MODEL=llama3.2` | `OPENAI_BASE_URL=http://localhost:11434/v1`, `OPENAI_API_KEY=ollama` |
| **Azure OpenAI** | `openai` | set `LLM_MODEL=your-deployment` | `OPENAI_BASE_URL=https://<resource>.openai.azure.com/openai/deployments/<deploy>` |
| **LM Studio** | `openai` | set `LLM_MODEL=<loaded-model>` | `OPENAI_BASE_URL=http://localhost:1234/v1` |

---

## Quick Start

### Option 1: Docker (recommended)

```bash
git clone https://github.com/amitgambhir/blast-radius-analyzer
cd blast-radius-analyzer

cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

docker-compose up
```

Open [http://localhost:3001](http://localhost:3001) — click **"Load Example ▾"** → **"Database Migration"** → **"Analyze Blast Radius 💥"**

### Option 2: Local Development

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Opens on http://localhost:3001
```

**Run the test suite:**
```bash
cd backend
pytest tests/ -v
```

---

## How It Works — The 5-Pass Engine

```
  BlastRadiusRequest (services, deps, teams, decision)
         │
         ▼
  ┌─────────────┐
  │   Pass 1    │  Decision Classification
  │    (AI)     │  → decision_class, primary_risk_category,
  └──────┬──────┘    playbook_notes, key_concerns,
         │           blast_radius_prediction
         ▼
  ┌─────────────┐
  │  NetworkX   │  Build nx.DiGraph from intake
  │   Graph     │  get_first_order()  → 1-hop neighbors
  │  Traversal  │  get_second_order() → 2-hop neighbors
  └──────┬──────┘  betweenness_centrality() → hub scoring
         │
         ▼
  ┌─────────────┐
  │   Pass 2    │  First-Order Technical Impact
  │    (AI)     │  → ImpactNode[] for directly affected services
  └──────┬──────┘    + 1-hop neighbors (graph-grounded, not guessed)
         │
         ▼
  ┌─────────────┐
  │   Pass 3    │  Second-Order Propagation
  │    (AI)     │  → dampened vs amplified impact signals
  └──────┬──────┘  → propagation mechanism per 2-hop service
         │
         ▼
  ┌─────────────┐
  │   Pass 4    │  Organizational Impact Mapping
  │    (AI)     │  → team workload, roadmap disruption,
  └──────┬──────┘    SLA risk, comms overhead, process impacts
         │           (the pass most tools skip entirely)
         ▼
  ┌─────────────┐
  │   Pass 5    │  Risk Scoring & Synthesis
  │    (AI)     │  → 5 risk dimensions (0–1.0 each)
  └──────┬──────┘  → overall verdict + executive summary
         │         → immediate actions + open questions
         ▼
  BlastRadiusResult → D3 Force Graph + Scorecards + Export
```

Each pass receives the **structured JSON output of all previous passes** as context. Pass 5 has seen everything Passes 1–4 found. This produces dramatically better output than a single mega-prompt — each step constrains and informs the next.

---

## Architecture

```
blast-radius-analyzer/
├── backend/
│   ├── main.py                    FastAPI app, CORS middleware, router registration
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   │
│   ├── routers/
│   │   ├── analyze.py             POST /api/analyze/stream  (SSE, 5-pass)
│   │   │                          POST /api/analyze          (sync)
│   │   ├── examples.py            GET  /api/examples
│   │   │                          GET  /api/examples/{id}
│   │   └── health.py              GET  /health
│   │
│   ├── services/
│   │   ├── graph_builder.py       nx.DiGraph builder, get_first_order(),
│   │   │                          get_second_order(), compute_centrality()
│   │   ├── decision_classifier.py Pass 1 — model call
│   │   ├── impact_analyzer.py     Pass 2 + 3 — model calls
│   │   ├── org_mapper.py          Pass 4 — model call
│   │   └── risk_scorer.py         Pass 5 — model call + BlastRadiusResult assembly
│   │
│   ├── models/
│   │   ├── intake.py              BlastRadiusRequest, Service, Dependency, Team, Decision
│   │   └── analysis.py            BlastRadiusResult, ImpactNode, ImpactEdge, RiskDimension
│   │
│   ├── utils/
│   │   └── prompts.py             All 5 model system + user prompts, isolated
│   │
│   └── tests/
│       ├── test_graph_builder.py  8 unit tests — graph traversal, centrality, hop logic
│       ├── test_examples.py       15 parametrized tests — all 3 examples, schema integrity,
│       │                          first/second-order correctness, ownership validation
│       └── test_api_routes.py     17 integration tests — endpoints, validation (422),
│                                  full 5-pass pipeline with mocked model, SSE events,
│                                  timeout/size-limit/error-routing coverage
│
└── frontend/
    ├── Dockerfile
    ├── vite.config.js
    ├── tailwind.config.js
    └── src/
        ├── App.jsx                Two-panel layout, nav, About toggle
        ├── index.css              Dark theme, IBM Plex fonts, custom utilities
        │
        ├── hooks/
        │   └── useAnalysis.js     SSE streaming hook (fetch + ReadableStream, not EventSource)
        │
        ├── data/
        │   └── examples.js        3 pre-built example scenarios as JS objects
        │
        └── components/
            ├── IntakeForm/        Section A: Services, B: Dependencies,
            │                      C: Teams, D: Decision
            ├── BlastGraph/        D3 v7 force-directed graph, drag/zoom/hover/click
            ├── Results/           VerdictBanner, RiskDimensions, OrgImpact,
            │                      ImmediateActions, OpenQuestions, AnalysisLog, Export
            ├── AboutPanel/        "How It Works" + "POC vs Production" tabs
            ├── StreamingProgress  Pass-by-pass live progress indicator
            └── NodeDrawer.jsx     Slide-over panel for node detail on click
```

---

## The 3 Example Scenarios

Load any of these from the **"Load Example ▾"** dropdown — no data entry required.

### Example 1 — Database Migration

**Decision:** Migrating user auth database from PostgreSQL to Aurora (hard cutover)

The interesting finding: `session-manager` has an undocumented direct database connection that the original change plan doesn't account for. The analysis surfaces this as a critical-path gap and recommends a blue-green migration over a hard cutover.

*Services: 5 · Teams: 3 · Primary risk: technical + delivery · Expected verdict: HIGH*

### Example 2 — API Deprecation

**Decision:** Deprecating v1 Payments API — 90-day sunset

A payments API sunset with 3 internal consumers and 3 external partners, one of whom has a 6-month migration cycle. The 90-day timeline is compliance-driven. The analysis surfaces the partner migration conflict and the mobile release cycle constraint as delivery risks the timeline doesn't accommodate.

*Services: 7 · Teams: 4 · Primary risk: delivery + compliance · Expected verdict: HIGH*

### Example 3 — Platform Team Reorg

**Decision:** Splitting Platform team into Infrastructure and Developer Experience sub-teams

No service code changes — pure ownership transfer. Technical risk is LOW. But the organizational impact is HIGH: an unresolved ownership gap on `secrets-management`, two engineers considering leaving, and cross-cutting on-call rotations that need reconstruction. This example deliberately shows Pass 4 (org impact) as the dominant output.

*Services: 8 · Teams: 4 · Primary risk: people + delivery · Technical risk: LOW · Org risk: HIGH*

---

## Step-by-Step Guide

### Prerequisites

- Python 3.11+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)

---

### Step 1 — Set Up Your Environment

```bash
git clone https://github.com/amitgambhir/blast-radius-analyzer
cd blast-radius-analyzer

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Open .env and set ANTHROPIC_API_KEY=sk-ant-...
```

---

### Step 2 — Start the Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

Verify it's running:
```bash
curl http://localhost:8000/health
# → {"status": "ok", "service": "blast-radius-analyzer"}
```

Interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Step 3 — Start the Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3001
```

---

### Step 4 — Load an Example Scenario

1. Open [http://localhost:3001](http://localhost:3001)
2. Click **"Load Example ▾"** in the top-left of the intake form
3. Select **"Database Migration"**
4. Click **"Analyze Blast Radius 💥"**
5. Watch each of the 5 passes complete in the right panel (~20–40 seconds)
6. Explore the interactive graph — hover nodes for details, click to expand, use severity filter chips
7. Click **"Export Markdown"** to copy the full analysis to your clipboard

---

### Step 5 — Analyze Your Own Decision

Fill in the 4 sections of the intake form:

**Section A — Services**
Add each service with an ID (slug), name, owner team ID, criticality (`low`/`medium`/`high`/`critical`), and a 1–2 sentence description. The description is the most important field — it's what the model reasons about.

**Section B — Dependencies**
Add directed dependencies between services. Set type (`sync-api`, `async-event`, `database`, `cache`, `file-system`) and strength (`hard` = breaks if dependency fails, `soft` = degrades gracefully).

**Section C — Teams**
Add teams with their owned services. If you skip this section, teams are auto-derived from the `owner_team` field on each service.

**Section D — Decision**
Fill in the title, description, decision type, which services are directly affected, timeline (`immediate`/`days`/`weeks`/`months`), and reversibility.

> **Tip:** Quality of analysis is proportional to quality of context. Specific service descriptions and accurate dependency strengths produce substantially better output than generic placeholders.

---

### Step 6 — Use the API Directly

**Streaming (recommended):**
```bash
curl -N -X POST http://localhost:8000/api/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{
    "services": [
      {"id": "auth-service", "name": "Auth Service", "owner_team": "platform",
       "criticality": "critical", "description": "Handles all user authentication and session management."},
      {"id": "api-gateway", "name": "API Gateway", "owner_team": "platform",
       "criticality": "high", "description": "Routes all inbound API traffic, validates JWT tokens."}
    ],
    "dependencies": [
      {"from_service": "api-gateway", "to_service": "auth-service",
       "dependency_type": "sync-api", "strength": "hard"}
    ],
    "teams": [
      {"id": "platform", "name": "Platform", "owns": ["auth-service", "api-gateway"],
       "size": 6, "focus": "platform"}
    ],
    "decision": {
      "title": "Migrating auth DB to Aurora",
      "description": "Hard cutover from PostgreSQL to Aurora in a 4-hour maintenance window.",
      "decision_type": "migration",
      "affected_services": ["auth-service"],
      "timeline": "immediate",
      "reversibility": "hard"
    }
  }'
```

SSE events emitted:
```
data: {"type": "progress", "pass": 1, "total": 5, "message": "Classifying decision type..."}
data: {"type": "pass_complete", "pass": 1, "name": "Decision Classification", "summary": "..."}
data: {"type": "progress", "pass": 2, ...}
...
data: {"type": "result", "data": { ...BlastRadiusResult... }}
data: {"type": "complete", "message": "Analysis complete"}
```

**Synchronous (no streaming):**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d @your-request.json | jq '.overall_verdict, .overall_risk_score, .executive_summary'
```

**Load an example via API:**
```bash
curl http://localhost:8000/api/examples
# → [{"id": "db-migration", "title": "...", "description": "..."}, ...]

curl http://localhost:8000/api/examples/db-migration
# → Full BlastRadiusRequest object, ready to POST to /api/analyze
```

---

### Step 7 — Run the Test Suite

The test suite covers graph traversal, all 3 example scenarios, request validation, and the full 5-pass pipeline — all without requiring any API key (model calls are mocked at the `llm_client.complete` level).

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

Expected output:
```
tests/test_api_routes.py::test_health PASSED
tests/test_api_routes.py::test_list_examples PASSED
tests/test_api_routes.py::test_get_example_db_migration PASSED
tests/test_api_routes.py::test_analyze_rejects_missing_decision_title PASSED
tests/test_api_routes.py::test_analyze_rejects_invalid_criticality PASSED
tests/test_api_routes.py::test_analyze_sync_returns_blast_radius_result PASSED
tests/test_api_routes.py::test_analyze_stream_emits_sse_events PASSED
tests/test_examples.py::test_example_loads[db-migration] PASSED
tests/test_examples.py::test_example_graph_builds[api-deprecation] PASSED
tests/test_examples.py::test_db_migration_first_order_graph PASSED
tests/test_examples.py::test_db_migration_second_order_graph PASSED
tests/test_examples.py::test_db_migration_auth_is_hub PASSED
tests/test_graph_builder.py::test_get_first_order_single_affected PASSED
tests/test_graph_builder.py::test_get_second_order PASSED
...
49 passed in 0.42s
```

---

## Understanding Risk Verdicts

| Verdict | Meaning |
|---------|---------|
| **LOW** | Change is well-scoped with limited propagation. Proceed with standard review. |
| **MODERATE** | Meaningful impacts identified. Address key concerns before scheduling. |
| **HIGH** | Significant blast radius across technical and/or organizational dimensions. Mitigation required before proceeding. |
| **CRITICAL** | Wide-impact change with unmitigated risks. Do not proceed without a full rollback plan and stakeholder sign-off. |

The **overall risk score** (0.0–1.0) is synthesized by Pass 5 across 5 dimensions:

| Dimension | What It Captures |
|-----------|-----------------|
| **Technical** | Service breakage probability, rollback complexity, schema/protocol incompatibility |
| **Delivery** | Timeline feasibility, downstream release conflicts, dependency on external parties |
| **People** | Team capacity, key-person dependencies, on-call burden, org change friction |
| **Compliance** | Audit trail gaps, data residency concerns, regulatory obligations |
| **Financial** | Downtime cost, lost revenue during window, customer SLA penalties |

---

## Understanding the Graph

The interactive force graph encodes all impact information visually:

| Visual Property | Meaning |
|----------------|---------|
| **Node color** | Impact level: red = direct, orange = first-order, yellow = second-order, gray = unaffected |
| **Node size** | Service criticality: critical > high > medium > low |
| **Node shape** | `●` = service, `◆` = team, `▲` = process/external |
| **◈ marker** | Node was inferred by the analysis engine — not explicitly in your intake |
| **Edge thickness** | Dependency strength: hard > soft |
| **Edge label** | Dependency type: sync-api, database, async-event, etc. |

Click any node to open the **detail drawer** — impact description, recommended actions, and an inferred-node warning if applicable.

Use the **severity filter chips** at the top to focus on critical and high nodes when the graph is dense.

---

## POC vs Production: Bridging the Gap

This section answers the questions a senior engineering leader will ask when evaluating this tool.

### Q1: The context I enter manually — how would that be automated in production?

| What you enter manually | Production replacement |
|---|---|
| Service list + descriptions | Backstage / OpsLevel service catalog API |
| Service dependencies | Terraform/CloudFormation parsed graph, Datadog service map |
| Team ownership | Workday org chart API, PagerDuty escalation policies |
| Historical incidents | PagerDuty / OpsGenie incident history API |
| SLA commitments | Internal SLA registry, Confluence/Notion page |

Each of these is a well-understood integration. The intake form is a product requirements document for those integrations, not a limitation of the approach.

### Q2: How does graph traversal work without a real dependency map?

The dependencies you define in the intake form build a real `nx.DiGraph`. The traversal logic — hop-distance propagation, betweenness centrality, dependency strength weighting — is production-ready as built. Only the data source changes in production. A Terraform graph parser or Datadog service map API replaces the form; the `get_first_order()` and `get_second_order()` functions are identical.

### Q3: What stops this from producing generic AI output?

**1. Structured intake forces specificity.** Analysis is grounded in your services, your teams, and your decision. The model cannot hallucinate a dependency that isn't in the graph.

**2. Multi-pass reasoning.** Each analysis pass receives structured output of all previous passes. The final synthesis is not a single prompt — it's the end of a reasoning chain where each step constrains the next.

**3. NetworkX graph traversal computes impact propagation algorithmically before the model reasons about it.** Before the model touches second-order impacts, the system has already computed which services are 1 and 2 hops away. The model interprets a real graph structure.

### Q4: How would stale context be handled in production?

Every node would carry a `last_updated` timestamp from its source integration. The UI would surface staleness warnings: *"Service X was last synced 47 days ago — verify before relying on this analysis."* The POC addresses this with the confidence note on every output and the ◈ marker on inferred nodes.

### Q5: What is the honest limitation of this POC?

Output quality is proportional to context quality. Vague service descriptions and incomplete dependencies produce vague analysis. This is by design — the tool makes context gaps visible through the ◈ inferred marker and the confidence note rather than hiding them.

The analysis engine, graph traversal, visualization, and 5-pass reasoning chain are production-ready. The data layer is what a real deployment would replace.

### Q6: What would a production deployment roadmap look like?

| Phase | What changes | Status |
|---|---|---|
| Phase 1 — POC (this repo) | Manual intake → analysis engine → graph UI | ✅ Complete |
| Phase 2 — Integration | Backstage API replaces service/dependency intake | 🔷 Scoped |
| Phase 3 — Intelligence | PagerDuty history enables pattern-matched risk | 🔷 Scoped |
| Phase 4 — Workflow | Jira/Confluence export, change management hooks | 📋 Planned |
| Phase 5 — Continuous | CI/CD hook — auto-analyze every arch decision | 📋 Planned |

Phase 1 is fully functional today. Phases 2–5 are well-scoped engineering work, not research problems. The hard architectural decisions are already made.

---

## Key Design Decisions

### 1. Model-provider agnostic — configured entirely via env vars
All 5 analysis passes route through a single `llm_client.complete(system, user, max_tokens)` function in `services/llm_client.py`. The service files contain zero SDK imports. Switching from Claude to GPT-4o to a local Ollama model requires only `.env` changes — no code changes.

### 2. Sequential passes with accumulated context, not a single mega-prompt
Each pass receives structured JSON from all prior passes. By the time Pass 5 runs, it has seen the decision classification, graph-grounded impact nodes, propagation analysis, and org impact mapping. This produces dramatically better synthesis than a single prompt trying to do all five jobs at once.

### 3. NetworkX graph traversal runs before the model, not instead of it
`get_first_order()` and `get_second_order()` compute the 1-hop and 2-hop service neighborhoods algorithmically before any model call. Pass 2 receives the actual first-order services as structured context — the model interprets a real dependency graph, not guesses at it.

### 4. Pass 4 (Organizational Impact) is treated as a first-class output
Most impact analysis tools produce a technical blast radius and stop. Pass 4 maps that technical blast radius to team workload, roadmap disruption, SLA risk, and communication overhead. The platform-reorg example is designed specifically to demonstrate this — it's a case where technical risk is LOW but organizational risk is HIGH.

### 5. `is_inferred: bool` on every ImpactNode
Every node the model identifies beyond your explicit intake is marked `is_inferred: true` and displayed with a ◈ marker in the UI. This is an explicit design choice: intellectual honesty over false confidence. The tool tells you what it knows vs. what it deduced.

### 6. SSE streaming with executor offloading
The `/api/analyze/stream` endpoint uses `asyncio.get_event_loop().run_in_executor()` to run blocking Anthropic SDK calls in a thread pool, while the async generator yields SSE events between each pass. Users see progress in real time without blocking the event loop.

### 7. Auto-derived teams if none are defined
If the user fills out services with `owner_team` values but doesn't add explicit teams, `handleSubmit` in the frontend auto-generates team stubs from unique `owner_team` values, grouping owned services. The backend always receives valid team data for Pass 4 regardless of whether the user fills out Section C.

---

## Extending the System

### Swap the AI Model or Provider

All model calls are routed through a single abstraction layer — [services/llm_client.py](backend/services/llm_client.py). Change provider and model entirely through `.env`, no code changes needed:

```env
# Switch to OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...

# Switch to Groq
LLM_PROVIDER=openai
LLM_MODEL=llama-3.3-70b-versatile
OPENAI_API_KEY=gsk_...
OPENAI_BASE_URL=https://api.groq.com/openai/v1

# Run fully local with Ollama
LLM_PROVIDER=openai
LLM_MODEL=llama3.2
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
```

To add a new provider (e.g. Cohere, Mistral native API), add a new branch in `llm_client.py`'s `_get_client()` and `complete()` functions.

### Add a New Risk Dimension

1. Add the dimension to the Pass 5 prompt in `utils/prompts.py`
2. Update `RiskDimension` expectations in the Pass 5 output schema
3. The frontend `RiskDimensions` component renders all dimensions dynamically — no frontend changes required

### Add a New Example Scenario

Add a new `BlastRadiusRequest` entry to the `EXAMPLES` dict in `routers/examples.py`:

```python
EXAMPLES["my-scenario"] = BlastRadiusRequest(
    services=[...],
    dependencies=[...],
    teams=[...],
    decision=Decision(
        title="My decision",
        description="...",
        decision_type="migration",
        affected_services=["svc-a"],
        timeline="weeks",
        reversibility="moderate",
    ),
)
```

Then add the corresponding JS object to `frontend/src/data/examples.js` for the frontend dropdown.

### Add a New API Endpoint

Add a router file in `backend/routers/` and register it in `backend/main.py`:

```python
from routers.my_endpoint import router as my_router
app.include_router(my_router, prefix="/api", tags=["my-feature"])
```

### Change the Graph Traversal Logic

`get_first_order()` and `get_second_order()` in `services/graph_builder.py` return `Set[str]` of service IDs. Both consider predecessors and successors (bidirectional). To restrict to only downstream propagation:

```python
def get_first_order(G: nx.DiGraph, affected_ids: List[str]) -> Set[str]:
    affected_set = set(affected_ids)
    neighbors: Set[str] = set()
    for sid in affected_ids:
        if sid in G:
            neighbors.update(G.successors(sid))   # downstream only
    return neighbors - affected_set
```

---

## API Reference

Interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/analyze/stream` | 5-pass analysis as Server-Sent Events |
| `POST` | `/api/analyze` | 5-pass analysis, synchronous, returns `BlastRadiusResult` |
| `GET` | `/api/examples` | List available example scenarios |
| `GET` | `/api/examples/{id}` | Get a complete example as `BlastRadiusRequest` |

### SSE Event Types (`/api/analyze/stream`)

| Event | Payload |
|-------|---------|
| `progress` | `{type, pass, total, message}` |
| `pass_complete` | `{type, pass, name, summary}` |
| `result` | `{type, data: BlastRadiusResult}` |
| `complete` | `{type, message}` |
| `error` | `{type, message, detail}` |

### BlastRadiusResult Shape

```json
{
  "overall_verdict": "HIGH",
  "overall_risk_score": 0.78,
  "decision_title": "Migrating auth DB to Aurora",
  "decision_type": "migration",
  "executive_summary": "...",
  "risk_dimensions": [
    {"dimension": "technical", "score": 0.85, "summary": "...", "top_risks": [...], "mitigations": [...]}
  ],
  "nodes": [
    {
      "id": "auth-service", "name": "Authentication Service", "type": "service",
      "impact_level": "direct", "risk_severity": "critical",
      "impact_description": "...", "recommended_actions": [...],
      "is_inferred": false
    }
  ],
  "edges": [
    {"from_id": "api-gateway", "to_id": "auth-service", "dependency_type": "sync-api", "strength": "hard"}
  ],
  "immediate_actions": ["...", "..."],
  "questions_to_answer": ["...", "..."],
  "confidence_note": "This analysis is grounded in the context you provided. Nodes marked ◈ are inferred.",
  "analysis_passes": [
    {"pass": 1, "name": "Decision Classification", "summary": "..."},
    ...
  ]
}
```

---

## Key Files

```
blast-radius-analyzer/
│
├── .env.example                        Template — copy to .env and add ANTHROPIC_API_KEY
├── docker-compose.yml                  Orchestrates backend (8000) + frontend (3001)
│
├── backend/
│   ├── main.py                         FastAPI app, configurable CORS, request-size
│   │                                   middleware (413), router registration,
│   │                                   startup warning if API key missing
│   ├── requirements.txt                fastapi, uvicorn, anthropic, openai, networkx,
│   │                                   pydantic>=2.0.0, python-dotenv
│   │
│   ├── models/
│   │   ├── intake.py                   BlastRadiusRequest, Service, Dependency,
│   │   │                               Team, Decision — Pydantic v2 with field-length
│   │   │                               bounds and cross-field referential validation
│   │   └── analysis.py                 BlastRadiusResult, ImpactNode, ImpactEdge,
│   │                                   RiskDimension — typed output models
│   │
│   ├── routers/
│   │   ├── analyze.py                  SSE streaming + sync endpoints;
│   │   │                               run_in_executor for non-blocking model calls;
│   │   │                               AnalysisError → 502, unexpected → 500 (no leakage)
│   │   ├── examples.py                 3 fully populated BlastRadiusRequest objects
│   │   └── health.py                   GET /health
│   │
│   ├── services/
│   │   ├── llm_client.py               Provider-agnostic model abstraction;
│   │   │                               routes to Anthropic or OpenAI SDK via LLM_PROVIDER;
│   │   │                               ThreadPoolExecutor timeout control
│   │   ├── errors.py                   AnalysisError → LLMOutputError, LLMTimeoutError;
│   │   │                               hierarchy that maps to 502 vs 500 at the router
│   │   ├── graph_builder.py            nx.DiGraph, get_first_order(), get_second_order(),
│   │   │                               compute_centrality(), get_services_by_ids()
│   │   ├── decision_classifier.py      Pass 1
│   │   ├── impact_analyzer.py          Pass 2 + 3
│   │   ├── org_mapper.py               Pass 4
│   │   └── risk_scorer.py              Pass 5 + BlastRadiusResult assembly
│   │
│   ├── utils/
│   │   ├── prompts.py                  All 5 model system + user prompts, isolated;
│   │   │                               each user prompt includes prior pass context
│   │   └── llm_json.py                 parse_llm_json() — multi-candidate JSON parser;
│   │                                   handles raw text, fenced blocks, bare {...};
│   │                                   raises LLMOutputError on all failures
│   │
│   └── tests/
│       ├── test_graph_builder.py       8 unit tests — no API key required
│       ├── test_examples.py            15 parametrized tests — all 3 examples,
│       │                               graph correctness, ownership validation
│       └── test_api_routes.py          17 integration tests — mocked model,
│                                       5-pass pipeline, SSE event types, 422 validation,
│                                       timeout/size-limit/error-routing coverage
│
└── frontend/
    ├── vite.config.js                  Dev server on :3001, proxy /api → :8000
    ├── tailwind.config.js              Dark theme palette, custom colors
    └── src/
        ├── App.jsx                     Two-panel layout (40/60), nav, About toggle,
        │                               team auto-derivation logic
        ├── index.css                   IBM Plex Mono/Sans fonts, slide-in animations
        │
        ├── hooks/
        │   └── useAnalysis.js          fetch() + ReadableStream SSE hook
        │                               (not EventSource — POST requires fetch)
        │
        ├── data/
        │   └── examples.js             3 example scenarios as JS objects
        │
        └── components/
            ├── IntakeForm/
            │   ├── index.jsx           Orchestrates 4 sections, Load Example dropdown
            │   ├── ServicesSection.jsx  Add/edit services with auto-slug ID generation
            │   ├── DependenciesSection.jsx  Visual dependency builder with dropdowns
            │   ├── TeamsSection.jsx    Add/edit teams with owned-services multi-select
            │   └── DecisionSection.jsx Segmented controls, affected services chips
            ├── BlastGraph/
            │   └── index.jsx           D3 v7 force simulation, decision node fixed
            │                           at center, severity filter chips, cleanup hook
            ├── Results/
            │   ├── index.jsx           Full results orchestrator
            │   ├── OrgImpact.jsx       Pass 4 display — team/process/external nodes
            │   └── ...                 VerdictBanner, RiskDimensions, Actions, etc.
            ├── AboutPanel/
            │   └── index.jsx           "How It Works" + "POC vs Production" tabs
            ├── StreamingProgress.jsx   Live pass progress with CheckCircle/Loader icons
            └── NodeDrawer.jsx          Slide-over node detail — impact, actions, ◈ warning
```

---

## Configuration

All settings are loaded from `.env` (copy from `.env.example`):

### AI Model Provider

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `anthropic` | AI model backend. Valid values: `anthropic`, `openai` |
| `LLM_MODEL` | *(provider default)* | Model name. Defaults: `claude-sonnet-4-6` (anthropic), `gpt-4o` (openai) |

### Anthropic (`LLM_PROVIDER=anthropic`)

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | **Yes** | Your Anthropic API key |

### OpenAI or compatible (`LLM_PROVIDER=openai`)

Covers OpenAI, Groq, Together.ai, Ollama, Azure OpenAI, LM Studio, and any OpenAI-compatible endpoint.

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | **Yes** | API key for your provider |
| `OPENAI_BASE_URL` | No | Override the API base URL. Omit for official OpenAI. |

### Examples

**Use Groq (Llama 3.3 70B, free tier available):**
```env
LLM_PROVIDER=openai
LLM_MODEL=llama-3.3-70b-versatile
OPENAI_API_KEY=gsk_...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

**Run locally with Ollama (no API key needed):**
```env
LLM_PROVIDER=openai
LLM_MODEL=llama3.2
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
```

**Use OpenAI GPT-4o:**
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
```

The backend prints a warning at startup if the required API key for the selected provider is missing. Health and examples endpoints work without a key; analysis endpoints will fail.

### Server & Deployment

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_TIMEOUT_SECONDS` | `120` | Max seconds to wait for a single model call. Returns 502 to the client if exceeded. Minimum 1. |
| `MAX_REQUEST_BYTES` | `262144` | Max request body size in bytes (256 KB). Returns 413 if exceeded. |
| `CORS_ALLOW_ORIGINS` | `http://localhost:3001, http://localhost:5173, http://localhost:3000` | Comma-separated list of allowed frontend origins. |
| `VITE_API_URL` | *(Vite proxy)* | Frontend API base URL. Leave unset in local dev (Vite proxies to `:8000`). Set for Docker or any non-localhost deployment. |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please open an issue before starting significant work.

Areas where contributions are particularly welcome:
- Additional example scenarios (different industries, decision types)
- New risk dimensions or scoring logic
- Backstage / service catalog integrations
- Export formats (PDF, Jira ticket, ADR template)

---

## License

MIT — see [LICENSE](LICENSE).
