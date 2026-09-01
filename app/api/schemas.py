from pydantic import BaseModel, Field


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


class IngestResponse(BaseModel):
    documents: int
    chunks: int
