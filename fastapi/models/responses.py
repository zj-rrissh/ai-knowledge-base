from pydantic import BaseModel, Field
from typing import Literal


class IngestResponse(BaseModel):
    document_id: int
    status: Literal["indexed", "failed"]
    chunk_count: int = 0
    error_message: str | None = None


class SourceDocument(BaseModel):
    doc_name: str
    chunk_text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDocument]


class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="生成的对话摘要")


class MetadataResponse(BaseModel):
    title: str = Field(..., description="AI 生成的文档标题")
    description: str = Field(default="", description="AI 生成的文档描述")
    tags: str = Field(default="", description="逗号分隔的标签")


class HealthResponse(BaseModel):
    status: str
    chromadb: Literal["connected", "disconnected"]
    llm_api: Literal["available", "unavailable"]
