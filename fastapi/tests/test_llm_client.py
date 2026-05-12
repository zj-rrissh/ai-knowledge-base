"""测试 LLM Client 模块。"""

import pytest
from unittest.mock import patch, MagicMock

from services.llm_client import (
    BaseLLMClient,
    OpenAILikeLLMClient,
    get_llm_client,
)


class TestBaseLLMClient:
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            BaseLLMClient()


class TestOpenAILikeLLMClient:
    def test_constructor_sets_attributes(self):
        client = OpenAILikeLLMClient(
            model="gpt-4", api_key="test-key", base_url="http://test/v1"
        )
        assert client.model == "gpt-4"

    def test_constructor_creates_openai_client(self):
        with patch("services.llm_client.OpenAI") as mock_openai:
            OpenAILikeLLMClient(
                model="gpt-4", api_key="test-key", base_url="http://test/v1"
            )
            mock_openai.assert_called_once_with(
                api_key="test-key", base_url="http://test/v1"
            )

    def test_chat_returns_text(self, mock_openai_client):
        client = OpenAILikeLLMClient(
            model="gpt-4", api_key="key", base_url="http://test/v1"
        )
        response = client.chat("system prompt", "user message")
        assert response == "AI response"
        assert isinstance(response, str)

    def test_chat_passes_correct_messages(self):
        with patch("services.llm_client.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "reply"
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_completion = MagicMock()
            mock_completion.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_completion
            mock_openai.return_value = mock_client

            client = OpenAILikeLLMClient(
                model="gpt-4", api_key="key", base_url="http://test/v1"
            )
            client.chat("You are a helper", "Hello")

            mock_client.chat.completions.create.assert_called_once()
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "gpt-4"
            assert call_kwargs["messages"] == [
                {"role": "system", "content": "You are a helper"},
                {"role": "user", "content": "Hello"},
            ]

    def test_chat_passes_custom_temperature(self):
        with patch("services.llm_client.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "reply"
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_completion = MagicMock()
            mock_completion.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_completion
            mock_openai.return_value = mock_client

            client = OpenAILikeLLMClient(
                model="gpt-4", api_key="key", base_url="http://test/v1"
            )
            client.chat("system", "user", temperature=0.5)
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["temperature"] == 0.5

    def test_chat_error_propagation(self):
        client = OpenAILikeLLMClient(
            model="gpt-4", api_key="key", base_url="http://test/v1"
        )
        with patch.object(
            client.client.chat.completions,
            "create",
            side_effect=Exception("API Error"),
        ):
            with pytest.raises(Exception, match="API Error"):
                client.chat("system", "user")


class TestGetLLMClient:
    def test_returns_openai_like_client(self, mock_settings):
        client = get_llm_client()
        assert isinstance(client, OpenAILikeLLMClient)

    def test_uses_settings_values(self, mock_settings):
        client = get_llm_client()
        assert client.model == "gpt-4o-mini"
