from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_index import INDEX_PATH, KB_DIR, build_index


DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
MANIFEST_PATH = DATA_DIR / "index_manifest.json"
LOG_PATH = LOG_DIR / "update_index.jsonl"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_manifest() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)): file_hash(path)
        for path in sorted(KB_DIR.glob("*.md"))
    }


def load_previous_manifest() -> dict[str, str]:
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def diff_manifest(previous: dict[str, str], current: dict[str, str]) -> dict[str, list[str]]:
    previous_keys = set(previous)
    current_keys = set(current)
    added = sorted(current_keys - previous_keys)
    removed = sorted(previous_keys - current_keys)
    changed = sorted(
        key for key in current_keys & previous_keys if previous[key] != current[key]
    )
    return {"added": added, "changed": changed, "removed": removed}


def append_log(record: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    started_at = datetime.now(timezone.utc).isoformat()
    previous = load_previous_manifest()
    current = current_manifest()
    changes = diff_manifest(previous, current)
    changed_count = sum(len(value) for value in changes.values())

    try:
        index = build_index(KB_DIR, INDEX_PATH, use_ml=False)
        status = "updated"
        error = None
    except Exception as exc:
        index = {"chunk_count": 0}
        status = "failed"
        error = str(exc)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")

    record = {
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "changed_files_count": changed_count,
        "changes": changes,
        "chunk_count": index["chunk_count"],
        "index_path": str(INDEX_PATH.relative_to(ROOT)),
        "error": error,
    }
    append_log(record)
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
