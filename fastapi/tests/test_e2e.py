from unittest.mock import patch

from fastapi.testclient import TestClient


def test_health(test_app):
    """健康检查端点应返回 200 且包含 status 字段"""
    response = test_app.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_ingest_invalid_file(test_app):
    """上传不存在的文件应返回 failed 状态"""
    response = test_app.post("/ingest", json={
        "file_path": "/nonexistent/file.pdf",
        "document_id": 1,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"


def test_chat_empty_knowledge_base(test_app):
    """无匹配文档时查询应返回无参考资料"""
    with patch("services.vector_store.query_chunks", return_value=[]):
        response = test_app.post("/chat", json={
            "session_id": "test-session-1",
            "query": "abc123xyz_unmatchable_query_foobar",
        })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["sources"] == []
