from __future__ import annotations


def overlap_at_k(baseline_neighbors: list[str], candidate_neighbors: list[str], k: int) -> float:
    """
    Overlap@K = |intersection(topK_baseline, topK_candidate)| / K

    Note: denominator is always K (not len(list)), by design.
    """
    if k <= 0:
        raise ValueError("k must be >= 1")

    b = set(baseline_neighbors[:k])
    c = set(candidate_neighbors[:k])
    return len(b & c) / float(k)


def rank_displacement(
    baseline_neighbors: list[str], candidate_neighbors: list[str], k: int
) -> float | None:
    """
    Mean absolute rank displacement for shared items in top-K.
    Returns None if there is no overlap.
    """
    if k <= 0:
        raise ValueError("k must be >= 1")

    b_top = baseline_neighbors[:k]
    c_top = candidate_neighbors[:k]

    b_rank = {item: i for i, item in enumerate(b_top)}
    c_rank = {item: i for i, item in enumerate(c_top)}

    shared = set(b_rank.keys()) & set(c_rank.keys())
    if not shared:
        return None

    total = 0.0
    for item in shared:
        total += abs(b_rank[item] - c_rank[item])

    return total / float(len(shared))
