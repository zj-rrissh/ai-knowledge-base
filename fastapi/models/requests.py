from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    file_path: str = Field(..., description="文件绝对路径")
    document_id: int = Field(..., description="SpringBoot 侧的文档 ID")
    user_id: int = Field(default=1, description="用户 ID，用于 collection 隔离")
    metadata: dict = Field(default_factory=dict, description="自定义元数据")


class HistoryMessage(BaseModel):
    role: str = Field(..., description="消息角色: user / assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="会话唯一标识")
    query: str = Field(..., min_length=1, description="用户问题")
    user_id: int = Field(default=1, description="用户 ID")
    top_k: int = Field(default=4, ge=1, le=20, description="检索文档块数量")
    history: list[HistoryMessage] = Field(default_factory=list, description="会话历史消息，用于多轮上下文感知")
    summary: str | None = Field(default=None, description="缓存的对话摘要，由 Spring Boot 异步生成")


class SummarizeRequest(BaseModel):
    session_id: str = Field(..., description="会话唯一标识")
    history: list[HistoryMessage] = Field(..., description="需要摘要的完整历史消息")
