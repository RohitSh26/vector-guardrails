from vector_guardrails.models import ComparisonConfig, RiskLevel
from vector_guardrails.risk import classify_anchor_risk, classify_overall_risk


def test_anchor_risk_safe_when_above_thresholds():
    cfg = ComparisonConfig(k=5)
    risk, reasons = classify_anchor_risk(overlap=0.9, displacement=1.0, cfg=cfg)
    assert risk in (RiskLevel.SAFE, RiskLevel.INFO)
    assert reasons == []


def test_anchor_risk_warning_on_low_overlap():
    cfg = ComparisonConfig(k=5)
    risk, reasons = classify_anchor_risk(overlap=0.6, displacement=0.0, cfg=cfg)
    assert risk == RiskLevel.WARNING
    assert any("overlap" in r.lower() for r in reasons)


def test_anchor_risk_critical_on_very_low_overlap():
    cfg = ComparisonConfig(k=5)
    risk, reasons = classify_anchor_risk(overlap=0.4, displacement=0.0, cfg=cfg)
    assert risk == RiskLevel.CRITICAL
    assert any("critical" in r.lower() or "overlap" in r.lower() for r in reasons)


def test_anchor_risk_warning_on_high_displacement():
    cfg = ComparisonConfig(k=5)
    risk, reasons = classify_anchor_risk(overlap=0.9, displacement=4.0, cfg=cfg)
    assert risk == RiskLevel.WARNING
    assert any("displacement" in r.lower() for r in reasons)


def test_overall_risk_warning_on_anchor_jaccard_mismatch():
    cfg = ComparisonConfig(k=5)
    risk, reasons = classify_overall_risk(
        churn_rate=0.0,
        anchor_jaccard=0.80,
        cfg=cfg,
        any_anchor_critical=False,
    )
    assert risk == RiskLevel.WARNING
    assert any("anchor" in r.lower() and "jaccard" in r.lower() for r in reasons)


def test_overall_risk_critical_if_any_anchor_critical():
    cfg = ComparisonConfig(k=5)
    risk, reasons = classify_overall_risk(
        churn_rate=0.0,
        anchor_jaccard=1.0,
        cfg=cfg,
        any_anchor_critical=True,
    )
    assert risk == RiskLevel.CRITICAL
    assert any("critical" in r.lower() for r in reasons)
