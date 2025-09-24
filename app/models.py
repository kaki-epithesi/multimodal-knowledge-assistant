from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    q: str
    top_k: int = 3  # default return 3 snippets


class Snippet(BaseModel):
    text: str
    score: float


class QueryResponse(BaseModel):
    query: str
    results: List[Snippet]
    answer: Optional[str] = None