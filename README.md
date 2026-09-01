# AI Knowledge Assistant — RAG + n8n

A portfolio project that implements a Retrieval-Augmented Generation (RAG) assistant with **Python, FastAPI, OpenAI, PostgreSQL/pgvector, Docker and n8n**.

The assistant retrieves relevant knowledge-base chunks before asking an LLM to answer. It returns the generated answer together with the retrieved sources and a grounded flag. If retrieval does not find enough evidence, the assistant refuses to invent an answer.

> Portfolio boundary: every document in this repository is fictional. No confidential company data, credentials or internal processes are included.

## Status

**MVP RAG implemented on `feature/full-rag-mvp`.**

Implemented:
- FastAPI REST API
- document ingestion from Markdown/TXT files
- deterministic text chunking with overlap
- OpenAI embeddings
- PostgreSQL + pgvector persistence
- cosine-similarity retrieval
- minimum retrieval-score safeguard
- source-grounded LLM generation through the Responses API
- structured output with `answer`, `sources` and `grounded`
- Docker Compose for API, pgvector and n8n
- importable n8n webhook workflow
- fictional sample documents
- unit/API tests
- GitHub Actions CI foundation

## Architecture

```text
Client / User
     |
     v
n8n Webhook
     |
     v
Validate input
     |
     v
FastAPI /ask
     |
     +----> OpenAI Embedding API
     |             |
     |             v
     +----> pgvector similarity search
     |             |
     |             v
     |       retrieved chunks
     |             |
     +-------------+
     |
     v
OpenAI Responses API
     |
     v
Grounded answer + sources + retrieval scores
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
tests/                      automated tests
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
git checkout feature/full-rag-mvp
```

### 3. Configure environment

PowerShell:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set only your local key:

```env
OPENAI_API_KEY=your_new_key_here
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
      "score": 0.0
    }
  ],
  "grounded": true
}
```

Try a question that is not covered by the fictional documents. When no retrieved chunk reaches the configured threshold, the system returns an insufficient-evidence answer instead of intentionally inventing a policy.

## n8n orchestration

1. Open `http://localhost:5678`.
2. Complete the local n8n setup if requested.
3. Import `n8n/workflows/knowledge-assistant-webhook.json`.
4. Open the workflow and test it.
5. Activate it when ready.

The workflow performs:

```text
Webhook -> input validation -> FastAPI /ask -> webhook response
```

Because n8n and FastAPI run in the same Docker Compose network, the workflow calls the API at `http://api:8000/ask`.

## Configuration

Important `.env` options:

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

## Reliability choices

- the model is instructed to answer only from retrieved context
- retrieval uses an explicit minimum score
- no matching context produces an insufficient-evidence response
- returned sources make retrieval inspectable
- API input is validated with Pydantic
- services are isolated with Docker Compose
- database health is checked before the API starts
- secrets remain outside Git through `.env`

## Tests

```bash
pytest -q
```

Current tests cover the health endpoint, request validation and chunking behavior. End-to-end tests that call the external LLM API are intentionally separate from the deterministic unit-test layer.

## Portfolio scope

This repository demonstrates a functional learning/portfolio implementation. It does **not** claim enterprise-scale production deployment. Natural next steps include structured observability, retries/backoff for external APIs, evaluation datasets, reranking, authentication, rate limiting, cost tracking, CI end-to-end tests, cloud deployment and an MCP interface.
