from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def load_json(path: str) -> Any:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"file not found: {path}")
    if not p.is_file():
        raise IsADirectoryError(f"not a file: {path}")

    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: str, obj: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def ensure_snapshot_shape(obj: Any) -> Mapping[str, list[str]]:
    """
    Snapshot must be: Mapping[str, list[str]]
    We validate lightly here; deeper validation happens in validation.py.
    """
    if not isinstance(obj, dict):
        raise ValueError("snapshot JSON must be an object: {anchor_id: [neighbors...]}")
    for k, v in obj.items():
        if not isinstance(k, str):
            raise ValueError("snapshot keys must be strings (anchor_id)")
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            raise ValueError(f"snapshot values must be list[str] for anchor_id={k!r}")
    return obj
