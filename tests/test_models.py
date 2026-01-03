import json

import pytest
from pydantic import ValidationError

from vector_guardrails import (
    AnchorAlignmentSummary,
    AnchorMetrics,
    ComparisonConfig,
    ComparisonReport,
    RiskLevel,
    ThresholdPreset,
)


def test_threshold_defaults():
    t = ThresholdPreset()
    assert t.overlap_warning == 0.70
    assert t.overlap_critical == 0.50
    assert t.displacement_warning == 3.0
    assert t.displacement_critical == 5.0
    assert t.churn_warning == 0.20
    assert t.churn_critical == 0.35
    assert t.anchor_jaccard_warning == 0.90


def test_models_are_frozen():
    cfg = ComparisonConfig()
    with pytest.raises(ValidationError):
        cfg.k = 20


def test_exit_code_mapping():
    cfg = ComparisonConfig()
    alignment = AnchorAlignmentSummary(
        total_baseline_anchors=5,
        total_candidate_anchors=5,
        compared_anchors=5,
        anchor_jaccard=1.0,
        baseline_only_anchor_count=0,
        candidate_only_anchor_count=0,
        baseline_only_anchor_sample=[],
        candidate_only_anchor_sample=[],
    )

    m = AnchorMetrics(
        anchor_id="a1",
        overlap=1.0,
        rank_displacement=0.0,
        shared_count=5,
        baseline_only_count=0,
        candidate_only_count=0,
        risk_level=RiskLevel.SAFE,
        reasons=[],
    )

    report = ComparisonReport(
        config=cfg,
        alignment=alignment,
        overall_mean_overlap=1.0,
        overall_mean_displacement=0.0,
        overall_churn_rate=0.0,
        overall_risk_level=RiskLevel.SAFE,
        anchor_metrics=[m],
        verdict_summary="SAFE",
    )

    assert report.to_exit_code() == 0


def test_report_json_serializable():
    cfg = ComparisonConfig()
    alignment = AnchorAlignmentSummary(
        total_baseline_anchors=2,
        total_candidate_anchors=3,
        compared_anchors=2,
        anchor_jaccard=2 / 3,
        baseline_only_anchor_count=0,
        candidate_only_anchor_count=1,
        baseline_only_anchor_sample=[],
        candidate_only_anchor_sample=["x"],
    )

    report = ComparisonReport(
        config=cfg,
        alignment=alignment,
        overall_mean_overlap=0.75,
        overall_mean_displacement=1.0,
        overall_churn_rate=0.1,
        overall_risk_level=RiskLevel.INFO,
        anchor_metrics=[],
        verdict_summary="INFO",
    )

    json.dumps(report.model_dump())
