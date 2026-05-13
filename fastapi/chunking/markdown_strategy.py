import re

from llama_index.core.node_parser import SentenceSplitter

from chunking.strategy import BaseChunkingStrategy, Chunk
from config import settings

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


class MarkdownChunkingStrategy(BaseChunkingStrategy):
    def __init__(self, max_chunk_size: int | None = None):
        self._max_chunk_size = max_chunk_size or getattr(
            settings, "markdown_max_chunk_size", 1024
        )

    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]:
        meta = dict(metadata or {})
        if not text.strip():
            return []

        headings = list(_HEADING_RE.finditer(text))
        if not headings:
            splitter = SentenceSplitter(chunk_size=self._max_chunk_size, chunk_overlap=50)
            from llama_index.core import Document as LiDocument

            doc = LiDocument(text=text)
            nodes = splitter.get_nodes_from_documents([doc])
            return [
                Chunk(text=node.get_content(), metadata=dict(meta))
                for node in nodes
            ]

        chunks: list[Chunk] = []
        heading_stack: list[tuple[int, str]] = []

        for idx, match in enumerate(headings):
            level = len(match.group(1))
            title = match.group(2).strip()
            start = match.end() + 1

            end = headings[idx + 1].start() if idx + 1 < len(headings) else len(text)

            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))

            heading_path = " > ".join(f"{'#' * lvl} {t}" for lvl, t in heading_stack)
            section_text = text[start:end].strip()

            if not section_text:
                continue

            if len(section_text) <= self._max_chunk_size:
                sec_meta = {
                    **meta,
                    "heading_path": heading_path,
                    "heading_level": str(level),
                }
                chunks.append(Chunk(text=section_text, metadata=sec_meta))
            else:
                splitter = SentenceSplitter(
                    chunk_size=self._max_chunk_size, chunk_overlap=50
                )
                from llama_index.core import Document as LiDocument

                doc = LiDocument(text=section_text)
                nodes = splitter.get_nodes_from_documents([doc])
                for node in nodes:
                    node_meta = {
                        **meta,
                        "heading_path": heading_path,
                        "heading_level": str(level),
                    }
                    chunks.append(Chunk(text=node.get_content(), metadata=node_meta))

        # 第一个标题前的内容
        if headings:
            preamble_end = headings[0].start()
            preamble = text[:preamble_end].strip()
            if preamble:
                chunks.insert(
                    0,
                    Chunk(
                        text=preamble,
                        metadata={**meta, "heading_path": "(前言)", "heading_level": "0"},
                    ),
                )

        return chunks
