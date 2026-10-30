from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def ensure_artifact_parent(path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def write_json_artifact(payload: Mapping[str, Any], path: str | Path) -> Path:
    output = ensure_artifact_parent(path)
    output.write_text(json.dumps(dict(payload), indent=2, sort_keys=True), encoding="utf-8")
    return output


def read_json_artifact(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Missing architecture artifact: {source}")
    return json.loads(source.read_text(encoding="utf-8"))


def write_text_artifact(text: str, path: str | Path) -> Path:
    output = ensure_artifact_parent(path)
    output.write_text(text, encoding="utf-8")
    return output
