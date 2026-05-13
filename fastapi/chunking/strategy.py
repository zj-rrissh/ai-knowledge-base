import importlib
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)


class BaseChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str, metadata: dict | None = None) -> list[Chunk]:
        ...


CONTENT_TYPE_MAP: dict[str, str] = {
    "application/pdf": ".pdf",
    "text/markdown": ".md",
    "text/plain": ".txt",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.ms-excel": ".xls",
}

_STRATEGY_CLASSES: dict[str, str] = {
    ".md": "chunking.markdown_strategy.MarkdownChunkingStrategy",
    ".pdf": "chunking.pdf_strategy.PdfWordChunkingStrategy",
    ".docx": "chunking.pdf_strategy.PdfWordChunkingStrategy",
    ".doc": "chunking.pdf_strategy.PdfWordChunkingStrategy",
    ".xlsx": "chunking.excel_strategy.ExcelChunkingStrategy",
    ".xls": "chunking.excel_strategy.ExcelChunkingStrategy",
    ".txt": "chunking.txt_strategy.ParagraphChunkingStrategy",
}

_strategy_cache: dict[str, BaseChunkingStrategy] = {}


def get_strategy(file_path: str, metadata: dict | None = None) -> BaseChunkingStrategy:
    if metadata and "content_type" in metadata:
        mapped_ext = CONTENT_TYPE_MAP.get(metadata["content_type"])
        if mapped_ext and mapped_ext in _STRATEGY_CLASSES:
            return _get_or_create(mapped_ext)

    ext = os.path.splitext(file_path)[1].lower()
    if ext in _STRATEGY_CLASSES:
        return _get_or_create(ext)

    return _get_or_create(None)


def _get_or_create(key: str | None) -> BaseChunkingStrategy:
    if key not in _strategy_cache:
        if key is None:
            from chunking.default_strategy import DefaultFallbackStrategy

            _strategy_cache[key] = DefaultFallbackStrategy()
        else:
            mod_path, cls_name = _STRATEGY_CLASSES[key].rsplit(".", 1)
            mod = importlib.import_module(mod_path)
            _strategy_cache[key] = getattr(mod, cls_name)()
    return _strategy_cache[key]
