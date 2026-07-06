from __future__ import annotations

from dataclasses import asdict, dataclass

from src.config import settings
from src.llm import CloudLLMClient
from src.retriever import SearchResult, VectorRetriever
from src.security import is_out_of_scope, is_prompt_injection, sanitize_context


@dataclass
class Source:
    title: str
    source: str
    chunk_id: int
    score: float


@dataclass
class RAGAnswer:
    question: str
    answer: str
    sources: list[Source]
    provider: str
    found_chunks: bool


class RAGService:
    def __init__(self) -> None:
        self.retriever = VectorRetriever(settings.index_path)
        self.llm = CloudLLMClient()

    def answer(self, question: str) -> RAGAnswer:
        if is_prompt_injection(question) or is_out_of_scope(question):
            llm_result = self.llm.generate(question, "")
            return RAGAnswer(
                question=question,
                answer=llm_result.answer,
                sources=[],
                provider=llm_result.provider,
                found_chunks=False,
            )

        results = self.retriever.search(question, top_k=settings.top_k)
        relevant = [result for result in results if result.score >= settings.min_score]
        safe_results = [result for result in relevant if not is_prompt_injection(result.text)]

        context = self._build_context(safe_results)
        if not safe_results:
            context = ""

        llm_result = self.llm.generate(question, context)
        return RAGAnswer(
            question=question,
            answer=llm_result.answer,
            sources=[
                Source(result.title, result.source, result.chunk_id, result.score)
                for result in safe_results
            ],
            provider=llm_result.provider,
            found_chunks=bool(safe_results),
        )

    def _build_context(self, results: list[SearchResult]) -> str:
        chunks = []
        for result in results:
            clean_text = sanitize_context(result.text)
            if not clean_text:
                continue
            chunks.append(
                f"Источник: {result.source}, чанк {result.chunk_id}, score={result.score}\n{clean_text}"
            )
        return "\n\n---\n\n".join(chunks)


def answer_as_dict(answer: RAGAnswer) -> dict:
    payload = asdict(answer)
    payload["sources"] = [asdict(source) for source in answer.sources]
    return payload
