from fastapi import APIRouter
from models.requests import ChatRequest, SummarizeRequest
from models.responses import ChatResponse, SummarizeResponse
from services.rag_service import generate_answer, _summarize_history

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    return generate_answer(
        query=req.query,
        user_id=req.user_id,
        top_k=req.top_k,
        history=[h.model_dump() for h in req.history] if req.history else None,
        summary=req.summary,
    )


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest):
    history = [h.model_dump() for h in req.history] if req.history else []
    summary = _summarize_history(history)
    return SummarizeResponse(summary=summary)
