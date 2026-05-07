from typing import Literal

from pydantic_settings import BaseSettings


LLM_PROVIDER_MAP: dict[str, str] = {
    "deepseek": "https://api.deepseek.com/v1",
    "openai": "https://api.openai.com/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "ollama": "http://localhost:11434/v1",
}

EMBED_PROVIDER_MAP: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "ollama": "http://localhost:11434/v1",
}


class Settings(BaseSettings):
    # ── LLM ──
    llm_provider: Literal["deepseek", "openai", "zhipu", "qwen", "ollama"] = "deepseek"
    llm_model: str = "deepseek-chat"
    llm_api_key: str = ""
    llm_base_url: str = ""

    # ── Embedding ──
    embed_provider: Literal["openai", "zhipu", "qwen", "ollama"] = "openai"
    embed_model: str = "text-embedding-3-small"
    embed_api_key: str = ""
    embed_base_url: str = ""

    # ── ChromaDB ──
    chroma_persist_dir: str = "./chroma_data"
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # ── Ingestion ──
    chunk_size: int = 512
    chunk_overlap: int = 50

    @property
    def resolved_llm_base_url(self) -> str:
        """Return the explicitly configured base URL or fall back to the provider default."""
        return self.llm_base_url or LLM_PROVIDER_MAP.get(self.llm_provider, "")

    @property
    def resolved_embed_base_url(self) -> str:
        """Return the explicitly configured base URL or fall back to the provider default."""
        return self.embed_base_url or EMBED_PROVIDER_MAP.get(self.embed_provider, "")

    @property
    def resolved_embed_api_key(self) -> str:
        """Return the embedding API key or fall back to the LLM key."""
        return self.embed_api_key or self.llm_api_key

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
