"""测试 Vector Store 模块。"""

import pytest
from unittest.mock import MagicMock, patch

from services.vector_store import (
    _get_client,
    get_collection,
    add_chunks,
    query_chunks,
    delete_chunks,
    health_check,
)

# 保存模块初始状态以便恢复
import services.vector_store as vs


class TestGetClient:
    def setup_method(self):
        vs._client = None

    def test_lazy_initialization(self):
        with patch("services.vector_store.chromadb.PersistentClient") as mock_pc:
            vs._client = None
            client = _get_client()
            assert client is not None
            mock_pc.assert_called_once()

    def test_singleton_behaviour(self):
        with patch("services.vector_store.chromadb.PersistentClient") as mock_pc:
            vs._client = None
            client1 = _get_client()
            client2 = _get_client()
            assert client1 is client2
            mock_pc.assert_called_once()

    def test_passes_correct_path(self):
        with patch(
            "services.vector_store.chromadb.PersistentClient"
        ) as mock_pc, patch(
            "services.vector_store.settings.chroma_persist_dir", "./custom_path"
        ):
            vs._client = None
            _get_client()
            mock_pc.assert_called_once()
            kwargs = mock_pc.call_args[1]
            assert "path" in kwargs


class TestGetCollection:
    def test_uses_correct_name(self):
        with patch("services.vector_store._get_client") as mock_gc:
            mock_collection = MagicMock()
            mock_gc.return_value.get_or_create_collection.return_value = mock_collection

            result = get_collection(user_id=1)
            mock_gc.return_value.get_or_create_collection.assert_called_once_with(
                name="kb_1"
            )
            assert result == mock_collection

    def test_different_users_get_different_collections(self):
        with patch("services.vector_store._get_client") as mock_gc:
            mock_collection = MagicMock()
            mock_gc.return_value.get_or_create_collection.return_value = mock_collection

            get_collection(user_id=1)
            get_collection(user_id=2)
            calls = mock_gc.return_value.get_or_create_collection.call_args_list
            assert calls[0][1]["name"] == "kb_1"
            assert calls[1][1]["name"] == "kb_2"


class TestAddChunks:
    def test_calls_collection_add(self):
        with patch("services.vector_store.get_collection") as mock_gc:
            mock_collection = MagicMock()
            mock_gc.return_value = mock_collection

            add_chunks(
                user_id=1,
                chunk_ids=["c1", "c2"],
                chunk_texts=["t1", "t2"],
                embeddings=[[0.1], [0.2]],
                metadatas=[{"s": "d1"}, {"s": "d1"}],
            )
            mock_collection.add.assert_called_once_with(
                ids=["c1", "c2"],
                documents=["t1", "t2"],
                embeddings=[[0.1], [0.2]],
                metadatas=[{"s": "d1"}, {"s": "d1"}],
            )


class TestQueryChunks:
    def test_returns_list_of_dicts(self):
        with patch("services.vector_store.get_collection") as mock_gc:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                "ids": [["c1", "c2"]],
                "documents": [["txt1", "txt2"]],
                "metadatas": [[{"s": "d1"}, {"s": "d1"}]],
                "distances": [[0.1, 0.2]],
            }
            mock_gc.return_value = mock_collection

            results = query_chunks(
                user_id=1, query_embedding=[0.1, 0.2, 0.3], top_k=2
            )
            assert len(results) == 2
            assert results[0]["id"] == "c1"
            assert results[0]["text"] == "txt1"
            assert results[0]["metadata"] == {"s": "d1"}
            assert results[0]["distance"] == 0.1

    def test_query_passes_embedding_and_top_k(self):
        with patch("services.vector_store.get_collection") as mock_gc:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                "ids": [["c1"]],
                "documents": [["txt1"]],
                "metadatas": [[{}]],
                "distances": [[0.1]],
            }
            mock_gc.return_value = mock_collection

            query_chunks(user_id=1, query_embedding=[0.5, 0.5], top_k=5)
            mock_collection.query.assert_called_once_with(
                query_embeddings=[[0.5, 0.5]], n_results=5
            )

    def test_empty_result(self):
        with patch("services.vector_store.get_collection") as mock_gc:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }
            mock_gc.return_value = mock_collection

            results = query_chunks(user_id=1, query_embedding=[0.1])
            assert results == []

    def test_handles_missing_metadatas(self):
        with patch("services.vector_store.get_collection") as mock_gc:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                "ids": [["c1"]],
                "documents": [["txt1"]],
                "metadatas": None,
                "distances": None,
            }
            mock_gc.return_value = mock_collection

            results = query_chunks(user_id=1, query_embedding=[0.1])
            assert len(results) == 1
            assert results[0]["metadata"] == {}
            assert results[0]["distance"] == 0


class TestDeleteChunks:
    def test_calls_collection_delete(self):
        with patch("services.vector_store.get_collection") as mock_gc:
            mock_collection = MagicMock()
            mock_gc.return_value = mock_collection

            delete_chunks(user_id=1, chunk_ids=["c1", "c2"])
            mock_collection.delete.assert_called_once_with(ids=["c1", "c2"])


class TestHealthCheck:
    def test_returns_true_when_client_works(self):
        with patch("services.vector_store._get_client") as mock_gc:
            mock_gc.return_value = MagicMock()
            assert health_check() is True

    def test_returns_false_on_exception(self):
        with patch(
            "services.vector_store._get_client",
            side_effect=Exception("DB Error"),
        ):
            assert health_check() is False
