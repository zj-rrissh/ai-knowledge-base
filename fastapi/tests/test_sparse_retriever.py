"""测试 BM25 稀疏检索器模块。"""

import json
import os
import tempfile
from unittest.mock import patch

from services.sparse_retriever import SparseRetriever, get_sparse_retriever, _tokenize


class TestTokenize:
    def test_basic_tokenization(self):
        tokens = _tokenize("Hello World 测试")
        assert len(tokens) > 0


class TestSparseRetriever:
    @patch("services.sparse_retriever.settings")
    def test_build_and_search(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.chroma_persist_dir = tmpdir

            retriever = SparseRetriever(user_id=1)
            retriever.build_index(
                ["考勤制度规定上班时间为 9:00", "迟到 30 分钟以上需提交说明"],
                [
                    {"document_id": "1", "source": "hr.txt"},
                    {"document_id": "1", "source": "hr.txt"},
                ],
            )

            assert retriever.is_ready()
            results = retriever.search("上班时间", top_k=5)
            assert len(results) > 0
            assert "9:00" in results[0]["text"]

    @patch("services.sparse_retriever.settings")
    def test_empty_corpus_returns_empty(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.chroma_persist_dir = tmpdir
            retriever = SparseRetriever(user_id=2)
            assert not retriever.is_ready()
            assert retriever.search("test") == []

    @patch("services.sparse_retriever.settings")
    def test_delete_document(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.chroma_persist_dir = tmpdir

            retriever = SparseRetriever(user_id=3)
            retriever.build_index(
                ["文档A 内容", "文档B 内容"],
                [
                    {"document_id": "1", "source": "a.txt"},
                    {"document_id": "2", "source": "b.txt"},
                ],
            )

            retriever.delete_document("1")
            results = retriever.search("文档", top_k=5)
            assert len(results) == 1
            assert results[0]["metadata"]["document_id"] == "2"

    @patch("services.sparse_retriever.settings")
    def test_persist_and_reload(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.chroma_persist_dir = tmpdir

            retriever1 = SparseRetriever(user_id=4)
            retriever1.build_index(["测试内容 ABC"], [{"document_id": "1"}])

            retriever2 = SparseRetriever(user_id=4)
            assert retriever2.is_ready()
            results = retriever2.search("ABC", top_k=5)
            assert len(results) == 1


class TestGetSparseRetriever:
    @patch("services.sparse_retriever.settings")
    def test_singleton_per_user(self, mock_settings):
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_settings.chroma_persist_dir = tmpdir
            a = get_sparse_retriever(1)
            b = get_sparse_retriever(1)
            assert a is b
