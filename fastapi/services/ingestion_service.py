from llama_index.core import SimpleDirectoryReader
from services.embedding_client import get_embedding_client
from services.vector_store import add_chunks, delete_chunks
from chunking.strategy import get_strategy


def ingest_document(file_path: str, document_id: int, user_id: int = 1,
                    metadata: dict | None = None) -> dict:
    """摄取文档：解析→按文件类型分块→向量化→存入 ChromaDB"""
    try:
        reader = SimpleDirectoryReader(input_files=[file_path])
        docs = reader.load_data()

        if not docs:
            return {"status": "failed", "error_message": "无法解析文档内容"}

        full_text = "\n\n".join(doc.get_content() for doc in docs)

        base_meta = {
            "document_id": str(document_id),
            "source": file_path,
            **(metadata or {}),
        }

        strategy = get_strategy(file_path, metadata)
        chunks = strategy.chunk(full_text, base_meta)

        chunk_texts: list[str] = []
        chunk_ids: list[str] = []
        metadatas: list[dict] = []
        for i, chunk in enumerate(chunks):
            chunk_ids.append(f"doc_{document_id}_chunk_{i}")
            chunk_texts.append(chunk.text)
            metadatas.append({**chunk.metadata, "chunk_index": str(i)})

        embed_client = get_embedding_client()
        embeddings = embed_client.embed(chunk_texts)

        add_chunks(
            user_id=user_id,
            chunk_ids=chunk_ids,
            chunk_texts=chunk_texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return {"status": "indexed", "chunk_count": len(chunk_texts)}

    except Exception as e:
        return {"status": "failed", "error_message": str(e)}
