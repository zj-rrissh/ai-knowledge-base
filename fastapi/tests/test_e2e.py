import tempfile
import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    """健康检查端点应返回 200 且包含 status 字段"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_ingest_invalid_file():
    """上传不存在的文件应返回 failed 状态"""
    response = client.post("/ingest", json={
        "file_path": "/nonexistent/file.pdf",
        "document_id": 1,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"


def test_chat_empty_knowledge_base():
    """空知识库查询应返回无参考资料"""
    response = client.post("/chat", json={
        "session_id": "test-session-1",
        "query": "公司考勤制度是什么？",
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["sources"] == []
