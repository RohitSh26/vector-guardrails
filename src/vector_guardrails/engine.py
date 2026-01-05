from __future__ import annotations

from collections.abc import Mapping

from vector_guardrails.alignment import align_anchors
from vector_guardrails.metrics import overlap_at_k, rank_displacement
from vector_guardrails.models import AnchorAlignmentSummary, AnchorIdentityMetrics, ComparisonConfig
from vector_guardrails.validation import validate_and_truncate_snapshot


class IdentityMetricsSummary:
    """
    Aggregated identity-only metrics for a comparison run.

    This is an internal, pre-risk summary used in Slice 3.
    It will be folded into ComparisonReport in later slices.
    """

    __slots__ = ("overall_mean_overlap", "overall_mean_displacement", "overall_churn_rate")

    def __init__(
        self,
        overall_mean_overlap: float,
        overall_mean_displacement: float,
        overall_churn_rate: float,
    ) -> None:
        self.overall_mean_overlap = overall_mean_overlap
        self.overall_mean_displacement = overall_mean_displacement
        self.overall_churn_rate = overall_churn_rate


def compute_identity_metrics(
    baseline: Mapping[str, list[str]],
    candidate: Mapping[str, list[str]],
    config: ComparisonConfig,
) -> tuple[AnchorAlignmentSummary, list[AnchorIdentityMetrics], IdentityMetricsSummary]:
    """
    Slice 3: compute identity drift metrics (overlap + rank displacement).

    - Validates + normalizes snapshots (truncates to K, de-dupes if your validator does that)
    - Aligns anchors using lenient matching (intersection)
    - Computes per-anchor identity metrics on the intersection
    - Computes overall aggregates (mean overlap, mean displacement, churn vs overlap_warning)
    """
    k = config.k

    baseline_norm = validate_and_truncate_snapshot(baseline, k=k)
    candidate_norm = validate_and_truncate_snapshot(candidate, k=k)

    alignment = align_anchors(
        baseline=baseline_norm,
        candidate=candidate_norm,
        sample_limit=25,
    )

    # Strict behavior lives here (alignment.py is purely descriptive)
    if config.require_exact_match and set(baseline_norm) != set(candidate_norm):
        raise ValueError("Anchor ID sets do not match and require_exact_match=True")

    anchors_to_compare = sorted(set(baseline_norm) & set(candidate_norm))

    rows: list[AnchorIdentityMetrics] = []
    for anchor_id in anchors_to_compare:
        b_list = baseline_norm.get(anchor_id, [])[:k]
        c_list = candidate_norm.get(anchor_id, [])[:k]

        b_set = set(b_list)
        c_set = set(c_list)
        shared = b_set & c_set

        rows.append(
            AnchorIdentityMetrics(
                anchor_id=anchor_id,
                overlap=overlap_at_k(b_list, c_list, k=k),
                rank_displacement=rank_displacement(b_list, c_list, k=k),
                shared_count=len(shared),
                baseline_only_count=len(b_set - c_set),
                candidate_only_count=len(c_set - b_set),
            )
        )

    if rows:
        mean_overlap = sum(r.overlap for r in rows) / float(len(rows))
        disps = [r.rank_displacement for r in rows if r.rank_displacement is not None]
        mean_disp = (sum(disps) / float(len(disps))) if disps else 0.0
        churn = sum(1 for r in rows if r.overlap < config.thresholds.overlap_warning) / float(
            len(rows)
        )
    else:
        mean_overlap = 0.0
        mean_disp = 0.0
        churn = 0.0

    overall = IdentityMetricsSummary(
        overall_mean_overlap=mean_overlap,
        overall_mean_displacement=mean_disp,
        overall_churn_rate=churn,
    )

    return alignment, rows, overall
