"""共享 fixtures 和 mock 环境配置。"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _disable_hybrid(monkeypatch):
    """所有测试默认使用纯密集检索，避免 BM25 副作用。"""
    import config
    monkeypatch.setattr(config.settings, "hybrid_enabled", False)


@pytest.fixture
def mock_settings(monkeypatch):
    """将 config.settings 的各属性替换为测试安全的值。

    修改直接在 config.settings 对象上进行，因而对所有持有相同引用的模块均生效。
    """
    import config

    monkeypatch.setattr(config.settings, "llm_provider", "openai")
    monkeypatch.setattr(config.settings, "llm_model", "gpt-4o-mini")
    monkeypatch.setattr(config.settings, "llm_api_key", "test-llm-key")
    monkeypatch.setattr(config.settings, "llm_base_url", "")
    monkeypatch.setattr(config.settings, "embed_provider", "openai")
    monkeypatch.setattr(config.settings, "embed_model", "text-embedding-3-small")
    monkeypatch.setattr(config.settings, "embed_api_key", "test-embed-key")
    monkeypatch.setattr(config.settings, "embed_base_url", "")
    monkeypatch.setattr(config.settings, "chroma_persist_dir", "/tmp/test_chroma")
    monkeypatch.setattr(config.settings, "chunk_size", 512)
    monkeypatch.setattr(config.settings, "chunk_overlap", 50)
    monkeypatch.setattr(config.settings, "max_history_rounds", 20)
    monkeypatch.setattr(config.settings, "summary_trigger_rounds", 10)
    monkeypatch.setattr(config.settings, "keep_recent_rounds", 6)
    monkeypatch.setattr(config.settings, "hybrid_enabled", False)
    monkeypatch.setattr(config.settings, "dense_top_k", 20)
    monkeypatch.setattr(config.settings, "sparse_top_k", 20)
    monkeypatch.setattr(config.settings, "rrf_k", 60)
    return config.settings


@pytest.fixture
def mock_openai_client():
    """Mock openai.OpenAI at service import sites, making chat and embedding return controlled results."""
    with patch("services.llm_client.OpenAI") as mock_llm_openai, \
         patch("services.embedding_client.OpenAI") as mock_embed_openai:
        # ── Chat completion ──
        mock_message = MagicMock()
        mock_message.content = "AI response"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_chat_completion = MagicMock()
        mock_chat_completion.choices = [mock_choice]

        mock_llm_client_instance = MagicMock()
        mock_llm_client_instance.chat.completions.create.return_value = mock_chat_completion
        mock_llm_openai.return_value = mock_llm_client_instance

        # ── Embedding ──
        mock_embed_item = MagicMock()
        mock_embed_item.embedding = [0.1, 0.2, 0.3, 0.4]
        mock_embed_response = MagicMock()
        mock_embed_response.data = [mock_embed_item, mock_embed_item]

        mock_embed_client_instance = MagicMock()
        mock_embed_client_instance.embeddings.create.return_value = mock_embed_response
        mock_embed_openai.return_value = mock_embed_client_instance

        yield {
            "llm": mock_llm_openai,
            "embed": mock_embed_openai,
        }


@pytest.fixture
def mock_llm_client():
    """Mock get_llm_client 在所有引用点，返回受控的 BaseLLMClient。"""
    mock = MagicMock()
    mock.chat.return_value = "Mocked LLM response"
    with (
        patch("services.llm_client.get_llm_client", return_value=mock),
        patch("services.rag_service.get_llm_client", return_value=mock),
        patch("routes.health.get_llm_client", return_value=mock),
    ):
        yield mock


@pytest.fixture
def mock_embedding_client():
    """Mock get_embedding_client 在所有引用点，返回受控的 embedding client。"""
    mock = MagicMock()
    mock.embed.return_value = [[0.1] * 1536, [0.2] * 1536]
    mock.embed_query.return_value = [0.1] * 1536
    with (
        patch("services.embedding_client.get_embedding_client", return_value=mock),
        patch("services.rag_service.get_embedding_client", return_value=mock),
        patch("services.ingestion_service.get_embedding_client", return_value=mock),
    ):
        yield mock


@pytest.fixture
def mock_vector_store():
    """Mock services.vector_store 的所有公有函数。"""
    with (
        patch("services.vector_store.add_chunks") as mock_add,
        patch("services.vector_store.query_chunks") as mock_query,
        patch("services.vector_store.delete_chunks") as mock_delete,
        patch("services.vector_store.get_collection") as mock_get_coll,
        patch("services.vector_store._get_client") as mock_get_client,
        patch(
            "services.vector_store.health_check", return_value=True
        ) as mock_health,
    ):
        mock_query.return_value = [
            {
                "id": "chunk1",
                "text": "test content 1",
                "metadata": {"source": "doc1.txt"},
                "distance": 0.1,
            },
            {
                "id": "chunk2",
                "text": "test content 2",
                "metadata": {"source": "doc1.txt"},
                "distance": 0.2,
            },
        ]
        yield {
            "add": mock_add,
            "query": mock_query,
            "delete": mock_delete,
            "get_collection": mock_get_coll,
            "get_client": mock_get_client,
            "health_check": mock_health,
        }


@pytest.fixture
def test_app(mock_settings, mock_llm_client, mock_embedding_client, mock_vector_store):
    """提供挂载了所有 mock 路由的 FastAPI TestClient。"""
    from main import app

    return TestClient(app)
