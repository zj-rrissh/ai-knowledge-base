from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from services.embedding_client import get_embedding_client
from services.vector_store import add_chunks, delete_chunks
from config import settings


def ingest_document(file_path: str, document_id: int, user_id: int = 1) -> dict:
    """摄取文档：解析→分块→向量化→存入 ChromaDB"""
    try:
        reader = SimpleDirectoryReader(input_files=[file_path])
        docs = reader.load_data()

        if not docs:
            return {"status": "failed", "error_message": "无法解析文档内容"}

        parser = SentenceSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        nodes = parser.get_nodes_from_documents(docs)

        chunk_texts = [node.get_content() for node in nodes]
        chunk_ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunk_texts))]

        embed_client = get_embedding_client()
        embeddings = embed_client.embed(chunk_texts)

        metadatas = [
            {"document_id": str(document_id), "chunk_index": str(i), "source": file_path}
            for i in range(len(chunk_texts))
        ]

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
