from abc import ABC, abstractmethod

from openai import OpenAI

from config import settings, EMBED_PROVIDER_MAP


class BaseEmbeddingClient(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        ...


class OpenAIEmbeddingClient(BaseEmbeddingClient):
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]


def get_embedding_client() -> BaseEmbeddingClient:
    base_url = settings.embed_base_url or EMBED_PROVIDER_MAP.get(settings.embed_provider, "")
    api_key = settings.embed_api_key or "ollama"  # Ollama 不需要真实 key，但不能为空（httpx>=0.28 拒绝空 Bearer token）
    return OpenAIEmbeddingClient(
        model=settings.embed_model,
        api_key=api_key,
        base_url=base_url,
    )
