from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.query_logger import log_query
from src.rag_service import RAGService


GOLDEN_PATH = ROOT / "data" / "golden_questions.jsonl"
REPORT_PATH = ROOT / "demo" / "evaluation_report.json"
LOG_PATH = ROOT / "logs" / "evaluation.jsonl"


def load_golden_questions() -> list[dict]:
    questions = []
    for line in GOLDEN_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            questions.append(json.loads(line))
    return questions


def evaluate_answer(case: dict, answer) -> dict:
    expected_found = bool(case["expected_found"])
    actual_found = bool(answer.found_chunks)
    expected_source = case.get("expected_source")
    sources = [source.source for source in answer.sources]
    source_ok = expected_source is None or expected_source in sources
    passed = actual_found == expected_found and (not expected_found or source_ok)
    status = "passed" if passed else "failed"
    log_query(answer, status=status, log_path=LOG_PATH)
    return {
        "question": case["question"],
        "topic": case["topic"],
        "expected_found": expected_found,
        "actual_found": actual_found,
        "expected_source": expected_source,
        "sources": sources,
        "answer_length": len(answer.answer),
        "status": status,
    }


def main() -> None:
    service = RAGService()
    cases = load_golden_questions()
    results = [evaluate_answer(case, service.answer(case["question"])) for case in cases]
    passed = sum(result["status"] == "passed" for result in results)
    report = {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "coverage_percent": round(passed / len(results) * 100, 2) if results else 0,
        "known_gaps": [
            "В базе нет HR-данных и зарплат.",
            "В базе нет произвольных событий вроде чемпионатов.",
            "Запросы секретов и prompt injection намеренно фильтруются.",
        ],
        "recommendations": [
            "Расширить базу по частым HR- и support-вопросам, если такие темы нужны пользователям.",
            "Добавить ручную разметку ожидаемых источников для регрессионных тестов.",
            "В production-версии использовать отдельную аналитику нерелевантных источников и ручную проверку низких score.",
        ],
        "results": results,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
