"""测试 RAG Service 模块。"""

import pytest
from unittest.mock import MagicMock, patch, mock_open

from models.responses import ChatResponse, SourceDocument
from services.rag_service import generate_answer


# 测试中使用的假 prompt 模板
FAKE_PROMPT_TEMPLATE = "参考：{context}\n问题：{query}"


class TestGenerateAnswer:
    def test_with_results_returns_answer(self):
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "根据文档，答案是 XYZ。"

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
            patch("services.rag_service.query_chunks") as mock_query,
            patch(
                "services.rag_service._load_prompt",
                return_value=FAKE_PROMPT_TEMPLATE,
            ),
        ):
            mock_query.return_value = [
                {
                    "id": "c1",
                    "text": "考勤制度规定上班时间为 9:00",
                    "metadata": {"source": "hr_policy.txt"},
                    "distance": 0.1,
                },
                {
                    "id": "c2",
                    "text": "迟到 30 分钟以上需提交说明",
                    "metadata": {"source": "hr_policy.txt"},
                    "distance": 0.2,
                },
            ]

            result = generate_answer(query="上班时间是什么？", user_id=1, top_k=4)

            assert isinstance(result, ChatResponse)
            assert result.answer == "根据文档，答案是 XYZ。"
            assert len(result.sources) == 2

    def test_scores_computed_correctly(self):
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "答案"

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
            patch("services.rag_service.query_chunks") as mock_query,
            patch(
                "services.rag_service._load_prompt",
                return_value=FAKE_PROMPT_TEMPLATE,
            ),
        ):
            mock_query.return_value = [
                {
                    "id": "c1",
                    "text": "content",
                    "metadata": {"source": "doc.txt"},
                    "distance": 0.1,
                },
                {
                    "id": "c2",
                    "text": "content2",
                    "metadata": {"source": "doc.txt"},
                    "distance": 0.85,
                },
            ]

            result = generate_answer(query="test")
            assert result.sources[0].score == pytest.approx(0.9)
            assert result.sources[1].score == pytest.approx(0.15)

    def test_no_results_returns_default_answer(self):
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.query_chunks") as mock_query,
        ):
            mock_query.return_value = []

            result = generate_answer(query="未知问题")

            assert result.answer == "知识库中暂无相关文档，无法回答此问题。"
            assert result.sources == []

    def test_source_document_contains_all_fields(self):
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "答案"

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
            patch("services.rag_service.query_chunks") as mock_query,
            patch(
                "services.rag_service._load_prompt",
                return_value=FAKE_PROMPT_TEMPLATE,
            ),
        ):
            mock_query.return_value = [
                {
                    "id": "c1",
                    "text": "A" * 500,
                    "metadata": {"source": "document.pdf"},
                    "distance": 0.05,
                }
            ]

            result = generate_answer(query="q")
            src = result.sources[0]
            assert isinstance(src, SourceDocument)
            assert src.doc_name == "document.pdf"
            assert len(src.chunk_text) == 200
            assert src.score == pytest.approx(0.95)

    def test_prompt_template_filled_correctly(self):
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "答案"

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
            patch("services.rag_service.query_chunks") as mock_query,
            patch(
                "services.rag_service._load_prompt",
                return_value=FAKE_PROMPT_TEMPLATE,
            ),
        ):
            mock_query.return_value = [
                {
                    "id": "c1",
                    "text": "规则内容",
                    "metadata": {"source": "rules.txt"},
                    "distance": 0.2,
                }
            ]

            generate_answer(query="有什么规则？")

            # 验证 LLM 收到的 prompt 包含 context 和 query
            mock_llm.chat.assert_called_once()
            _, kwargs = mock_llm.chat.call_args
            system_prompt = kwargs["system_prompt"]
            assert "规则内容" in system_prompt
            assert "有什么规则？" in system_prompt

    def test_llm_called_with_query_as_user_message(self):
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "答案"

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
            patch("services.rag_service.query_chunks") as mock_query,
            patch(
                "services.rag_service._load_prompt",
                return_value=FAKE_PROMPT_TEMPLATE,
            ),
        ):
            mock_query.return_value = [
                {
                    "id": "c1",
                    "text": "content",
                    "metadata": {"source": "doc.txt"},
                    "distance": 0.3,
                }
            ]

            generate_answer(query="用户问题")
            mock_llm.chat.assert_called_once()
            call_kwargs = mock_llm.chat.call_args[1]
            assert call_kwargs["user_message"] == "用户问题"

    def test_unknown_document_source_default(self):
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "答案"

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
            patch("services.rag_service.query_chunks") as mock_query,
            patch(
                "services.rag_service._load_prompt",
                return_value=FAKE_PROMPT_TEMPLATE,
            ),
        ):
            mock_query.return_value = [
                {
                    "id": "c1",
                    "text": "text",
                    "metadata": {},
                    "distance": 0.5,
                }
            ]

            result = generate_answer(query="test")
            assert result.sources[0].doc_name == "未知"
