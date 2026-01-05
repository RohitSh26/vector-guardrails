from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from vector_guardrails.metrics import overlap_at_k, rank_displacement
from vector_guardrails.models import ComparisonConfig


@dataclass(frozen=True)
class AnchorAlignmentSummary:
    total_baseline_anchors: int
    total_candidate_anchors: int
    compared_anchors: int
    anchor_jaccard: float
    baseline_only_anchors: list[str]
    candidate_only_anchors: list[str]
    warning: bool


@dataclass(frozen=True)
class AnchorMetricRow:
    anchor_id: str
    overlap: float
    rank_displacement: float | None
    shared_count: int
    baseline_only_count: int
    candidate_only_count: int


@dataclass(frozen=True)
class OverallMetrics:
    overall_mean_overlap: float
    overall_mean_displacement: float
    overall_churn_rate: float


def compute_identity_metrics(
    baseline: Mapping[str, list[str]],
    candidate: Mapping[str, list[str]],
    config: ComparisonConfig,
) -> tuple[AnchorAlignmentSummary, list[AnchorMetricRow], OverallMetrics]:
    """
    Slice 3: compute identity drift metrics (overlap + rank displacement),
    comparing only anchor intersection.
    """
    k = config.k

    baseline_anchors = set(baseline.keys())
    candidate_anchors = set(candidate.keys())
    intersection = sorted(baseline_anchors & candidate_anchors)
    union = baseline_anchors | candidate_anchors

    total_b = len(baseline_anchors)
    total_c = len(candidate_anchors)
    compared = len(intersection)

    anchor_jaccard = (compared / float(len(union))) if union else 1.0

    baseline_only = sorted(baseline_anchors - candidate_anchors)
    candidate_only = sorted(candidate_anchors - baseline_anchors)

    # Option B: lenient behavior + warning on large mismatch.
    # Threshold is configured as mismatch fraction; convert to Jaccard threshold:
    # mismatch_warning=0.10 => warn if Jaccard < 0.90
    mismatch_warn = getattr(getattr(config, "thresholds", None), "anchor_mismatch_warning", 0.10)
    jaccard_threshold = 1.0 - float(mismatch_warn)
    warning = anchor_jaccard < jaccard_threshold

    # If strict matching was enabled, fail fast on mismatch
    if getattr(config, "require_exact_match", False) and (baseline_anchors != candidate_anchors):
        raise ValueError("Anchor ID sets do not match and require_exact_match=True")

    # Compute per-anchor metrics
    rows: list[AnchorMetricRow] = []
    for anchor_id in intersection:
        b_list = (baseline.get(anchor_id) or [])[:k]
        c_list = (candidate.get(anchor_id) or [])[:k]

        # We assume Slice 2 validation ensures uniqueness etc.
        b_set = set(b_list)
        c_set = set(c_list)
        shared = b_set & c_set

        ov = overlap_at_k(b_list, c_list, k=k)
        disp = rank_displacement(b_list, c_list, k=k)

        rows.append(
            AnchorMetricRow(
                anchor_id=anchor_id,
                overlap=ov,
                rank_displacement=disp,
                shared_count=len(shared),
                baseline_only_count=len(b_set - c_set),
                candidate_only_count=len(c_set - b_set),
            )
        )

    # Overall aggregates
    if rows:
        mean_overlap = sum(r.overlap for r in rows) / float(len(rows))
        disps = [r.rank_displacement for r in rows if r.rank_displacement is not None]
        mean_disp = (sum(disps) / float(len(disps))) if disps else 0.0
    else:
        mean_overlap = 0.0
        mean_disp = 0.0

    # Churn uses overlap threshold for WARNING for now (Slice 4 will do full risk)
    overlap_warn = getattr(getattr(config, "thresholds", None), "overlap_warning", 0.70)
    churn = (sum(1 for r in rows if r.overlap < overlap_warn) / float(len(rows))) if rows else 0.0

    alignment = AnchorAlignmentSummary(
        total_baseline_anchors=total_b,
        total_candidate_anchors=total_c,
        compared_anchors=compared,
        anchor_jaccard=anchor_jaccard,
        baseline_only_anchors=baseline_only,
        candidate_only_anchors=candidate_only,
        warning=warning,
    )

    overall = OverallMetrics(
        overall_mean_overlap=mean_overlap,
        overall_mean_displacement=mean_disp,
        overall_churn_rate=churn,
    )

    return alignment, rows, overall
