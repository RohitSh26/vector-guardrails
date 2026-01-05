from __future__ import annotations


def overlap_at_k(baseline_neighbors: list[str], candidate_neighbors: list[str], k: int) -> float:
    raise NotImplementedError


def rank_displacement(
    baseline_neighbors: list[str], candidate_neighbors: list[str], k: int
) -> float | None:
    raise NotImplementedError
