import json
import re

from services.errors import LLMOutputError


def parse_llm_json(text: str, stage_name: str) -> dict:
    candidates = _build_candidates(text)

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, dict):
            return parsed

    raise LLMOutputError(
        f"Analysis failed during {stage_name} because the model returned invalid JSON. Please retry."
    )


def _build_candidates(text: str) -> list[str]:
    normalized = text.strip()
    candidates: list[str] = []

    if normalized:
        candidates.append(normalized)

    fenced_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", normalized)
    if fenced_match:
        candidates.append(fenced_match.group(1).strip())

    object_match = re.search(r"\{[\s\S]*\}", normalized)
    if object_match:
        candidates.append(object_match.group(0).strip())

    unique_candidates: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            unique_candidates.append(candidate)

    return unique_candidates
