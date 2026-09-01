from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.rag.embeddings import embed_query
from app.rag.models import DocumentChunk

settings = get_settings()


def retrieve(db: Session, question: str) -> list[tuple[DocumentChunk, float]]:
    query_vector = embed_query(question)
    distance = DocumentChunk.embedding.cosine_distance(query_vector)
    stmt = (
        select(DocumentChunk, distance.label("distance"))
        .order_by(distance)
        .limit(settings.retrieval_top_k)
    )
    rows = db.execute(stmt).all()

    results: list[tuple[DocumentChunk, float]] = []
    for chunk, cosine_distance in rows:
        score = max(0.0, 1.0 - float(cosine_distance))
        if score >= settings.retrieval_min_score:
            results.append((chunk, score))
    return results
