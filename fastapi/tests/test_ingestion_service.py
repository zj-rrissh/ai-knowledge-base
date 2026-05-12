"""测试 Ingestion Service 模块。"""

import pytest
from unittest.mock import MagicMock, patch

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
            patch(
                "services.ingestion_service.SentenceSplitter"
            ) as mock_splitter_class,
        ):
            # Mock reader
            mock_doc = MagicMock()
            mock_doc.get_content.return_value = "full document content"
            mock_reader_instance = MagicMock()
            mock_reader_instance.load_data.return_value = [mock_doc]
            mock_reader.return_value = mock_reader_instance

            # Mock splitter
            mock_node1 = MagicMock()
            mock_node1.get_content.return_value = "chunk 1 content"
            mock_node2 = MagicMock()
            mock_node2.get_content.return_value = "chunk 2 content"
            splitter_instance = mock_splitter_class.return_value
            splitter_instance.get_nodes_from_documents.return_value = [
                mock_node1,
                mock_node2,
            ]

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
            patch("services.ingestion_service.SentenceSplitter") as mock_splitter_cls,
        ):
            mock_doc = MagicMock()
            mock_doc.get_content.return_value = "content"
            mock_reader_instance = MagicMock()
            mock_reader_instance.load_data.return_value = [mock_doc]
            mock_reader.return_value = mock_reader_instance

            mock_node = MagicMock()
            mock_node.get_content.return_value = "chunk"
            splitter = mock_splitter_cls.return_value
            splitter.get_nodes_from_documents.return_value = [mock_node]

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
            patch("services.ingestion_service.SentenceSplitter") as mock_splitter_cls,
        ):
            mock_doc = MagicMock()
            mock_doc.get_content.return_value = "content"
            mock_reader_instance = MagicMock()
            mock_reader_instance.load_data.return_value = [mock_doc]
            mock_reader.return_value = mock_reader_instance

            mock_node = MagicMock()
            mock_node.get_content.return_value = "chunk"
            splitter = mock_splitter_cls.return_value
            splitter.get_nodes_from_documents.return_value = [mock_node]

            ingest_document(file_path="/data/doc.pdf", document_id=77, user_id=2)

            mock_add.assert_called_once()
            metadatas = mock_add.call_args[1]["metadatas"]
            assert metadatas[0]["document_id"] == "77"
            assert metadatas[0]["source"] == "/data/doc.pdf"
            assert metadatas[0]["chunk_index"] == "0"

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
