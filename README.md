# QuantumForge RAG Bot

Учебный RAG-бот для проектной работы: подготовка базы знаний, построение локального векторного индекса, REST API, защита от prompt injection, автоматическое обновление индекса и оценка качества.

## Стек

- Python 3.11+
- FastAPI
- FAISS / JSON fallback для локального индекса
- Sentence-Transformers / deterministic hashing fallback для эмбеддингов
- Облачная LLM через OpenAI-compatible API

## Быстрый запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 scripts/generate_knowledge_base.py
python3 scripts/build_index.py --no-ml
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Проверка API:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Кто отвечает за протокол HelioBridge?"}'
```

## Демонстрация

```bash
python3 scripts/run_demo.py
```

Сценарии демонстрации описаны в `demo/demo_queries.md`: 5 успешных ответов и 5 безопасных отказов.

## Оценка качества

```bash
python3 scripts/evaluate.py
```

Golden set находится в `data/golden_questions.jsonl`, отчёт последнего прогона — в `demo/evaluation_report.json`.

## Автообновление индекса

```bash
python3 scripts/update_index.py
```

Пример cron-задачи находится в `demo/cron_example.txt`, диаграмма процесса — в `diagrams/update_flow.puml`.

## Docker

```bash
docker compose up --build
```

После запуска API будет доступен на `http://127.0.0.1:8000`.

## Сдача

Работа выполняется в ветке `rag`. Для сдачи нужно создать pull request из `rag` в `main` в собственном публичном репозитории GitHub.
