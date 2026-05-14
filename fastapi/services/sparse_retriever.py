"""BM25 稀疏检索器 —— 关键词倒排索引召回。

每个用户独立一个语料库（JSON 持久化），启动时从语料重建 BM25 索引。
中文分词优先用 jieba，不可用时回退到字符级分词。
"""
import json
import os
import logging
from collections.abc import Iterable

from rank_bm25 import BM25Okapi

from config import settings

log = logging.getLogger(__name__)

try:
    import jieba
    _HAS_JIEBA = True
except ImportError:
    _HAS_JIEBA = False


def _tokenize(text: str) -> list[str]:
    if _HAS_JIEBA:
        return [w for w in jieba.cut(text) if w.strip()]
    return list(text)


class SparseRetriever:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._corpus: list[str] = []
        self._bm25: BM25Okapi | None = None
        self._chunks: list[dict] = []
        self._load()

    def _corpus_path(self) -> str:
        return os.path.join(settings.chroma_persist_dir, f"corpus_{self.user_id}.json")

    def _load(self):
        path = self._corpus_path()
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                self._corpus = data.get("corpus", [])
                self._chunks = data.get("chunks", [])
                if self._corpus:
                    tokenized = [_tokenize(doc) for doc in self._corpus]
                    self._bm25 = BM25Okapi(tokenized)
            except Exception:
                log.warning("Failed to load corpus for user %s", self.user_id, exc_info=True)

    def _save(self):
        os.makedirs(settings.chroma_persist_dir, exist_ok=True)
        with open(self._corpus_path(), "w", encoding="utf-8") as f:
            json.dump({"corpus": self._corpus, "chunks": self._chunks}, f, ensure_ascii=False)

    def build_index(self, chunks: list[str], metadatas: list[dict] | None = None):
        """用 chunks 重建全局索引（增量追加到现有语料后重建）。"""
        if metadatas is None:
            metadatas = [{}] * len(chunks)
        self._corpus.extend(chunks)
        self._chunks.extend(
            {"text": c, "metadata": m} for c, m in zip(chunks, metadatas)
        )
        tokenized = [_tokenize(doc) for doc in self._corpus]
        self._bm25 = BM25Okapi(tokenized)
        self._save()

    def delete_document(self, document_id: str):
        """按 document_id 删除对应的 chunks 并重建索引。"""
        keep_corpus = []
        keep_chunks = []
        for i, chunk in enumerate(self._chunks):
            if chunk.get("metadata", {}).get("document_id") == document_id:
                continue
            keep_corpus.append(self._corpus[i])
            keep_chunks.append(chunk)
        self._corpus = keep_corpus
        self._chunks = keep_chunks
        if self._corpus:
            tokenized = [_tokenize(doc) for doc in self._corpus]
            self._bm25 = BM25Okapi(tokenized)
        else:
            self._bm25 = None
        self._save()

    def search(self, query: str, top_k: int = 20) -> list[dict]:
        if not self._bm25 or not self._corpus:
            return []
        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [
            {
                "text": self._chunks[idx]["text"],
                "score": float(score),
                "metadata": self._chunks[idx].get("metadata", {}),
            }
            for idx, score in ranked[:top_k]
        ]

    def is_ready(self) -> bool:
        return self._bm25 is not None and len(self._corpus) > 0


_retrievers: dict[int, SparseRetriever] = {}


def get_sparse_retriever(user_id: int) -> SparseRetriever:
    if user_id not in _retrievers:
        _retrievers[user_id] = SparseRetriever(user_id)
    return _retrievers[user_id]
