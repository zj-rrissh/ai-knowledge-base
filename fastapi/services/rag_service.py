import os
from services.llm_client import get_llm_client
from services.embedding_client import get_embedding_client
from services.vector_store import query_chunks
from models.responses import ChatResponse, SourceDocument

_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


def _load_prompt(name: str = "default") -> str:
    with open(os.path.join(_PROMPT_DIR, f"{name}.txt"), encoding="utf-8") as f:
        return f.read()


def generate_answer(query: str, user_id: int = 1, top_k: int = 4) -> ChatResponse:
    embed_client = get_embedding_client()
    query_embedding = embed_client.embed_query(query)

    chunks = query_chunks(user_id=user_id, query_embedding=query_embedding, top_k=top_k)

    if not chunks:
        return ChatResponse(
            answer="知识库中暂无相关文档，无法回答此问题。",
            sources=[],
        )

    context_parts = []
    for c in chunks:
        doc_name = c.get("metadata", {}).get("source", "未知文档")
        context_parts.append(f"[文档: {doc_name}]\n{c['text']}")
    context = "\n\n---\n\n".join(context_parts)

    prompt_template = _load_prompt()
    system_prompt = prompt_template.format(context=context, query=query)
    user_message = query

    llm_client = get_llm_client()
    answer = llm_client.chat(system_prompt=system_prompt, user_message=user_message)

    sources = [
        SourceDocument(
            doc_name=c.get("metadata", {}).get("source", "未知"),
            chunk_text=c["text"][:200],
            score=round(1.0 - c.get("distance", 0), 4),
        )
        for c in chunks
    ]

    return ChatResponse(answer=answer, sources=sources)
