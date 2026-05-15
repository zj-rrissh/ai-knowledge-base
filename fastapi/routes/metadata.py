import json
import os

from fastapi import APIRouter, HTTPException
from models.requests import MetadataRequest
from models.responses import MetadataResponse
from services.llm_client import get_llm_client

router = APIRouter(prefix="/metadata", tags=["metadata"])

_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


def _extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".txt", ".md"):
        with open(file_path, encoding="utf-8", errors="replace") as f:
            return f.read()
    try:
        from llama_index.core import SimpleDirectoryReader
        docs = SimpleDirectoryReader(input_files=[file_path]).load_data()
        return "\n\n".join(d.get_content() for d in docs)
    except Exception:
        return ""


def _file_info(file_path: str) -> tuple[str, str]:
    ext = os.path.splitext(file_path)[1].lower()
    names = {".pdf": ("PDF", "PDF文档"), ".md": ("Markdown", "Markdown文档"), ".txt": ("文本", "文本文档")}
    return names.get(ext, ("文档", "文档"))


def _parse_json(text: str) -> dict:
    raw = text.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    return json.loads(raw)


@router.post("/generate", response_model=MetadataResponse)
def generate_metadata(req: MetadataRequest):
    if not os.path.exists(req.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    filename = req.filename or os.path.basename(req.file_path)
    file_type, default_type_tag = _file_info(req.file_path)

    try:
        content = _extract_text(req.file_path)
    except Exception:
        return MetadataResponse(
            title=os.path.basename(req.file_path).rsplit(".", 1)[0],
            description="",
            tags=default_type_tag,
        )

    if not content or not content.strip():
        return MetadataResponse(
            title=os.path.basename(req.file_path).rsplit(".", 1)[0],
            description="",
            tags=default_type_tag,
        )

    content = content[:3000]

    try:
        with open(os.path.join(_PROMPT_DIR, "metadata.txt"), encoding="utf-8") as f:
            prompt_template = f.read()
        llm = get_llm_client()
        response = llm.chat(
            system_prompt="你是一个文档元数据提取助手，请严格按照 JSON 格式输出。",
            user_message=prompt_template.format(
                filename=filename,
                file_type=file_type,
                content=content,
            ),
        )
        data = _parse_json(response)
        tags_list = data.get("tags", [])
        if not isinstance(tags_list, list):
            tags_list = [tags_list] if isinstance(tags_list, str) else []
        if not tags_list or tags_list[0] != default_type_tag:
            tags_list = [t for t in tags_list if t != default_type_tag]
            tags_list.insert(0, default_type_tag)
        tags_str = ",".join(tags_list)
        return MetadataResponse(
            title=str(data.get("title", filename))[:30],
            description=str(data.get("description", ""))[:150],
            tags=tags_str,
        )
    except Exception:
        return MetadataResponse(
            title=filename.rsplit(".", 1)[0],
            description="",
            tags=default_type_tag,
        )
