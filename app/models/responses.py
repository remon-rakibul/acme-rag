from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class IngestedDocument(BaseModel):
    filename: str
    language: str
    chunks: int
    size: int


class IngestResponse(BaseModel):
    status: str
    ingested: int
    documents: List[IngestedDocument]
    errors: Optional[List[str]] = None
    total_documents_in_index: int


class RetrievedDocument(BaseModel):
    id: int
    text: str
    language: str
    filename: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)


class RetrieveResponse(BaseModel):
    query: str
    results: List[RetrievedDocument]
    total_results: int


class GenerateResponse(BaseModel):
    query: str
    refined_query: Optional[str] = None
    response: str
    language: str
    retrieved_context: List[Dict]
    num_context_docs: int
    debug_info: Optional[Dict] = None

