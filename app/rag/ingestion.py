from pathlib import Path

from sqlalchemy import delete, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_texts
from app.rag.models import Base, DocumentChunk

settings = get_settings()


def ensure_schema(db: Session) -> None:
    db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    db.commit()
    Base.metadata.create_all(bind=db.get_bind())


def ingest_directory(db: Session, directory: str = "data/sample_docs") -> dict[str, int]:
    ensure_schema(db)
    base = Path(directory)
    files = sorted([p for p in base.glob("**/*") if p.is_file() and p.suffix.lower() in {".txt", ".md"}])

    total_chunks = 0
    for file_path in files:
        document_name = file_path.name
        text_content = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(text_content, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            continue

        embeddings = embed_texts(chunks)
        db.execute(delete(DocumentChunk).where(DocumentChunk.document == document_name))
        for index, (content, embedding) in enumerate(zip(chunks, embeddings)):
            db.add(
                DocumentChunk(
                    document=document_name,
                    chunk_index=index,
                    content=content,
                    embedding=embedding,
                )
            )
            total_chunks += 1
        db.commit()

    return {"documents": len(files), "chunks": total_chunks}
