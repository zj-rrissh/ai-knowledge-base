import re

from chunking.strategy import BaseChunkingStrategy, Chunk
from config import settings

# Chinese sentence-ending punctuation — split AFTER these characters
_CN_SENT_SPLIT = re.compile(r"(?<=[。！？；」』）】》])")
# English sentence-ending punctuation followed by whitespace
_EN_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


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
        for i, para in enumerate(paragraphs):
            para_meta = {**meta, "paragraph_index": str(i)}
            if len(para) <= self._chunk_size:
                chunks.append(Chunk(text=para, metadata=para_meta))
            else:
                chunks.extend(self._split_long_paragraph(para, para_meta))
        return chunks

    # ── sentence splitting ──────────────────────────────────────────────

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences with bilingual boundary awareness.

        Priority:
          1) Chinese sentence endings (。！？；） — covers CJK documents
          2) English sentence endings (. ! ?) — covers mixed/English docs
          3) Hard character split — fallback for unpunctuated segments
        """
        # 1) Chinese sentence boundaries
        sentences = [s.strip() for s in _CN_SENT_SPLIT.split(text) if s.strip()]

        # 2) Fall through to English if no Chinese boundary was found
        if len(sentences) <= 1:
            sentences = [s.strip() for s in _EN_SENT_SPLIT.split(text) if s.strip()]

        # 3) Hard character split for any segment still exceeding chunk_size
        result: list[str] = []
        for s in sentences:
            if len(s) <= self._chunk_size:
                result.append(s)
            else:
                # Try newline split first, then character-level fallback
                for part in s.split("\n"):
                    part = part.strip()
                    if not part:
                        continue
                    if len(part) <= self._chunk_size:
                        result.append(part)
                    else:
                        for i in range(0, len(part), self._chunk_size):
                            result.append(part[i : i + self._chunk_size])
        return result

    # ── chunk assembly ──────────────────────────────────────────────────

    def _split_long_paragraph(self, text: str, base_meta: dict) -> list[Chunk]:
        """Accumulate sentences into chunks bounded by *chunk_size*."""
        sentences = self._split_sentences(text)
        chunks: list[Chunk] = []
        buffer = ""

        for sent in sentences:
            if len(sent) >= self._chunk_size:
                # Sentence too long to combine — flush buffer then emit standalone
                if buffer:
                    chunks.append(Chunk(text=buffer.strip(), metadata=dict(base_meta)))
                    buffer = ""
                chunks.append(Chunk(text=sent.strip(), metadata=dict(base_meta)))
                continue

            candidate = f"{buffer} {sent}".strip() if buffer else sent
            if len(candidate) <= self._chunk_size:
                buffer = candidate
            else:
                chunks.append(Chunk(text=buffer.strip(), metadata=dict(base_meta)))
                buffer = sent

        if buffer:
            chunks.append(Chunk(text=buffer.strip(), metadata=dict(base_meta)))

        return chunks
