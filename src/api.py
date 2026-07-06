from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.rag_service import RAGService, answer_as_dict


app = FastAPI(title="QuantumForge RAG Bot", version="0.1.0")
service = RAGService()


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["Кто отвечает за протокол HelioBridge?"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask")
def ask(request: AskRequest) -> dict:
    return answer_as_dict(service.answer(request.question))
