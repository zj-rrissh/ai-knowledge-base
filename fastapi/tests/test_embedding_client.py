"""测试 Embedding Client 模块。"""

import pytest
from unittest.mock import patch, MagicMock

from services.embedding_client import (
    BaseEmbeddingClient,
    OpenAIEmbeddingClient,
    get_embedding_client,
)


class TestBaseEmbeddingClient:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            BaseEmbeddingClient()


class TestOpenAIEmbeddingClient:
    def test_constructor_creates_openai_client(self):
        with patch("services.embedding_client.OpenAI") as mock_openai:
            OpenAIEmbeddingClient(
                model="text-embedding-3-small",
                api_key="key",
                base_url="http://test/v1",
            )
            mock_openai.assert_called_once_with(
                api_key="key", base_url="http://test/v1"
            )

    def test_embed_returns_vector_list(self, mock_openai_client):
        client = OpenAIEmbeddingClient(
            model="text-embedding-3-small",
            api_key="key",
            base_url="http://test/v1",
        )
        result = client.embed(["hello", "world"])
        assert len(result) == 2
        assert isinstance(result[0], list)
        assert len(result[0]) == 4

    def test_embed_passes_correct_model(self):
        with patch("services.embedding_client.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_embed = MagicMock()
            mock_embed.data = [MagicMock(embedding=[0.1])]
            mock_client.embeddings.create.return_value = mock_embed
            mock_openai.return_value = mock_client

            client = OpenAIEmbeddingClient(
                model="text-embedding-ada-002",
                api_key="key",
                base_url="http://test/v1",
            )
            client.embed(["text1", "text2"])

            mock_client.embeddings.create.assert_called_once_with(
                model="text-embedding-ada-002", input=["text1", "text2"]
            )

    def test_embed_query_returns_single_vector(self, mock_openai_client):
        client = OpenAIEmbeddingClient(
            model="text-embedding-3-small",
            api_key="key",
            base_url="http://test/v1",
        )
        result = client.embed_query("test query")
        assert isinstance(result, list)
        assert len(result) == 4

    def test_embed_query_calls_embed(self):
        client = OpenAIEmbeddingClient(
            model="text-embedding-3-small",
            api_key="key",
            base_url="http://test/v1",
        )
        with patch.object(client, "embed", return_value=[[0.1, 0.2]]) as mock_embed:
            result = client.embed_query("query")
            mock_embed.assert_called_once_with(["query"])
            assert result == [0.1, 0.2]

    def test_error_propagation(self):
        client = OpenAIEmbeddingClient(
            model="text-embedding-3-small",
            api_key="key",
            base_url="http://test/v1",
        )
        with patch.object(
            client.client.embeddings,
            "create",
            side_effect=Exception("Embedding Error"),
        ):
            with pytest.raises(Exception, match="Embedding Error"):
                client.embed(["text"])


class TestGetEmbeddingClient:
    def test_returns_openai_embedding_client(self, mock_settings):
        client = get_embedding_client()
        assert isinstance(client, OpenAIEmbeddingClient)

    def test_uses_settings_values(self, mock_settings):
        client = get_embedding_client()
        assert client.model == "text-embedding-3-small"
