from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from enum import Enum, IntEnum

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RiskLevel(str, Enum):
    SAFE = "SAFE"
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class ExitCode(IntEnum):
    OK = 0          # SAFE / INFO
    WARNING = 1
    CRITICAL = 2
    ERROR = 3       # CLI-only (invalid input / IO failures)


# ---------------------------------------------------------------------------
# Typing aliases (documentation-level)
# ---------------------------------------------------------------------------

RetrievalSnapshot = Mapping[str, list[str]]
SegmentMapping = Mapping[str, Mapping[str, str]]


# ---------------------------------------------------------------------------
# Configuration models
# ---------------------------------------------------------------------------

class ThresholdPreset(BaseModel):
    """Conservative threshold presets for risk classification."""

    model_config = ConfigDict(frozen=True)

    overlap_warning: float = Field(0.70, ge=0.0, le=1.0)
    overlap_critical: float = Field(0.50, ge=0.0, le=1.0)

    displacement_warning: float = Field(3.0, ge=0.0)
    displacement_critical: float = Field(5.0, ge=0.0)

    churn_warning: float = Field(0.20, ge=0.0, le=1.0)
    churn_critical: float = Field(0.35, ge=0.0, le=1.0)

    anchor_jaccard_warning: float = Field(0.90, ge=0.0, le=1.0)


class ComparisonConfig(BaseModel):
    """Configuration for comparison behavior."""

    model_config = ConfigDict(frozen=True)

    k: int = Field(10, ge=1)
    thresholds: ThresholdPreset = Field(default_factory=ThresholdPreset)

    require_exact_match: bool = False
    min_anchors: int = Field(10, ge=1)

    segment_keys: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Report models
# ---------------------------------------------------------------------------

class AnchorMetrics(BaseModel):
    """Per-anchor metrics and risk classification."""

    model_config = ConfigDict(frozen=True)

    anchor_id: str

    overlap: float = Field(ge=0.0, le=1.0)
    rank_displacement: float | None = Field(default=None, ge=0.0)

    shared_count: int = Field(ge=0)
    baseline_only_count: int = Field(ge=0)
    candidate_only_count: int = Field(ge=0)

    risk_level: RiskLevel
    reasons: list[str] = Field(default_factory=list)


class SegmentSummary(BaseModel):
    """Aggregated metrics for a segment."""

    model_config = ConfigDict(frozen=True)

    segment_key: str
    anchor_count: int = Field(ge=1)

    mean_overlap: float = Field(ge=0.0, le=1.0)
    mean_displacement: float = Field(ge=0.0)
    churn_rate: float = Field(ge=0.0, le=1.0)

    risk_level: RiskLevel


class AnchorAlignmentSummary(BaseModel):
    """Summary of baseline vs candidate anchor alignment."""

    model_config = ConfigDict(frozen=True)

    total_baseline_anchors: int = Field(ge=0)
    total_candidate_anchors: int = Field(ge=0)
    compared_anchors: int = Field(ge=0)

    anchor_jaccard: float = Field(ge=0.0, le=1.0)

    baseline_only_anchor_count: int = Field(ge=0)
    candidate_only_anchor_count: int = Field(ge=0)

    baseline_only_anchor_sample: list[str] = Field(default_factory=list)
    candidate_only_anchor_sample: list[str] = Field(default_factory=list)


class ComparisonReport(BaseModel):
    """Full comparison report."""

    model_config = ConfigDict(frozen=True)

    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    config: ComparisonConfig
    alignment: AnchorAlignmentSummary

    overall_mean_overlap: float = Field(ge=0.0, le=1.0)
    overall_mean_displacement: float = Field(ge=0.0)
    overall_churn_rate: float = Field(ge=0.0, le=1.0)

    overall_risk_level: RiskLevel

    anchor_metrics: list[AnchorMetrics] = Field(default_factory=list)
    segment_summaries: list[SegmentSummary] | None = None

    verdict_summary: str

    def get_critical_anchors(self) -> list[AnchorMetrics]:
        return [m for m in self.anchor_metrics if m.risk_level == RiskLevel.CRITICAL]

    def get_warning_anchors(self) -> list[AnchorMetrics]:
        return [m for m in self.anchor_metrics if m.risk_level == RiskLevel.WARNING]

    def to_exit_code(self) -> int:
        if self.overall_risk_level in (RiskLevel.SAFE, RiskLevel.INFO):
            return int(ExitCode.OK)
        if self.overall_risk_level == RiskLevel.WARNING:
            return int(ExitCode.WARNING)
        return int(ExitCode.CRITICAL)
