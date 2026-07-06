from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.embeddings import get_embedder

KB_DIR = ROOT / "knowledge_base"
INDEX_PATH = ROOT / "indexes" / "vector_index.json"


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
        current = paragraph

    if current:
        chunks.append(current)

    expanded: list[str] = []
    for chunk in chunks:
        if len(chunk) <= chunk_size:
            expanded.append(chunk)
            continue

        start = 0
        while start < len(chunk):
            end = start + chunk_size
            expanded.append(chunk[start:end].strip())
            start = max(end - overlap, start + 1)

    return [chunk for chunk in expanded if chunk]


def load_documents(kb_dir: Path) -> list[dict]:
    documents: list[dict] = []
    for path in sorted(kb_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = path.stem.replace("_", " ").title()
        if text.startswith("# "):
            title = text.splitlines()[0].replace("#", "").strip()

        for chunk_id, chunk in enumerate(chunk_text(text), start=1):
            documents.append(
                {
                    "id": f"{path.stem}:{chunk_id}",
                    "source": str(path.relative_to(ROOT)),
                    "title": title,
                    "chunk_id": chunk_id,
                    "text": chunk,
                }
            )
    return documents


def build_index(kb_dir: Path = KB_DIR, index_path: Path = INDEX_PATH, use_ml: bool = True) -> dict:
    start = time.perf_counter()
    documents = load_documents(kb_dir)
    embedder = get_embedder(prefer_sentence_transformers=use_ml)
    vectors = embedder.encode([document["text"] for document in documents])

    payload = {
        "embedding_model": getattr(embedder, "model_name", "unknown"),
        "dimension": len(vectors[0]) if vectors else 0,
        "created_at_unix": int(time.time()),
        "build_seconds": round(time.perf_counter() - start, 3),
        "chunk_count": len(documents),
        "documents": [
            {
                **document,
                "vector": vector,
            }
            for document, vector in zip(documents, vectors)
        ],
    }

    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Build local vector index for RAG bot.")
    parser.add_argument("--no-ml", action="store_true", help="Use deterministic hashing embeddings.")
    parser.add_argument("--kb-dir", type=Path, default=KB_DIR)
    parser.add_argument("--index-path", type=Path, default=INDEX_PATH)
    args = parser.parse_args()

    index = build_index(args.kb_dir, args.index_path, use_ml=not args.no_ml)
    print(
        f"Built index: {index['chunk_count']} chunks, "
        f"model={index['embedding_model']}, dimension={index['dimension']}, "
        f"time={index['build_seconds']}s"
    )


if __name__ == "__main__":
    main()
