from abc import ABC, abstractmethod

from openai import OpenAI

from config import settings, LLM_PROVIDER_MAP


class BaseLLMClient(ABC):
    @abstractmethod
    def chat(self, system_prompt: str, user_message: str, **kwargs) -> str:
        ...


class OpenAILikeLLMClient(BaseLLMClient):
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(self, system_prompt: str, user_message: str, history: list[dict] | None = None, **kwargs) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for h in history:
                role = h.get("role", "user")
                if role not in ("user", "assistant"):
                    role = "user"
                messages.append({"role": role, "content": h.get("content", "")})
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.1),
        )
        return response.choices[0].message.content  # type: ignore


def get_llm_client() -> BaseLLMClient:
    base_url = settings.llm_base_url or LLM_PROVIDER_MAP.get(settings.llm_provider, "")
    return OpenAILikeLLMClient(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=base_url,
    )
