from pydantic import BaseModel, Field
from typing import Optional


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query in English or Japanese")
    top_k: Optional[int] = Field(default=3, ge=1, le=10, description="Number of results to return")


class GenerateRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query in English or Japanese")
    output_language: Optional[str] = Field(
        default=None, 
        description="Output language: 'en' or 'ja'. Defaults to query language"
    )
    top_k: Optional[int] = Field(default=3, ge=1, le=10, description="Number of context chunks to retrieve")

