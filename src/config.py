from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_env_file(path: Path = ROOT / ".env") -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()


@dataclass(frozen=True)
class Settings:
    index_path: Path = Path(os.getenv("RAG_INDEX_PATH", ROOT / "indexes" / "vector_index.json"))
    top_k: int = int(os.getenv("RAG_TOP_K", "4"))
    min_score: float = float(os.getenv("RAG_MIN_SCORE", "0.10"))
    cloud_llm_provider: str = os.getenv("CLOUD_LLM_PROVIDER", "openai").lower()
    cloud_llm_api_url: str = os.getenv("CLOUD_LLM_API_URL", "")
    cloud_llm_api_key: str = os.getenv("CLOUD_LLM_API_KEY", "")
    cloud_llm_model: str = os.getenv("CLOUD_LLM_MODEL", "gpt-4o-mini")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")


settings = Settings()
