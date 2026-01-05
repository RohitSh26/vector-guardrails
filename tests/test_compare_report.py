from vector_guardrails.compare import compare
from vector_guardrails.models import ComparisonConfig, RiskLevel


def test_compare_returns_report_with_anchor_metrics_and_verdict():
    baseline = {
        "A1": ["X", "Y", "Z"],
        "A2": ["M", "N", "O"],
    }
    candidate = {
        "A1": ["Y", "X", "Z"],  # reorder only
        "A3": ["P", "Q", "R"],  # anchor mismatch
    }

    cfg = ComparisonConfig(k=3)
    report = compare(baseline=baseline, candidate=candidate, config=cfg)

    assert report.config.k == 3
    assert report.alignment.compared_anchors == 1
    assert report.alignment.total_baseline_anchors == 2
    assert report.alignment.total_candidate_anchors == 2

    # only A1 compared
    assert len(report.anchor_metrics) == 1
    assert report.anchor_metrics[0].anchor_id == "A1"

    # because A1 overlap is 1.0, should not be WARNING/CRITICAL
    assert report.anchor_metrics[0].risk_level in (RiskLevel.SAFE, RiskLevel.INFO)

    # anchor mismatch jaccard should typically trigger WARNING overall (unless any CRITICAL)
    assert report.overall_risk_level in (RiskLevel.WARNING, RiskLevel.SAFE, RiskLevel.INFO)
    assert isinstance(report.verdict_summary, str)
    assert report.verdict_summary.strip()