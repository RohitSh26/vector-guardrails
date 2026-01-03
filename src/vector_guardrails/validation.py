from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def _is_sequence_of_str(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def validate_and_truncate_snapshot(
    snapshot: Mapping[str, list[str]],
    k: int,
) -> dict[str, list[str]]:
    """Validate a retrieval snapshot and truncate neighbor lists to top-k.

    Rules (v0.1):
    - snapshot must be Mapping[str, list[str]]
    - k must be >= 1
    - anchor_id keys must be non-empty strings
    - neighbors must be a list[str]
    - neighbors are truncated to k
    - duplicates within the truncated top-k neighbors are not allowed (ValueError)
    """
    if not isinstance(k, int) or k < 1:
        raise ValueError(f"k must be an int >= 1, got: {k!r}")

    if not isinstance(snapshot, Mapping):
        raise ValueError("snapshot must be a mapping of anchor_id -> list[str]")

    out: dict[str, list[str]] = {}
    for anchor_id, neighbors in snapshot.items():
        if not isinstance(anchor_id, str) or not anchor_id.strip():
            raise ValueError(f"anchor_id must be a non-empty string, got: {anchor_id!r}")

        if not _is_sequence_of_str(neighbors):
            raise ValueError(
                f"neighbors for anchor_id={anchor_id!r} must be a list[str], "
                f"got: {type(neighbors).__name__}"
            )

        topk = neighbors[:k]

        # Disallow duplicates in top-k (prevents misleading metrics later)
        if len(set(topk)) != len(topk):
            raise ValueError(f"duplicate neighbor IDs found in top-{k} for anchor_id={anchor_id!r}")

        out[anchor_id] = topk

    return out


def bounded_sample(values: Iterable[str], limit: int) -> list[str]:
    """Return a deterministic bounded sample (sorted, then truncated)."""
    if limit < 0:
        raise ValueError("limit must be >= 0")
    return sorted(values)[:limit]
