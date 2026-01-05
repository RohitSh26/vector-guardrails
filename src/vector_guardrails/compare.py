from __future__ import annotations

from collections.abc import Mapping

from vector_guardrails.engine import compute_identity_metrics
from vector_guardrails.models import AnchorMetrics, ComparisonConfig, ComparisonReport, RiskLevel
from vector_guardrails.risk import classify_anchor_risk, classify_overall_risk


def compare(
    baseline: Mapping[str, list[str]],
    candidate: Mapping[str, list[str]],
    config: ComparisonConfig | None = None,
) -> ComparisonReport:
    cfg = config or ComparisonConfig()

    alignment, anchor_rows, overall = compute_identity_metrics(
        baseline=baseline,
        candidate=candidate,
        config=cfg,
    )

    anchor_metrics: list[AnchorMetrics] = []
    any_anchor_critical = False

    for row in anchor_rows:
        risk, reasons = classify_anchor_risk(
            overlap=row.overlap,
            displacement=row.rank_displacement,
            cfg=cfg,
        )
        if risk == RiskLevel.CRITICAL:
            any_anchor_critical = True

        anchor_metrics.append(
            AnchorMetrics(
                anchor_id=row.anchor_id,
                overlap=row.overlap,
                rank_displacement=row.rank_displacement,
                shared_count=row.shared_count,
                baseline_only_count=row.baseline_only_count,
                candidate_only_count=row.candidate_only_count,
                risk_level=risk,
                reasons=reasons,
            )
        )

    overall_risk, overall_reasons = classify_overall_risk(
        churn_rate=overall.overall_churn_rate,
        anchor_jaccard=alignment.anchor_jaccard,
        cfg=cfg,
        any_anchor_critical=any_anchor_critical,
    )

    # A short, human-readable summary (we'll polish more in Slice 5)
    verdict_summary = (
        f"VERDICT: {overall_risk.value} — "
        f"Compared anchors: {alignment.compared_anchors}, "
        f"Mean overlap@{cfg.k}: {overall.overall_mean_overlap:.2f}, "
        f"Churn rate: {overall.overall_churn_rate:.2f}"
    )
    if overall_reasons:
        verdict_summary += " | REASONS: " + "; ".join(overall_reasons)

    report = ComparisonReport(
        config=cfg,
        alignment=alignment,
        overall_mean_overlap=overall.overall_mean_overlap,
        overall_mean_displacement=overall.overall_mean_displacement,
        overall_churn_rate=overall.overall_churn_rate,
        overall_risk_level=overall_risk,
        anchor_metrics=anchor_metrics,
        segment_summaries=None,
        verdict_summary=verdict_summary,
    )
    return report
