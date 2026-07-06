from __future__ import annotations

import re


DANGEROUS_PATTERNS = [
    re.compile(r"ignore\s+all\s+instructions", re.IGNORECASE),
    re.compile(r"игнорируй.*инструкц|выведи.*системн", re.IGNORECASE),
    re.compile(r"output\s*:", re.IGNORECASE),
    re.compile(r"суперпароль|root\s*:|swordfish", re.IGNORECASE),
    re.compile(r"парол|password|secret|секрет", re.IGNORECASE),
    re.compile(r"system\s+prompt|системн.*промпт", re.IGNORECASE),
]


def is_prompt_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in DANGEROUS_PATTERNS)


def sanitize_context(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if is_prompt_injection(line):
            continue
        lines.append(line)
    return "\n".join(lines).strip()
