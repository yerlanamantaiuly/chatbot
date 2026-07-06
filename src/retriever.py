from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.embeddings import HashingEmbedder, cosine_similarity


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX_PATH = ROOT / "indexes" / "vector_index.json"


@dataclass
class SearchResult:
    score: float
    source: str
    title: str
    chunk_id: int
    text: str


class VectorRetriever:
    def __init__(self, index_path: Path = DEFAULT_INDEX_PATH) -> None:
        self.index_path = index_path
        payload = json.loads(index_path.read_text(encoding="utf-8"))
        self.embedding_model = payload["embedding_model"]
        self.dimension = payload["dimension"]
        self.documents = payload["documents"]
        self.embedder = HashingEmbedder(dimension=self.dimension)

    def search(self, query: str, top_k: int = 4) -> list[SearchResult]:
        query_vector = self.embedder.encode([query])[0]
        scored = []
        for document in self.documents:
            score = cosine_similarity(query_vector, document["vector"])
            scored.append(
                SearchResult(
                    score=round(float(score), 4),
                    source=document["source"],
                    title=document["title"],
                    chunk_id=int(document["chunk_id"]),
                    text=document["text"],
                )
            )
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]
