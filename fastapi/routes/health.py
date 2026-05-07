from fastapi import APIRouter
from services.vector_store import health_check as chroma_health
from services.llm_client import get_llm_client
from models.responses import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health():
    llm_ok = "unavailable"
    try:
        client = get_llm_client()
        client.chat("echo", "ping")
        llm_ok = "available"
    except Exception:
        pass

    return HealthResponse(
        status="ok" if chroma_health() and llm_ok == "available" else "degraded",
        chromadb="connected" if chroma_health() else "disconnected",
        llm_api=llm_ok,
    )
