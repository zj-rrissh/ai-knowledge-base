"""测试各分块策略及策略路由。"""

import pytest
from unittest.mock import MagicMock, patch

from chunking.strategy import Chunk, get_strategy
from chunking.default_strategy import DefaultFallbackStrategy
from chunking.txt_strategy import ParagraphChunkingStrategy
from chunking.markdown_strategy import MarkdownChunkingStrategy
from chunking.pdf_strategy import PdfWordChunkingStrategy

PATCH_SPLITTER = "chunking.default_strategy.SentenceSplitter"


class TestChunkDataclass:
    def test_creates_with_text_and_metadata(self):
        c = Chunk(text="hello", metadata={"key": "val"})
        assert c.text == "hello"
        assert c.metadata == {"key": "val"}

    def test_default_metadata_empty(self):
        c = Chunk(text="x")
        assert c.metadata == {}


class TestDefaultFallbackStrategy:
    def test_uses_sentence_splitter(self):
        with patch(PATCH_SPLITTER) as mock_splitter_cls:
            mock_node = MagicMock()
            mock_node.get_content.return_value = "sentence chunk"
            mock_splitter_cls.return_value.get_nodes_from_documents.return_value = [mock_node]

            strategy = DefaultFallbackStrategy(chunk_size=100, chunk_overlap=10)
            chunks = strategy.chunk("test text")
            assert len(chunks) == 1
            assert chunks[0].text == "sentence chunk"

    def test_metadata_preserved(self):
        with patch(PATCH_SPLITTER) as mock_cls:
            mock_node = MagicMock()
            mock_node.get_content.return_value = "text"
            mock_cls.return_value.get_nodes_from_documents.return_value = [mock_node]

            strategy = DefaultFallbackStrategy(chunk_size=100, chunk_overlap=10)
            chunks = strategy.chunk("text", {"source": "doc.txt"})
            assert chunks[0].metadata["source"] == "doc.txt"

    def test_chunk_count(self):
        with patch(PATCH_SPLITTER) as mock_cls:
            nodes = [MagicMock() for _ in range(3)]
            for n in nodes:
                n.get_content.return_value = "chunk"
            mock_cls.return_value.get_nodes_from_documents.return_value = nodes

            strategy = DefaultFallbackStrategy(chunk_size=100, chunk_overlap=10)
            chunks = strategy.chunk("a b c")
            assert len(chunks) == 3


