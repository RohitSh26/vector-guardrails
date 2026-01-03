from __future__ import annotations

from collections.abc import Mapping

from .models import AnchorAlignmentSummary
from .validation import bounded_sample


def compute_anchor_sets(
    baseline: Mapping[str, list[str]],
    candidate: Mapping[str, list[str]],
) -> tuple[set[str], set[str]]:
    return set(baseline.keys()), set(candidate.keys())


def compute_anchor_jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    if not union:
        return 1.0  # both empty => perfect "match"
    return len(a & b) / len(union)


def align_anchors(
    baseline: Mapping[str, list[str]],
    candidate: Mapping[str, list[str]],
    *,
    sample_limit: int = 50,
) -> AnchorAlignmentSummary:
    """Compute alignment summary between baseline and candidate anchor sets.

    Lenient policy:
    - comparison happens on intersection elsewhere (Slice 3+)
    - this function only reports alignment statistics and samples
    """
    a, b = compute_anchor_sets(baseline, candidate)
    intersection = a & b

    baseline_only = a - b
    candidate_only = b - a

    anchor_jaccard = compute_anchor_jaccard(a, b)

    return AnchorAlignmentSummary(
        total_baseline_anchors=len(a),
        total_candidate_anchors=len(b),
        compared_anchors=len(intersection),
        anchor_jaccard=anchor_jaccard,
        baseline_only_anchor_count=len(baseline_only),
        candidate_only_anchor_count=len(candidate_only),
        baseline_only_anchor_sample=bounded_sample(baseline_only, sample_limit),
        candidate_only_anchor_sample=bounded_sample(candidate_only, sample_limit),
    )


def anchor_mismatch_warning(
    alignment: AnchorAlignmentSummary,
    *,
    jaccard_warning_threshold: float = 0.90,
) -> str | None:
    """Return a WARNING message if anchor mismatch is significant, else None."""
    if alignment.anchor_jaccard < jaccard_warning_threshold:
        return (
            "Significant anchor_id mismatch detected. "
            f"anchor_jaccard={alignment.anchor_jaccard:.3f} "
            f"(baseline_only={alignment.baseline_only_anchor_count}, "
            f"candidate_only={alignment.candidate_only_anchor_count})."
        )
    return None
