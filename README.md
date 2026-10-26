# Stock News Agent

A production-style AI workflow that collects market news for a stock ticker, summarizes each article in English and Korean, scores sentiment, and persists the results to Supabase.

This project is built as a LangGraph-based agent and exposed through FastAPI and LangServe, making it suitable both as a backend service and as an example of applied agent architecture for financial intelligence workflows.

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Workflow-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-API_Service-009688)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black)
![Supabase](https://img.shields.io/badge/Supabase-Data_Store-3ECF8E)
![uv](https://img.shields.io/badge/uv-Package_Manager-6E56CF)

## Overview

The system accepts a stock ticker, checks whether fresh news already exists for the current day, fetches new articles when needed, runs structured LLM analysis, and stores the results for downstream use.

It demonstrates several patterns that are valuable in real AI product development:

- stateful orchestration with LangGraph
- external data acquisition with Tavily and yfinance
- structured LLM output with Pydantic schemas
- bilingual summarization and sentiment analysis
- API-first delivery with FastAPI and LangServe
- persistent storage with Supabase

## What It Does

- Loads same-day news from Supabase when it already exists for the requested ticker.
- Searches recent stock-related news when no cached records are available.
- Enriches the request with company, sector, and industry metadata from yfinance.
- Uses a local Ollama model to generate structured analysis for each article.
- Produces English and Korean summaries and Korean content translations.
- Assigns article-level sentiment labels and scores.
- Exposes the workflow through both a custom REST endpoint and a LangServe route.

## Architecture

The core workflow is implemented as a LangGraph state machine.

![Stock News Agent Architecture](assets/architecture-diagram.svg)

The diagram below shows how the API layer, LangGraph workflow, model inference, and persistence layer interact during a request.

### Workflow Nodes

- `load_news`: checks Supabase for same-day news for the requested active ticker.
- `search_news`: queries Tavily for recent relevant articles and attaches company metadata.
- `summarize_news`: uses Ollama with structured output to create bilingual summaries and sentiment analysis.
- `save_to_db`: upserts ticker metadata and stores analyzed news records in Supabase.

## Tech Stack

- Python 3.13
- LangGraph, LangChain, LangServe
- FastAPI, Uvicorn
- Ollama for local inference
- Tavily for news search
- yfinance for company metadata
- Supabase for persistence
- Pydantic for response and state schemas
- uv for dependency and environment management

## API Surface

### Custom endpoint

`POST /api/v1/stock-news/news`

Request body:

```json
{
	"ticker": "AAPL"
}
```

Response shape:

```json
{
	"ticker": "AAPL",
	"industry": "Consumer Electronics",
	"sector": "Technology",
	"news_list": [
		{
			"id": 1,
			"title": "...",
			"content": "...",
			"content_kr": "...",
			"summary": "...",
			"summary_kr": "...",
			"published_date": "2026-06-08T12:34:56+00:00",
			"url": "https://...",
			"sentiment_label": "Positive",
			"sentiment_score": 0.74
		}
	]
}
```

### LangServe route

`/agent`

This route exposes the LangGraph workflow directly through LangServe for experimentation and agent-focused integration.

## Project Structure

```text
.
├── main.py                  # FastAPI application entrypoint
├── agent/
│   ├── stock_news_agent.py  # LangGraph definition
│   ├── state.py             # Shared workflow state and schemas
│   ├── nodes/               # Workflow node implementations
│   └── utils/               # Search, metadata, LLM, and data clients
├── data/
│   └── schema.sql           # Supabase schema
├── notebooks/               # Local experimentation and visualization
└── main.spec                # PyInstaller packaging configuration
```

## Local Setup

### 1. Install dependencies

```powershell
uv sync
```

### 2. Create a `.env` file in the project root

Required variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key
TAVILY_API_KEY=your_tavily_api_key
```

### 3. Prepare the database

Run the SQL in `data/schema.sql` against your Supabase project.

### 4. Start Ollama and pull the required model

```powershell
ollama pull qwen3.5:9b
ollama serve
```

### 5. Run the API locally

```powershell
uv run python main.py
```

The API starts on `http://localhost:8008`.

## Example Request

```powershell
Invoke-RestMethod `
	-Method Post `
	-Uri http://localhost:8008/api/v1/stock-news/news `
	-ContentType 'application/json' `
	-Body '{"ticker":"AAPL"}'
```

## Demo Screenshots

### API Demo Preview

![Stock News Agent Demo Preview](assets/demo-screenshot-placeholder.svg)

Suggested real screenshots to replace this placeholder later:

- FastAPI Swagger page for `POST /api/v1/stock-news/news`
- terminal run showing the app booting on port `8008`
- JSON response example for a ticker such as `AAPL` or `NVDA`

## Current Limitations

- The project currently has no automated test suite.
- Error handling and observability can be expanded for production readiness.
- The current workflow focuses on a single ticker request at a time.
- Secrets and deployment steps are not yet packaged for one-command onboarding.

## Roadmap to v1.0

This project is being upgraded from a fixed news-summarization pipeline into a
production-grade, evaluated, multi-agent system. Work is tracked through
[issues](../../issues) and [milestones](../../milestones), and each phase ends
with a pre-release tag (`v1.0.0-alpha.N`).

**Branching:** active development happens on `integration/v1.0` (the current default
branch). `main` holds the last stable release and receives v1.0 when all four
phases are complete.

### Phase 1 – Testability
Make every component testable in isolation and add an automated quality gate.

- [ ] Dev tooling (pytest, ruff, mypy), CI workflow, and license (#1)
- [ ] Dependency injection via LangGraph runtime context; remove import-time side effects
- [ ] Unit tests for pure functions and graph routing, using fakes for external services
- [ ] Fix: prompt template breaks when article content contains `{`
- [ ] Fix: API returns 500 when date, industry, or sector is missing
- [ ] Fix: analysis merge trusts LLM-generated article ids
- [ ] Cleanups: `zoneinfo` instead of `pytz`, log swallowed exceptions, remove duplicate calls

### Phase 2 – Resilience & Packaging
Keep the pipeline running when individual articles, models, or services fail.

- [ ] Replace LangServe (with an architecture decision record)
- [ ] Per-article fan-out with failure isolation (LangGraph `Send`)
- [ ] Timeouts, retries with backoff, and model fallback behind a provider abstraction
- [ ] Idempotent saves with URL-based deduplication
- [ ] Resumable runs with a Postgres checkpointer
- [ ] Docker and docker-compose (app, Ollama, Postgres)
- [ ] Structured logging

### Phase 3 – Evals & Observability
Measure quality instead of assuming it, and make every run traceable.

- [ ] Golden dataset: ~100 articles with human sentiment labels and Korean references
- [ ] Evaluation harness: sentiment accuracy, summary faithfulness, translation quality,
      schema validity, latency, and cost
- [ ] Model comparison report (local open-weight vs. hosted models)
- [ ] Tracing for every node: latency and token usage
- [ ] CI regression gate: fail the build when eval scores drop below baseline
- [ ] Prompt-injection guardrails and tests (fetched articles are untrusted input)

### Phase 4 – Agentic Evolution
Move from a fixed workflow to agents that decide what to research next.

- [ ] MCP servers for news search and market data, decoupled from agent logic
- [ ] Multi-agent analysis: news, fundamentals, and risk analysts coordinated by a supervisor
- [ ] Historical retrieval with pgvector: "what happened after similar news?"
- [ ] Human-in-the-loop review before reports are published
- [ ] Watchlist batch processing through a queue
- [ ] v1.0 release: design document, updated screenshots, merge to `main`

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