class TestParagraphChunkingStrategy:
    def test_splits_at_double_newline(self):
        strategy = ParagraphChunkingStrategy(chunk_size=512, chunk_overlap=50)
        text = "段落一内容\n\n段落二内容\n\n段落三内容"
        chunks = strategy.chunk(text)
        assert len(chunks) == 3
        assert chunks[0].text == "段落一内容"
        assert chunks[2].text == "段落三内容"

    def test_paragraph_index_metadata(self):
        strategy = ParagraphChunkingStrategy(chunk_size=512, chunk_overlap=50)
        text = "first\n\nsecond"
        chunks = strategy.chunk(text)
        assert chunks[0].metadata["paragraph_index"] == "0"
        assert chunks[1].metadata["paragraph_index"] == "1"

    def test_filters_empty_paragraphs(self):
        strategy = ParagraphChunkingStrategy(chunk_size=512, chunk_overlap=50)
        text = "para1\n\n\n\npara2"
        chunks = strategy.chunk(text)
        assert len(chunks) == 2

    def test_empty_text(self):
        strategy = ParagraphChunkingStrategy()
        chunks = strategy.chunk("")
        assert chunks == []

    def test_whitespace_only(self):
        strategy = ParagraphChunkingStrategy()
        chunks = strategy.chunk("\n\n \n\n")
        assert chunks == []

    def test_large_paragraph_subdivided(self):
        strategy = ParagraphChunkingStrategy(chunk_size=50, chunk_overlap=10)
        text = "这是超过五十个字符的一段长文本内容。" * 10
        chunks = strategy.chunk(text)
        assert len(chunks) > 1
        for c in chunks:
            assert c.metadata["paragraph_index"] == "0"

    def test_metadata_propagated(self):
        strategy = ParagraphChunkingStrategy(chunk_size=512, chunk_overlap=50)
        chunks = strategy.chunk("hello", {"source": "doc.txt", "document_id": "1"})
        assert chunks[0].metadata["source"] == "doc.txt"
        assert chunks[0].metadata["document_id"] == "1"

    # ── 中文句边界优化专用用例 ─────────────────────────────────────

    def test_chinese_sentence_boundary_split(self):
        """中文句号（。）作句子边界，句子不被截断。"""
        strategy = ParagraphChunkingStrategy(chunk_size=20, chunk_overlap=0)
        text = "强化学习是一种机器学习范式。智能体通过与环境交互来学习。奖励信号驱动策略优化。"
        chunks = strategy.chunk(text)
        assert len(chunks) == 3
        assert all(c.text.endswith("。") for c in chunks)

    def test_chinese_mixed_punctuation_split(self):
        """中文多种句末标点（？！；。）均作边界。"""
        strategy = ParagraphChunkingStrategy(chunk_size=10, chunk_overlap=0)
        text = "这是第一句？这是第二句！这是第三句；这是第四句。"
        chunks = strategy.chunk(text)
        # 每个句子 6 字，chunk_size=10 放不下两句（含空格 13），所以 4 个块
        assert len(chunks) == 4

    def test_chinese_and_english_mixed(self):
        """中英文混排段落：中文句号优先分隔。"""
        strategy = ParagraphChunkingStrategy(chunk_size=35, chunk_overlap=0)
        text = "本文介绍Transformer架构。It is based on self-attention。该机制效果显著。"
        chunks = strategy.chunk(text)
        assert len(chunks) == 3

    def test_pure_english_fallback(self):
        """纯英文文档走 English split 兜底。"""
        strategy = ParagraphChunkingStrategy(chunk_size=30, chunk_overlap=0)
        text = "Hello world. This is a test. Split at sentences. Each one is short."
        chunks = strategy.chunk(text)
        assert len(chunks) >= 3

    def test_no_punctuation_hard_split(self):
        """无标点时按字符数硬切。"""
        strategy = ParagraphChunkingStrategy(chunk_size=20, chunk_overlap=0)
        text = "这是一个完全没有标点符号的超长字符串用来测试硬切分的兜底逻辑" * 3
        chunks = strategy.chunk(text)
        assert len(chunks) >= 3


class TestMarkdownChunkingStrategy:
    def test_splits_at_headings(self):
        strategy = MarkdownChunkingStrategy(max_chunk_size=1024)
        text = "# 标题一\n内容一\n\n## 标题二\n内容二\n\n# 标题三\n内容三"
        chunks = strategy.chunk(text)
        assert len(chunks) == 3

    def test_heading_path_metadata(self):
        strategy = MarkdownChunkingStrategy(max_chunk_size=1024)
        text = "# 安装\n安装说明\n\n## 快速开始\n快速开始内容"
        chunks = strategy.chunk(text)
        heading_paths = [c.metadata.get("heading_path", "") for c in chunks]
        assert any("# 安装" in p for p in heading_paths)
        assert any("## 快速开始" in p for p in heading_paths)

    def test_heading_level_metadata(self):
        strategy = MarkdownChunkingStrategy(max_chunk_size=1024)
        text = "## 二级标题\n内容"
        chunks = strategy.chunk(text)
        assert chunks[0].metadata["heading_level"] == "2"

    def test_no_headings_fallback(self):
        strategy = MarkdownChunkingStrategy(max_chunk_size=1024)
        text = "这是没有标题的普通文本，使用 SentenceSplitter 兜底。"
        chunks = strategy.chunk(text)
        assert len(chunks) >= 1

    def test_empty_document(self):
        strategy = MarkdownChunkingStrategy()
        chunks = strategy.chunk("   ")
        assert chunks == []

    def test_preamble_before_first_heading(self):
        strategy = MarkdownChunkingStrategy(max_chunk_size=1024)
        text = "前言内容\n\n# 第一章\n正文"
        chunks = strategy.chunk(text)
        preamble = [c for c in chunks if c.metadata.get("heading_path") == "(前言)"]
        assert len(preamble) == 1
        assert preamble[0].text == "前言内容"

    def test_nested_headings(self):
        strategy = MarkdownChunkingStrategy(max_chunk_size=1024)
        text = "# H1\nh1 content\n\n## H2\nh2 content\n\n### H3\nh3 content"
        chunks = strategy.chunk(text)
        paths = [c.metadata.get("heading_path", "") for c in chunks]
        assert any("# H1 > ## H2 > ### H3" in p for p in paths)


