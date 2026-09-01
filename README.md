# AI Knowledge Assistant — RAG + n8n

A portfolio project for building a reliable Retrieval-Augmented Generation (RAG) assistant orchestrated with n8n, FastAPI and PostgreSQL/pgvector.

## Goal

The assistant answers business questions using only retrieved knowledge-base content and returns the supporting sources. When retrieval evidence is insufficient, the system should avoid inventing an answer.

This repository uses fictional documents only. It is designed as a learning and portfolio project and does not contain confidential company data.

## Current status

**Milestone 1 — foundation:** in progress

Implemented:
- FastAPI service with `/health` and `/ask` endpoints
- structured response contract
- Dockerfile
- Docker Compose with PostgreSQL + pgvector
- environment template
- fictional sample knowledge document
- initial automated tests
- GitHub Actions CI

Next milestones:
1. document ingestion and chunking
2. embeddings generation
3. pgvector persistence and similarity search
4. grounded answer generation with citations
5. n8n webhook orchestration
6. retries, validation, observability and evaluation

## Architecture

```text
User / Client
    |
    v
n8n Webhook
    |
    v
FastAPI
    |
    +--> Retriever --> PostgreSQL / pgvector
    |                       ^
    |                       |
    |                  Embeddings
    |
    +--> LLM --> Structured grounded response
                    |
                    +--> answer
                    +--> sources
                    +--> grounded flag
```

## Local setup

### Requirements

- Docker Desktop
- Docker Compose
- An OpenAI API key will be required when the RAG/LLM stage is enabled

### Start

```bash
cp .env.example .env
# edit .env when API credentials are required

docker compose up --build
```

API documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
GET http://localhost:8000/health
```

Initial question endpoint:

```text
POST http://localhost:8000/ask
Content-Type: application/json

{
  "question": "How do I request a notebook?"
}
```

At Milestone 1 this endpoint intentionally returns a placeholder. Retrieval and generation will be implemented next.

## Why n8n + custom code?

The project intentionally separates orchestration from application logic. n8n will handle triggers and workflow coordination, while FastAPI will own retrieval, validation and RAG-specific code. This demonstrates both low-code automation and the ability to extend workflows with custom software.

## Portfolio boundaries

- fictional data only
- no claim of commercial production deployment
- no confidential business process or internal company document
- each technical claim should be reproducible from this repository
