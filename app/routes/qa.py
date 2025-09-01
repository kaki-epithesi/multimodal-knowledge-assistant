from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse, Snippet
from app.services.retriever import Retriever

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_docs(request: QueryRequest):
    try:
        retriever = Retriever()
        results = retriever.query(request.q, request.top_k)
        snippets = [Snippet(text=txt, score=score) for txt, score in results]
        return QueryResponse(query=request.q, results=snippets)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Index not built yet. Please ingest docs first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))