class TestPdfWordChunkingStrategy:
    def test_splits_at_chinese_punctuation(self):
        strategy = PdfWordChunkingStrategy(chunk_size=20, chunk_overlap=5)
        text = "这是第一句话。这是第二句话。这是第三句话。"
        chunks = strategy.chunk(text)
        assert len(chunks) >= 2

    def test_empty_text(self):
        strategy = PdfWordChunkingStrategy()
        chunks = strategy.chunk("")
        assert chunks == []

    def test_short_text_single_chunk(self):
        strategy = PdfWordChunkingStrategy(chunk_size=512, chunk_overlap=50)
        text = "短短一句话。"
        chunks = strategy.chunk(text)
        assert len(chunks) == 1

    def test_metadata_propagated(self):
        strategy = PdfWordChunkingStrategy(chunk_size=512, chunk_overlap=50)
        chunks = strategy.chunk("测试文本。", {"source": "doc.pdf"})
        assert chunks[0].metadata["source"] == "doc.pdf"

    def test_long_text_many_chunks(self):
        strategy = PdfWordChunkingStrategy(chunk_size=50, chunk_overlap=10)
        text = "。".join([f"这是第{i}句测试内容" for i in range(20)]) + "。"
        chunks = strategy.chunk(text)
        assert len(chunks) > 1


class TestGetStrategy:
    def test_txt_extension_returns_paragraph_strategy(self):
        s = get_strategy("/data/doc.txt")
        assert isinstance(s, ParagraphChunkingStrategy)

    def test_md_extension_returns_markdown_strategy(self):
        s = get_strategy("/data/readme.md")
        assert isinstance(s, MarkdownChunkingStrategy)

    def test_pdf_extension_returns_pdf_strategy(self):
        s = get_strategy("/data/report.pdf")
        assert isinstance(s, PdfWordChunkingStrategy)

    def test_docx_extension_returns_pdf_strategy(self):
        s = get_strategy("/data/report.docx")
        assert isinstance(s, PdfWordChunkingStrategy)

    def test_unknown_extension_returns_default(self):
        s = get_strategy("/data/file.xyz")
        assert isinstance(s, DefaultFallbackStrategy)

    def test_no_extension_returns_default(self):
        s = get_strategy("/data/noext")
        assert isinstance(s, DefaultFallbackStrategy)

    def test_content_type_takes_priority(self):
        s = get_strategy(
            "/data/file.bin",
            metadata={"content_type": "text/markdown"},
        )
        assert isinstance(s, MarkdownChunkingStrategy)

    def test_content_type_for_pdf(self):
        s = get_strategy(
            "/data/unknown.xyz",
            metadata={"content_type": "application/pdf"},
        )
        assert isinstance(s, PdfWordChunkingStrategy)

    def test_strategy_caching(self):
        s1 = get_strategy("/data/a.txt")
        s2 = get_strategy("/data/b.txt")
        assert s1 is s2

    def test_case_insensitive_extensions(self):
        s = get_strategy("/data/FILE.TXT")
        assert isinstance(s, ParagraphChunkingStrategy)
