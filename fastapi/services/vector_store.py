import chromadb
from chromadb.api import ClientAPI
from config import settings

_client = None


def _get_client() -> ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
    return _client


def get_collection(user_id: int = 1):
    """获取用户专属 collection，不存在则创建（使用 cosine 距离）"""
    client = _get_client()
    name = f"kb_{user_id}"
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(
    user_id: int,
    chunk_ids: list[str],
    chunk_texts: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
):
    collection = get_collection(user_id)
    collection.add(
        ids=chunk_ids,
        documents=chunk_texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def query_chunks(
    user_id: int,
    query_embedding: list[float],
    top_k: int = 4,
) -> list[dict]:
    collection = get_collection(user_id)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    items = []
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            items.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0,
            })
    return items


def delete_chunks(user_id: int, chunk_ids: list[str]):
    collection = get_collection(user_id)
    collection.delete(ids=chunk_ids)


def delete_document_chunks(user_id: int, document_id: int) -> int:
    collection = get_collection(user_id)
    results = collection.get(
        where={"document_id": str(document_id)},
        include=[],
    )
    ids = results["ids"]
    if ids:
        collection.delete(ids=ids)
    return len(ids)


def health_check() -> bool:
    try:
        _ = _get_client()
        return True
    except Exception:
        return False
