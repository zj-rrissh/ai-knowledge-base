from fastapi import APIRouter
from models.requests import IngestRequest
from models.responses import IngestResponse
from services.ingestion_service import ingest_document
from services.vector_store import delete_document_chunks

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
def ingest(req: IngestRequest):
    result = ingest_document(
        file_path=req.file_path,
        document_id=req.document_id,
        user_id=req.user_id,
    )
    return IngestResponse(
        document_id=req.document_id,
        status=result["status"],
        chunk_count=result.get("chunk_count", 0),
        error_message=result.get("error_message"),
    )


@router.delete("/{document_id}")
def delete_document(document_id: int, user_id: int = 1):
    deleted = delete_document_chunks(user_id=user_id, document_id=document_id)
    return {"document_id": document_id, "status": "deleted", "chunks_removed": deleted}
