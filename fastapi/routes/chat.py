from fastapi import APIRouter
from models.requests import ChatRequest
from models.responses import ChatResponse
from services.rag_service import generate_answer

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    return generate_answer(
        query=req.query,
        user_id=req.user_id,
        top_k=req.top_k,
    )
