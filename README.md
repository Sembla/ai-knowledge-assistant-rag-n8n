# AI Knowledge Assistant — RAG + n8n

A functional portfolio project implementing a Retrieval-Augmented Generation (RAG) knowledge assistant with **Python, FastAPI, OpenAI, PostgreSQL/pgvector, Docker and n8n**.

The assistant retrieves relevant knowledge-base chunks before asking an LLM to answer. It returns the generated answer together with its retrieved sources, similarity scores and a `grounded` flag. If retrieval does not find enough evidence, the assistant refuses to invent an answer.

> **Portfolio boundary:** every knowledge-base document in this repository is fictional. No confidential company data, credentials or internal processes are included.

## Current status

The MVP is functional and has been validated locally through the API, the n8n webhook and an automated regression suite.

Implemented:
- FastAPI REST API
- Markdown/TXT document ingestion
- deterministic text chunking with overlap
- OpenAI embeddings
- PostgreSQL + pgvector persistence
- cosine-similarity retrieval
- configurable top-k retrieval
- minimum similarity safeguard (`RETRIEVAL_MIN_SCORE=0.45`)
- source-grounded LLM generation
- structured `answer`, `sources` and `grounded` output
- explicit insufficient-evidence fallback
- Docker Compose for API, pgvector and n8n
- importable n8n webhook orchestration
- fictional sample knowledge base
- automated unit, API and RAG grounding tests
- GitHub Actions CI foundation

## Architecture

```text
Client / User
     |
     v
n8n Webhook
     |
     v
Input normalization
     |
     v
FastAPI /ask
     |
     +----> OpenAI Embedding API
     |             |
     |             v
     +----> pgvector similarity search
     |             |
     |      score >= threshold?
     |          /       \
     |        no         yes
     |        |           |
     |        v           v
     |    safe fallback  retrieved context
     |                    |
     +--------------------+
                          |
                          v
                 OpenAI Responses API
                          |
                          v
              Grounded answer + sources
```

Document ingestion is a separate path:

```text
Markdown/TXT documents
        |
        v
     chunking
        |
        v
 OpenAI embeddings
        |
        v
PostgreSQL + pgvector
```

## Project structure

```text
app/
├── api/
│   ├── routes.py
│   └── schemas.py
├── core/
│   ├── config.py
│   └── database.py
├── rag/
│   ├── chunking.py
│   ├── embeddings.py
│   ├── generation.py
│   ├── ingestion.py
│   ├── models.py
│   └── retrieval.py
└── main.py

data/sample_docs/          fictional knowledge base
n8n/workflows/              importable n8n workflow
tests/                      automated regression suite
```

## Local setup

### 1. Requirements

- Docker Desktop with WSL 2/virtualization enabled on Windows
- Git
- an OpenAI API key with API billing/credits available

### 2. Clone

```bash
git clone https://github.com/Sembla/ai-knowledge-assistant-rag-n8n.git
cd ai-knowledge-assistant-rag-n8n
```

### 3. Configure environment

PowerShell:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set only your local key:

```env
OPENAI_API_KEY=your_key_here
```

Never commit `.env`. It is ignored by `.gitignore`.

### 4. Start the stack

```bash
docker compose up --build
```

Services:
- FastAPI: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- n8n: `http://localhost:5678`
- PostgreSQL/pgvector: `localhost:5432`

### 5. Health check

```http
GET /health
```

Expected:

```json
{"status":"ok"}
```

### 6. Ingest the fictional knowledge base

From Swagger, execute:

```http
POST /ingest
```

Expected shape:

```json
{
  "documents": 3,
  "chunks": 3
}
```

The exact chunk count can change when documents or chunk settings change.

### 7. Ask a grounded question

```http
POST /ask
Content-Type: application/json

{
  "question": "How do I request a notebook?"
}
```

Response shape:

```json
{
  "answer": "...",
  "sources": [
    {
      "document": "it_equipment_policy.md",
      "excerpt": "...",
      "score": 0.6238
    }
  ],
  "grounded": true
}
```

Questions outside the fictional knowledge base return an insufficient-evidence response with no accepted sources and `grounded: false`.

## n8n orchestration

1. Open `http://localhost:5678`.
2. Complete the local n8n setup if requested.
3. Import `n8n/workflows/knowledge-assistant-webhook.json`.
4. Open and test the workflow.
5. Activate/publish it when ready.

The workflow performs:

```text
Webhook -> input normalization -> FastAPI /ask -> webhook response
```

Because n8n and FastAPI run in the same Docker Compose network, the workflow calls the API at `http://api:8000/ask`.

## Configuration

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | local API credential |
| `OPENAI_CHAT_MODEL` | response-generation model |
| `OPENAI_EMBEDDING_MODEL` | embedding model |
| `EMBEDDING_DIMENSIONS` | pgvector dimension |
| `RETRIEVAL_TOP_K` | maximum retrieved chunks |
| `RETRIEVAL_MIN_SCORE` | minimum similarity accepted as evidence |
| `CHUNK_SIZE` | maximum chunk size in characters |
| `CHUNK_OVERLAP` | repeated context between adjacent chunks |

The current portfolio baseline uses `RETRIEVAL_MIN_SCORE=0.45`. This value was selected to reject unrelated questions in the sample corpus while retaining the supported evaluation questions; it is a demo threshold, not a universal production value.

## Reliability and hallucination controls

- the model is instructed to answer from retrieved context
- retrieval uses an explicit minimum similarity score
- low-confidence retrieval is discarded before generation
- no accepted context produces a deterministic insufficient-evidence fallback
- returned sources and scores make retrieval inspectable
- API input is validated with Pydantic
- services are isolated with Docker Compose
- database health is checked before the API starts
- secrets remain outside Git through `.env`

## Automated tests

Run the suite inside the API container:

```bash
docker compose exec api pytest -v
```

The suite covers:
- chunk splitting and overlap
- blank-input chunking
- invalid overlap validation
- `/health`
- `/ask` request validation
- notebook-policy grounding
- access-policy grounding
- purchasing-policy grounding
- unsupported-question fallback

### Validated local run

The current implementation was manually validated on **September 2, 2026** with:

```text
collected 9 items
9 passed, 1 warning in 11.92s
```

The warning observed in that run was a dependency deprecation warning from the Starlette/AnyIO test stack, not a failed application test.

The three supported RAG evaluation questions selected their expected source documents, while a vacation-policy question outside the knowledge base returned `grounded: false` with an empty accepted-source list.

> The RAG regression tests call the configured embedding/LLM services and therefore are integration-style tests rather than fully deterministic offline unit tests. They may consume API credits.

## What this project demonstrates

This repository provides hands-on evidence of:
- RAG architecture
- embeddings and vector similarity search
- pgvector
- retrieval thresholds and hallucination safeguards
- LLM API integration
- FastAPI
- REST/webhook integration
- n8n orchestration
- Dockerized services
- automated regression testing
- source traceability
- explicit handling of insufficient knowledge

## Portfolio scope and next steps

This is a functional learning/portfolio implementation, **not an enterprise-scale production deployment**.

Natural next steps:
- structured observability and request tracing
- latency and token/cost metrics
- retries/backoff for external APIs
- a larger evaluation dataset and retrieval metrics
- reranking
- authentication and rate limiting
- cloud deployment
- CI integration tests with controlled credentials
- optional Flowise comparison
- an MCP interface
