from fastapi import APIRouter
from models.requests import IngestRequest
from models.responses import IngestResponse
from services.ingestion_service import ingest_document
from services.vector_store import delete_document_chunks, get_collection
from services.sparse_retriever import get_sparse_retriever
import os

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
def ingest(req: IngestRequest):
    result = ingest_document(
        file_path=req.file_path,
        document_id=req.document_id,
        user_id=req.user_id,
        metadata=req.metadata or None,
    )
    return IngestResponse(
        document_id=req.document_id,
        status=result["status"],
        chunk_count=result.get("chunk_count", 0),
        error_message=result.get("error_message"),
    )


@router.delete("/{document_id}")
def delete_document(document_id: int, user_id: int = 1):
    # 删除前获取 metadata，尝试清理物理文件
    try:
        collection = get_collection(user_id)
        doc_data = collection.get(
            where={"document_id": str(document_id)},
            include=["metadatas"],
        )
        if doc_data["metadatas"]:
            file_path = str(doc_data["metadatas"][0].get("file_path", ""))
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
    except Exception:
        pass

    deleted = delete_document_chunks(user_id=user_id, document_id=document_id)
    retriever = get_sparse_retriever(user_id)
    retriever.delete_document(str(document_id))
    return {"document_id": document_id, "status": "deleted", "chunks_removed": deleted}
