"""测试路由端点。"""

import pytest
from unittest.mock import MagicMock, patch

from models.responses import ChatResponse


class TestHealthEndpoint:
    def test_health_returns_200(self, test_app):
        response = test_app.get("/health")
        assert response.status_code == 200

    def test_health_returns_correct_structure(self, test_app):
        response = test_app.get("/health")
        data = response.json()
        assert "status" in data
        assert "chromadb" in data
        assert "llm_api" in data

    def test_health_returns_ok(self, test_app):
        mock_client = MagicMock()
        mock_client.chat.return_value = "ok"
        with patch("routes.health.get_llm_client", return_value=mock_client), \
             patch("routes.health.chroma_health", return_value=True):
            response = test_app.get("/health")
            data = response.json()
            assert data["status"] == "ok"
            assert data["chromadb"] == "connected"
            assert data["llm_api"] == "available"


class TestIngestEndpoint:
    def test_ingest_success(self, test_app):
        with patch(
            "routes.ingest.ingest_document",
            return_value={"status": "indexed", "chunk_count": 5},
        ):
            response = test_app.post(
                "/ingest",
                json={"file_path": "/data/test.txt", "document_id": 42},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "indexed"
            assert data["chunk_count"] == 5
            assert data["document_id"] == 42

    def test_ingest_missing_required_fields(self, test_app):
        response = test_app.post("/ingest", json={"file_path": "/tmp/test.txt"})
        assert response.status_code == 422

    def test_ingest_empty_body(self, test_app):
        response = test_app.post("/ingest", json={})
        assert response.status_code == 422


class TestChatEndpoint:
    def test_chat_success(self, test_app):
        with patch(
            "routes.chat.generate_answer",
            return_value=ChatResponse(
                answer="AI 回答",
                sources=[],
            ),
        ):
            response = test_app.post(
                "/chat",
                json={
                    "session_id": "sess-1",
                    "query": "公司考勤制度是什么？",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == "AI 回答"
            assert data["sources"] == []

    def test_chat_missing_query(self, test_app):
        response = test_app.post(
            "/chat",
            json={"session_id": "sess-1", "query": ""},
        )
        assert response.status_code == 422

    def test_chat_missing_session_id(self, test_app):
        response = test_app.post(
            "/chat",
            json={"query": "hello"},
        )
        assert response.status_code == 422

    def test_chat_empty_body(self, test_app):
        response = test_app.post("/chat", json={})
        assert response.status_code == 422

    def test_chat_top_k_out_of_range(self, test_app):
        response = test_app.post(
            "/chat",
            json={"session_id": "sess-1", "query": "hi", "top_k": 25},
        )
        assert response.status_code == 422
