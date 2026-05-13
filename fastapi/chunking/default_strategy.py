from llama_index.core import Document as LiDocument
from llama_index.core.node_parser import SentenceSplitter

from chunking.strategy import BaseChunkingStrategy, Chunk
from config import settings


class DefaultFallbackStrategy(BaseChunkingStrategy):
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        self._parser = SentenceSplitter(
            chunk_size=chunk_size or settings.chunk_size,
            chunk_overlap=chunk_overlap or settings.chunk_overlap,
        )

    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]:
        meta = dict(metadata or {})
        doc = LiDocument(text=text)
        nodes = self._parser.get_nodes_from_documents([doc])
        return [
            Chunk(text=node.get_content(), metadata=dict(meta))
            for node in nodes
        ]
