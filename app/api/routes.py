from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import AnswerResponse, IngestResponse, QuestionRequest, SourceItem
from app.core.database import get_db
from app.rag.generation import generate_answer
from app.rag.ingestion import ingest_directory
from app.rag.retrieval import retrieve

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ingest", response_model=IngestResponse)
def ingest(db: Session = Depends(get_db)) -> IngestResponse:
    try:
        result = ingest_directory(db)
        return IngestResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc


@router.post("/ask", response_model=AnswerResponse)
def ask(payload: QuestionRequest, db: Session = Depends(get_db)) -> AnswerResponse:
    try:
        matches = retrieve(db, payload.question)
        context_items = [(chunk.document, chunk.content) for chunk, _ in matches]
        answer = generate_answer(payload.question, context_items)
        sources = [
            SourceItem(document=chunk.document, excerpt=chunk.content[:280], score=round(score, 4))
            for chunk, score in matches
        ]
        return AnswerResponse(answer=answer, sources=sources, grounded=bool(matches))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Question processing failed: {exc}") from exc
