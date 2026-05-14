import os
from services.llm_client import get_llm_client
from services.embedding_client import get_embedding_client
from services.vector_store import query_chunks
from models.responses import ChatResponse, SourceDocument
from config import settings

_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


def _load_prompt(name: str = "default") -> str:
    with open(os.path.join(_PROMPT_DIR, f"{name}.txt"), encoding="utf-8") as f:
        return f.read()


def _apply_history_window(
    history: list[dict],
    max_rounds: int | None = None,
) -> list[dict]:
    """滑动窗口截断：仅保留最近 N 轮对话。"""
    if not history:
        return history
    max_rounds = max_rounds or settings.max_history_rounds

    user_count = sum(1 for h in history if h.get("role") == "user")
    if user_count <= max_rounds:
        return history

    users_to_skip = user_count - max_rounds
    users_seen = 0
    cutoff_idx = 0
    for i, h in enumerate(history):
        if h.get("role") == "user":
            users_seen += 1
            if users_seen == users_to_skip + 1:
                cutoff_idx = i
                break

    return history[cutoff_idx:]


def _summarize_history(
    history: list[dict],
    llm_client=None,
) -> str:
    """使用 LLM 对历史对话生成摘要。"""
    if llm_client is None:
        llm_client = get_llm_client()

    lines = []
    for h in history:
        role = "用户" if h.get("role") == "user" else ("AI" if h.get("role") == "assistant" else "系统")
        lines.append(f"{role}: {h.get('content', '')}")
    history_text = "\n".join(lines)

    summary_prompt = _load_prompt("summary").format(history=history_text)
    return llm_client.chat(
        system_prompt="你是一个对话摘要助手。",
        user_message=summary_prompt,
    )


def generate_answer(query: str, user_id: int = 1, top_k: int = 4,
                    min_score: float = 0.2, history: list[dict] | None = None,
                    summary: str | None = None) -> ChatResponse:
    embed_client = get_embedding_client()
    query_embedding = embed_client.embed_query(query)

    chunks = query_chunks(user_id=user_id, query_embedding=query_embedding, top_k=top_k)
    chunks = [c for c in chunks if 1.0 - c.get("distance", 0) >= min_score]

    if not chunks:
        return ChatResponse(
            answer="知识库中暂无相关文档，无法回答此问题。",
            sources=[],
        )

    context_parts = []
    for c in chunks:
        raw_name = c.get("metadata", {}).get("source", "未知文档")
        doc_name = os.path.basename(raw_name) if raw_name.startswith("/") else raw_name
        context_parts.append(f"[文档: {doc_name}]\n{c['text']}")
    context = "\n\n---\n\n".join(context_parts)

    prompt_template = _load_prompt()
    system_prompt = prompt_template.format(context=context, query=query)
    user_message = query

    llm_client = get_llm_client()
    history = _apply_history_window(history or [])
    if summary:
        history = [
            {"role": "system", "content": f"以下是历史对话摘要：\n{summary}"},
            *history,
        ]
    answer = llm_client.chat(system_prompt=system_prompt, user_message=user_message, history=history)

    sources = [
        SourceDocument(
            doc_name=os.path.basename(c.get("metadata", {}).get("source", "未知"))
            if c.get("metadata", {}).get("source", "").startswith("/")
            else c.get("metadata", {}).get("source", "未知"),
            chunk_text=c["text"][:200],
            score=round(1.0 - c.get("distance", 0), 4),
        )
        for c in chunks
    ]

    return ChatResponse(answer=answer, sources=sources)
