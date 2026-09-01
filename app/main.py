from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="AI Knowledge Assistant",
    version="0.1.0",
    description="RAG-based knowledge assistant orchestrated with n8n.",
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class SourceItem(BaseModel):
    document: str
    excerpt: str
    score: float


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    grounded: bool


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
def ask(payload: QuestionRequest) -> AnswerResponse:
    # Temporary deterministic response for the first integration test.
    # The RAG pipeline will replace this in the next milestone.
    return AnswerResponse(
        answer=(
            "The API is running. The retrieval and generation pipeline has not "
            "been enabled yet."
        ),
        sources=[],
        grounded=False,
    )
