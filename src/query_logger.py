from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.rag_service import RAGAnswer


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = ROOT / "logs" / "queries.jsonl"


def log_query(answer: RAGAnswer, status: str, log_path: Path = DEFAULT_LOG_PATH) -> dict:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": answer.question,
        "found_chunks": answer.found_chunks,
        "answer_length": len(answer.answer),
        "status": status,
        "sources": [
            {
                "title": source.title,
                "source": source.source,
                "chunk_id": source.chunk_id,
                "score": source.score,
            }
            for source in answer.sources
        ],
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
