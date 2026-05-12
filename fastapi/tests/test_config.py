"""测试 config 模块：Settings 解析、回退逻辑与 Request 模型验证。"""

import pytest
from pydantic import ValidationError

from config import Settings, LLM_PROVIDER_MAP, EMBED_PROVIDER_MAP
from models.requests import IngestRequest, ChatRequest


# ──────────────────────────────────────────────
# Settings 基本解析
# ──────────────────────────────────────────────


class TestSettingsDefaults:
    def test_default_llm_provider(self):
        s = Settings(_env_file=None)
        assert s.llm_provider == "deepseek"

    def test_default_llm_model(self):
        s = Settings(_env_file=None)
        assert s.llm_model == "deepseek-chat"

    def test_default_embed_provider(self):
        s = Settings(_env_file=None)
        assert s.embed_provider == "openai"

    def test_default_embed_model(self):
        s = Settings(_env_file=None)
        assert s.embed_model == "text-embedding-3-small"

    def test_default_chunk_settings(self):
        s = Settings(_env_file=None)
        assert s.chunk_size == 512
        assert s.chunk_overlap == 50


class TestSettingsFromEnv:
    def test_env_overrides_defaults(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "qwen")
        monkeypatch.setenv("LLM_MODEL", "qwen-max")
        s = Settings(_env_file=None)
        assert s.llm_provider == "qwen"
        assert s.llm_model == "qwen-max"

    def test_env_embed_settings(self, monkeypatch):
        monkeypatch.setenv("EMBED_PROVIDER", "zhipu")
        monkeypatch.setenv("EMBED_MODEL", "embedding-3")
        s = Settings(_env_file=None)
        assert s.embed_provider == "zhipu"
        assert s.embed_model == "embedding-3"


# ──────────────────────────────────────────────
# resolved_llm_base_url 回退逻辑
# ──────────────────────────────────────────────


class TestResolvedLLMBaseUrl:
    def test_custom_url_used_when_set(self):
        s = Settings(llm_base_url="http://my-proxy/v1", _env_file=None)
        assert s.resolved_llm_base_url == "http://my-proxy/v1"

    def test_fallback_to_provider_map(self):
        s = Settings(llm_provider="deepseek", llm_base_url="", _env_file=None)
        assert s.resolved_llm_base_url == LLM_PROVIDER_MAP["deepseek"]

    def test_fallback_different_provider(self):
        s = Settings(llm_provider="zhipu", llm_base_url="", _env_file=None)
        assert s.resolved_llm_base_url == LLM_PROVIDER_MAP["zhipu"]

    def test_fallback_ollama(self):
        s = Settings(llm_provider="ollama", llm_base_url="", _env_file=None)
        assert s.resolved_llm_base_url == LLM_PROVIDER_MAP["ollama"]


# ──────────────────────────────────────────────
# resolved_embed_base_url 回退逻辑
# ──────────────────────────────────────────────


class TestResolvedEmbedBaseUrl:
    def test_custom_url_used_when_set(self):
        s = Settings(embed_base_url="http://my-embed/v1", _env_file=None)
        assert s.resolved_embed_base_url == "http://my-embed/v1"

    def test_fallback_to_embed_provider_map(self):
        s = Settings(embed_provider="openai", embed_base_url="", _env_file=None)
        assert s.resolved_embed_base_url == EMBED_PROVIDER_MAP["openai"]

    def test_fallback_ollama_embed(self):
        s = Settings(embed_provider="ollama", embed_base_url="", _env_file=None)
        assert s.resolved_embed_base_url == EMBED_PROVIDER_MAP["ollama"]


# ──────────────────────────────────────────────
# resolved_embed_api_key 回退逻辑
# ──────────────────────────────────────────────


class TestResolvedEmbedApiKey:
    def test_own_key_used_when_set(self):
        s = Settings(embed_api_key="my-embed-key", _env_file=None)
        assert s.resolved_embed_api_key == "my-embed-key"

    def test_fallback_to_llm_key(self):
        s = Settings(embed_api_key="", llm_api_key="llm-fallback", _env_file=None)
        assert s.resolved_embed_api_key == "llm-fallback"

    def test_empty_when_both_empty(self):
        s = Settings(embed_api_key="", llm_api_key="", _env_file=None)
        assert s.resolved_embed_api_key == ""


# ──────────────────────────────────────────────
# PROVIDER_MAP 完整性
# ──────────────────────────────────────────────


class TestProviderMaps:
    def test_llm_provider_map_keys(self):
        assert set(LLM_PROVIDER_MAP.keys()) == {
            "deepseek",
            "openai",
            "zhipu",
            "qwen",
            "ollama",
        }

    def test_embed_provider_map_keys(self):
        assert set(EMBED_PROVIDER_MAP.keys()) == {
            "openai",
            "zhipu",
            "qwen",
            "ollama",
        }

    def test_llm_map_urls_not_empty(self):
        for url in LLM_PROVIDER_MAP.values():
            assert url.startswith("http") or url.startswith("https")


# ──────────────────────────────────────────────
# IngestRequest 验证
# ──────────────────────────────────────────────


class TestIngestRequest:
    def test_valid_request(self):
        req = IngestRequest(file_path="/data/doc.pdf", document_id=42)
        assert req.file_path == "/data/doc.pdf"
        assert req.document_id == 42
        assert req.user_id == 1
        assert req.metadata == {}

    def test_default_user_id(self):
        req = IngestRequest(file_path="/f.txt", document_id=7)
        assert req.user_id == 1

    def test_custom_user_id(self):
        req = IngestRequest(file_path="/f.txt", document_id=7, user_id=99)
        assert req.user_id == 99

    def test_custom_metadata(self):
        req = IngestRequest(
            file_path="/f.txt", document_id=7, metadata={"category": "hr"}
        )
        assert req.metadata == {"category": "hr"}

    def test_json_roundtrip(self):
        req = IngestRequest(file_path="/f.txt", document_id=7)
        data = req.model_dump()
        restored = IngestRequest(**data)
        assert restored.file_path == req.file_path
        assert restored.document_id == req.document_id


# ──────────────────────────────────────────────
# ChatRequest 验证
# ──────────────────────────────────────────────


class TestChatRequest:
    def test_valid_request(self):
        req = ChatRequest(session_id="sess-1", query="公司考勤制度")
        assert req.session_id == "sess-1"
        assert req.query == "公司考勤制度"
        assert req.user_id == 1
        assert req.top_k == 4

    def test_empty_query_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="sess-1", query="")

    def test_top_k_below_minimum(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="sess-1", query="hi", top_k=0)

    def test_top_k_above_maximum(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="sess-1", query="hi", top_k=21)

    def test_top_k_boundary_min(self):
        req = ChatRequest(session_id="sess-1", query="hi", top_k=1)
        assert req.top_k == 1

    def test_top_k_boundary_max(self):
        req = ChatRequest(session_id="sess-1", query="hi", top_k=20)
        assert req.top_k == 20

    def test_custom_user_id(self):
        req = ChatRequest(session_id="sess-1", query="hi", user_id=5)
        assert req.user_id == 5

    def test_json_roundtrip(self):
        req = ChatRequest(session_id="sess-1", query="hello", user_id=2, top_k=10)
        data = req.model_dump()
        restored = ChatRequest(**data)
        assert restored.session_id == req.session_id
        assert restored.query == req.query
        assert restored.user_id == req.user_id
        assert restored.top_k == req.top_k
