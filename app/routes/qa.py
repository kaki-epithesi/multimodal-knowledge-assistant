from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse, Snippet
from app.services.retriever import Retriever
from app.services.summarizer import summarize
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query_docs(request: QueryRequest):
    try:
        retriever = Retriever()
        results = retriever.query(request.q, request.top_k)
        snippets = [Snippet(text=txt, score=score) for txt, score in results]

        # combine top-k snippets and run summarizer
        combined_text = " ".join([s.text for s in snippets])
        if not combined_text:
            answer = ""
        else:
            # trim to safe size
            combined_text = combined_text[:6000]
            try:
                answer = summarize(combined_text, method="transformer", max_length=200, min_length=50)
            except Exception as e:
                logger.exception("Transformer summarizer failed, falling back to TextRank")
                # fallback
                answer = summarize(combined_text, method="textrank", sentences_count=3)

        return QueryResponse(query=request.q, results=snippets, answer=answer)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Index not built yet. Please ingest docs first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))