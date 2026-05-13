from llama_index.core.node_parser import SentenceSplitter

from chunking.strategy import BaseChunkingStrategy, Chunk
from config import settings


class ParagraphChunkingStrategy(BaseChunkingStrategy):
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        self._chunk_size = chunk_size or settings.chunk_size
        self._chunk_overlap = chunk_overlap or settings.chunk_overlap

    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]:
        meta = dict(metadata or {})
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            return []

        chunks: list[Chunk] = []
        splitter = SentenceSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
        )
        for i, para in enumerate(paragraphs):
            if len(para) <= self._chunk_size:
                para_meta = {**meta, "paragraph_index": str(i)}
                chunks.append(Chunk(text=para, metadata=para_meta))
            else:
                from llama_index.core import Document as LiDocument

                doc = LiDocument(text=para)
                nodes = splitter.get_nodes_from_documents([doc])
                for node in nodes:
                    node_meta = {**meta, "paragraph_index": str(i)}
                    chunks.append(Chunk(text=node.get_content(), metadata=node_meta))
        return chunks
