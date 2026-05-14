"""测试 RAG Service 模块。"""

import pytest
from unittest.mock import MagicMock, patch

from models.responses import ChatResponse, SourceDocument
from services.rag_service import (
    generate_answer,
    _apply_history_window,
    _summarize_history,
)


# 测试中使用的假 prompt 模板
FAKE_PROMPT_TEMPLATE = "参考：{context}\n问题：{query}"


# ── 辅助函数 ———————————————————————————————————————


def _make_history(user_count: int) -> list[dict]:
    """构造 user/assistant 交替的假历史消息列表。"""
    history = []
    for i in range(1, user_count + 1):
        history.append({"role": "user", "content": f"用户问题 {i}"})
        history.append({"role": "assistant", "content": f"AI 回答 {i}"})
    return history


# ── 滑动窗口截断 ———————————————————————————————————


class TestApplyHistoryWindow:
    def test_empty_history(self):
        assert _apply_history_window([]) == []

    def test_within_window_returns_all(self):
        history = _make_history(5)
        result = _apply_history_window(history, max_rounds=10)
        assert len(result) == 10
        assert result == history

    def test_exceeds_window_truncates(self):
        history = _make_history(30)
        result = _apply_history_window(history, max_rounds=20)
        assert len(result) == 40  # 20 rounds = 40 messages
        # 第一条应为第 11 轮的用户问题
        assert result[0] == {"role": "user", "content": "用户问题 11"}

    def test_exceeds_window_by_one(self):
        history = _make_history(6)
        result = _apply_history_window(history, max_rounds=5)
        assert len(result) == 10
        assert result[0]["content"] == "用户问题 2"

    def test_uses_settings_default(self):
        history = _make_history(25)
        with patch("services.rag_service.settings") as mock_settings:
            mock_settings.max_history_rounds = 20
            result = _apply_history_window(history)
            assert len(result) == 40

    def test_preserves_message_order(self):
        history = _make_history(50)
        result = _apply_history_window(history, max_rounds=5)
        # 应是最近的 5 轮
        assert result[0]["content"] == "用户问题 46"
        assert result[-1]["content"] == "AI 回答 50"


# ── 对话摘要压缩 ———————————————————————————————————


class TestSummarizeHistory:
    def test_calls_llm_with_formatted_history(self):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "摘要内容"

        history = _make_history(3)
        with patch("services.rag_service._load_prompt", return_value="{history}"):
            result = _summarize_history(history, llm_client=mock_llm)

        mock_llm.chat.assert_called_once()
        call_kwargs = mock_llm.chat.call_args[1]
        assert "用户问题 1" in call_kwargs["user_message"]
        assert "AI 回答 1" in call_kwargs["user_message"]
        assert call_kwargs["system_prompt"] == "你是一个对话摘要助手。"
        assert result == "摘要内容"

    def test_creates_llm_client_when_none(self):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "auto summary"
        with (
            patch("services.rag_service._load_prompt", return_value="{history}"),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
        ):
            result = _summarize_history(_make_history(1))
            assert result == "auto summary"


# ── generate_answer 集成测试 ———————————————————————


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
                    "distance": 0.75,
                },
            ]

            result = generate_answer(query="test")
            assert result.sources[0].score == pytest.approx(0.95)
            assert result.sources[1].score == pytest.approx(0.625)

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
            assert src.score == pytest.approx(0.975)

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

    def test_short_history_passed_verbatim(self):
        """短历史应原样传递，不触发截断。"""
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "答案"

        short_history = _make_history(3)

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
            patch("services.rag_service.query_chunks") as mock_query,
            patch("services.rag_service._load_prompt", return_value=FAKE_PROMPT_TEMPLATE),
        ):
            mock_query.return_value = [
                {"id": "c1", "text": "content", "metadata": {"source": "doc.txt"}, "distance": 0.3}
            ]

            generate_answer(query="test", history=short_history)

            call_kwargs = mock_llm.chat.call_args[1]
            assert len(call_kwargs["history"]) == 6

    def test_long_history_with_summary_uses_cached(self):
        """30 轮历史 + 缓存摘要：仅窗口截断 + 注入摘要，不额外调用 LLM。"""
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "答案"

        long_history = _make_history(30)

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
            patch("services.rag_service.query_chunks") as mock_query,
            patch("services.rag_service._load_prompt", return_value=FAKE_PROMPT_TEMPLATE),
            patch("services.rag_service.settings") as mock_settings,
        ):
            mock_settings.max_history_rounds = 20
            mock_settings.hybrid_enabled = False
            mock_query.return_value = [
                {"id": "c1", "text": "content", "metadata": {"source": "doc.txt"}, "distance": 0.3}
            ]

            generate_answer(query="test", history=long_history, summary="缓存摘要")

            assert mock_llm.chat.call_count == 1
            call_kwargs = mock_llm.chat.call_args[1]
            history_arg = call_kwargs["history"]
            assert history_arg[0]["role"] == "system"
            assert "缓存摘要" in history_arg[0]["content"]
            # 1 system + 20 rounds (40 messages) = 41
            assert len(history_arg) == 41

    def test_no_history_ok(self):
        """无历史消息时应正常返回。"""
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "答案"

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
            patch("services.rag_service.query_chunks") as mock_query,
            patch("services.rag_service._load_prompt", return_value=FAKE_PROMPT_TEMPLATE),
        ):
            mock_query.return_value = [
                {"id": "c1", "text": "content", "metadata": {"source": "doc.txt"}, "distance": 0.3}
            ]

            result = generate_answer(query="test", history=None)

            assert result.answer == "答案"
            mock_llm.chat.assert_called_once()
            assert mock_llm.chat.call_args[1]["history"] == []

    def test_summary_none_does_not_inject_system_message(self):
        """summary=None 时不注入 system 消息，仅保留窗口截断后的逐字历史。"""
        mock_embed = MagicMock()
        mock_embed.embed_query.return_value = [0.1] * 1536

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "答案"

        short_history = _make_history(5)

        with (
            patch("services.rag_service.get_embedding_client", return_value=mock_embed),
            patch("services.rag_service.get_llm_client", return_value=mock_llm),
            patch("services.rag_service.query_chunks") as mock_query,
            patch("services.rag_service._load_prompt", return_value=FAKE_PROMPT_TEMPLATE),
        ):
            mock_query.return_value = [
                {"id": "c1", "text": "content", "metadata": {"source": "doc.txt"}, "distance": 0.3}
            ]

            generate_answer(query="test", history=short_history, summary=None)

            call_kwargs = mock_llm.chat.call_args[1]
            # 全部 5 轮逐字，无 system 摘要
            assert len(call_kwargs["history"]) == 10
            assert all(h["role"] != "system" for h in call_kwargs["history"])
