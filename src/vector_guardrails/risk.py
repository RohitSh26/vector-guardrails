from __future__ import annotations

from vector_guardrails.models import ComparisonConfig, RiskLevel


def classify_anchor_risk(
    overlap: float, displacement: float | None, cfg: ComparisonConfig
) -> tuple[RiskLevel, list[str]]:
    t = cfg.thresholds
    reasons: list[str] = []

    # Determine severity by worst triggered rule
    level = RiskLevel.SAFE

    # Overlap rules
    if overlap < t.overlap_critical:
        level = RiskLevel.CRITICAL
        reasons.append(
            f"overlap@k below CRITICAL threshold ({overlap:.2f} < {t.overlap_critical:.2f})"
        )
    elif overlap < t.overlap_warning:
        level = RiskLevel.WARNING
        reasons.append(
            f"overlap@k below WARNING threshold ({overlap:.2f} < {t.overlap_warning:.2f})"
        )

    # Displacement rules (only if defined)
    if displacement is not None:
        if displacement > t.displacement_critical:
            level = RiskLevel.CRITICAL
            reasons.append(
                f"rank displacement above CRITICAL threshold "
                f"({displacement:.2f} > {t.displacement_critical:.2f})"
            )
        elif displacement > t.displacement_warning and level != RiskLevel.CRITICAL:
            level = RiskLevel.WARNING
            reasons.append(
                f"rank displacement above WARNING threshold "
                f"({displacement:.2f} > {t.displacement_warning:.2f})"
            )

    # If SAFE but we computed metrics, INFO is fine (you can keep SAFE too)
    if level == RiskLevel.SAFE:
        level = RiskLevel.INFO

    return level, reasons


def classify_overall_risk(
    churn_rate: float,
    anchor_jaccard: float,
    cfg: ComparisonConfig,
    any_anchor_critical: bool,
) -> tuple[RiskLevel, list[str]]:
    t = cfg.thresholds
    reasons: list[str] = []

    if any_anchor_critical:
        return RiskLevel.CRITICAL, ["at least one anchor was classified CRITICAL"]

    # Churn rules
    if churn_rate > t.churn_critical:
        reasons.append(
            f"churn rate above CRITICAL threshold ({churn_rate:.2f} > {t.churn_critical:.2f})"
        )
        return RiskLevel.CRITICAL, reasons

    if churn_rate > t.churn_warning:
        reasons.append(
            f"churn rate above WARNING threshold ({churn_rate:.2f} > {t.churn_warning:.2f})"
        )
        level = RiskLevel.WARNING
    else:
        level = RiskLevel.INFO

    # Anchor mismatch (alignment signal)
    if anchor_jaccard < t.anchor_jaccard_warning:
        reasons.append(
            f"anchor mismatch detected (jaccard={anchor_jaccard:.2f} < "
            f"{t.anchor_jaccard_warning:.2f})"
        )
        level = RiskLevel.WARNING if level != RiskLevel.CRITICAL else level

    return level, reasons
