import re

from chunking.strategy import BaseChunkingStrategy, Chunk
from config import settings

_CN_SENT_END = re.compile(r"[。！？；」』）】》]")
_EN_SENT_END = re.compile(r"[.!?]\s+")


class PdfWordChunkingStrategy(BaseChunkingStrategy):
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        self._chunk_size = chunk_size or settings.chunk_size
        self._chunk_overlap = chunk_overlap or settings.chunk_overlap

    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]:
        meta = dict(metadata or {})
        if not text.strip():
            return []

        chunks: list[Chunk] = []
        pos = 0
        text_len = len(text)

        while pos < text_len:
            end = min(pos + self._chunk_size, text_len)
            if end >= text_len:
                remaining = text[pos:].strip()
                if remaining:
                    chunks.append(Chunk(text=remaining, metadata=dict(meta)))
                break

            window = text[pos:end]
            cut = self._find_boundary(window)

            if cut > 0:
                end = pos + cut + 1

            chunk_text = text[pos:end].strip()
            if chunk_text:
                chunks.append(Chunk(text=chunk_text, metadata=dict(meta)))

            next_pos = end - self._chunk_overlap
            if next_pos <= pos:
                next_pos = end
            pos = next_pos

        return chunks

    def _find_boundary(self, window: str) -> int:
        last_cn = -1
        for m in _CN_SENT_END.finditer(window):
            last_cn = m.start()
        if last_cn >= 0:
            return last_cn

        last_en = -1
        for m in _EN_SENT_END.finditer(window):
            last_en = m.start()
        if last_en >= 0:
            return last_en

        last_space = window.rfind(" ")
        if last_space > 0:
            return last_space

        return -1
