"""测试 Ingestion Service 模块。"""

import pytest
from unittest.mock import MagicMock, patch

from chunking.strategy import Chunk
from services.ingestion_service import ingest_document


class TestIngestDocument:
    def test_successful_ingestion(self, mock_settings):
        mock_embed = MagicMock()
        mock_embed.embed.return_value = [[0.1] * 1536, [0.2] * 1536]

        with (
            patch(
                "services.ingestion_service.get_embedding_client",
                return_value=mock_embed,
            ),
            patch("services.ingestion_service.add_chunks") as mock_add,
            patch("services.ingestion_service.SimpleDirectoryReader") as mock_reader,
            patch("services.ingestion_service.get_strategy") as mock_get_strategy,
        ):
            mock_doc = MagicMock()
            mock_doc.get_content.return_value = "full document content"
            mock_reader_instance = MagicMock()
            mock_reader_instance.load_data.return_value = [mock_doc]
            mock_reader.return_value = mock_reader_instance

            mock_strategy = MagicMock()
            mock_strategy.chunk.return_value = [
                Chunk(text="chunk 1 content", metadata={"document_id": "42", "source": "/data/test.txt"}),
                Chunk(text="chunk 2 content", metadata={"document_id": "42", "source": "/data/test.txt"}),
            ]
            mock_get_strategy.return_value = mock_strategy

            result = ingest_document(
                file_path="/data/test.txt", document_id=42, user_id=1
            )

            assert result["status"] == "indexed"
            assert result["chunk_count"] == 2

    def test_chunk_ids_format(self, mock_settings):
        mock_embed = MagicMock()
        mock_embed.embed.return_value = [[0.1] * 1536]

        with (
            patch(
                "services.ingestion_service.get_embedding_client",
                return_value=mock_embed,
            ),
            patch("services.ingestion_service.add_chunks") as mock_add,
            patch("services.ingestion_service.SimpleDirectoryReader") as mock_reader,
            patch("services.ingestion_service.get_strategy") as mock_get_strategy,
        ):
            mock_doc = MagicMock()
            mock_doc.get_content.return_value = "content"
            mock_reader_instance = MagicMock()
            mock_reader_instance.load_data.return_value = [mock_doc]
            mock_reader.return_value = mock_reader_instance

            mock_strategy = MagicMock()
            mock_strategy.chunk.return_value = [
                Chunk(text="chunk", metadata={"document_id": "99", "source": "/data/doc.txt"}),
            ]
            mock_get_strategy.return_value = mock_strategy

            ingest_document(file_path="/data/doc.txt", document_id=99, user_id=1)

            mock_add.assert_called_once()
            chunk_ids = mock_add.call_args[1]["chunk_ids"]
            assert chunk_ids == ["doc_99_chunk_0"]

    def test_metadatas_contain_document_id(self, mock_settings):
        mock_embed = MagicMock()
        mock_embed.embed.return_value = [[0.1] * 1536]

        with (
            patch(
                "services.ingestion_service.get_embedding_client",
                return_value=mock_embed,
            ),
            patch("services.ingestion_service.add_chunks") as mock_add,
            patch("services.ingestion_service.SimpleDirectoryReader") as mock_reader,
            patch("services.ingestion_service.get_strategy") as mock_get_strategy,
        ):
            mock_doc = MagicMock()
            mock_doc.get_content.return_value = "content"
            mock_reader_instance = MagicMock()
            mock_reader_instance.load_data.return_value = [mock_doc]
            mock_reader.return_value = mock_reader_instance

            mock_strategy = MagicMock()
            mock_strategy.chunk.return_value = [
                Chunk(text="chunk", metadata={"document_id": "77", "source": "/data/doc.pdf"}),
            ]
            mock_get_strategy.return_value = mock_strategy

            ingest_document(file_path="/data/doc.pdf", document_id=77, user_id=2)

            mock_add.assert_called_once()
            metadatas = mock_add.call_args[1]["metadatas"]
            assert metadatas[0]["document_id"] == "77"
            assert metadatas[0]["source"] == "/data/doc.pdf"
            assert metadatas[0]["chunk_index"] == "0"

    def test_metadata_passed_to_strategy(self, mock_settings):
        mock_embed = MagicMock()
        mock_embed.embed.return_value = [[0.1] * 1536]

        with (
            patch("services.ingestion_service.get_embedding_client", return_value=mock_embed),
            patch("services.ingestion_service.add_chunks"),
            patch("services.ingestion_service.SimpleDirectoryReader") as mock_reader,
            patch("services.ingestion_service.get_strategy") as mock_get_strategy,
        ):
            mock_doc = MagicMock()
            mock_doc.get_content.return_value = "content"
            mock_reader.return_value.load_data.return_value = [mock_doc]

            mock_strategy = MagicMock()
            mock_strategy.chunk.return_value = [
                Chunk(text="chunk", metadata={}),
            ]
            mock_get_strategy.return_value = mock_strategy

            ingest_document(
                file_path="/data/doc.pdf",
                document_id=1,
                user_id=1,
                metadata={"content_type": "application/pdf"},
            )

            mock_get_strategy.assert_called_once_with(
                "/data/doc.pdf", {"content_type": "application/pdf"}
            )

    def test_empty_document_returns_failed(self, mock_settings):
        with patch("services.ingestion_service.SimpleDirectoryReader") as mock_reader:
            mock_reader_instance = MagicMock()
            mock_reader_instance.load_data.return_value = []
            mock_reader.return_value = mock_reader_instance

            result = ingest_document(
                file_path="/data/empty.txt", document_id=1, user_id=1
            )
            assert result["status"] == "failed"
            assert "无法解析文档内容" in result["error_message"]

    def test_exception_captured_as_failed(self, mock_settings):
        with patch(
            "services.ingestion_service.SimpleDirectoryReader",
            side_effect=RuntimeError("文件读取失败"),
        ):
            result = ingest_document(
                file_path="/data/broken.txt", document_id=1, user_id=1
            )
            assert result["status"] == "failed"
            assert "文件读取失败" in result["error_message"]

    def test_file_not_found_returns_failed(self, mock_settings):
        result = ingest_document(
            file_path="/nonexistent/path/file.pdf", document_id=1, user_id=1
        )
        assert result["status"] == "failed"
        assert result.get("error_message") is not None

    def test_chunk_count_zero_when_ingestion_fails(self, mock_settings):
        with patch(
            "services.ingestion_service.SimpleDirectoryReader",
            side_effect=Exception("Error"),
        ):
            result = ingest_document(
                file_path="/data/fail.txt", document_id=1, user_id=1
            )
            assert result["status"] == "failed"
