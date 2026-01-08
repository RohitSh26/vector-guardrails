# Changelog

All notable changes to Vector Guardrails will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-01-08

### Overview

**First stable release.** Vector Guardrails v0.1 provides offline drift detection for embedding-based retrieval systems through snapshot comparison.

**What this release does:**
- Compares retrieval snapshots (anchor → neighbors mappings) to detect semantic drift
- Produces conservative risk signals (SAFE, INFO, WARNING, CRITICAL)
- Provides CLI and Python API for pre-deployment checks and CI/CD integration
- Works with any vector store or retrieval engine (architecture-agnostic)

**What this release does NOT do:**
- Real-time monitoring or production observability
- Quality measurement (only stability measurement)
- Automatic rollback or deployment decisions
- Embedding training or serving

**Stability guarantees:**
- Core comparison logic is stable
- CLI interface and exit codes are stable
- Python API surface (`compare()`, `ComparisonConfig`, `ComparisonReport`) is stable
- Snapshot JSON format is stable
- Breaking changes will increment minor version (0.x.0)

**Known limitations:**
- Non-deterministic retrieval systems produce noisy results
- Personalization and context-dependent ranking not fully supported
- Overlap measures stability, not quality (false negatives possible)
- Default thresholds require calibration for most domains
- No statistical significance testing (point estimates only)
- See [docs/when-to-use.md](./docs/when-to-use.md#known-limitations--failure-modes) for full details

---

### Added

#### Core Functionality

- **Snapshot comparison engine**
  - Compares baseline vs candidate retrieval snapshots
  - Computes per-anchor metrics: overlap@K, rank displacement, shared/only counts
  - Computes aggregate metrics: mean overlap, mean displacement, churn rate
  - Anchor alignment with Jaccard similarity measurement
  - Conservative risk classification (SAFE → INFO → WARNING → CRITICAL)

- **CLI tool** (`vector-guardrails compare`)
  - Text output format with metric explanations and contextual interpretations
  - JSON output format for programmatic consumption
  - Full report export to file (`--output report.json`)
  - Exit codes for CI/CD gating (0=OK, 1=WARNING, 2=CRITICAL, 3=ERROR)
  - Configurable parameters: `--k`, `--strict`, `--min-anchors`, `--format`

- **Python API**
  - `compare(baseline, candidate, config)` — core comparison function
  - `ComparisonConfig` — configuration with threshold customization
  - `ComparisonReport` — structured report with full metrics and risk levels
  - `ThresholdPreset` — configurable risk thresholds
  - `RiskLevel` enum (SAFE, INFO, WARNING, CRITICAL)

#### Metrics

- **Overlap@K** — Fraction of neighbors in common between baseline and candidate
  - Primary stability metric
  - Configurable WARNING/CRITICAL thresholds (default: 0.70/0.50)

- **Rank Displacement** — Mean position change for shared neighbors
  - Measures ranking instability
  - Configurable WARNING/CRITICAL thresholds (default: 3.0/5.0 positions)

- **Churn Rate** — Fraction of anchors with low overlap
  - Aggregate drift indicator
  - Configurable WARNING/CRITICAL thresholds (default: 0.20/0.35)

- **Anchor Jaccard** — Similarity of anchor ID sets between snapshots
  - Detects anchor set mismatches
  - Configurable WARNING threshold (default: 0.90)

#### Documentation

- **Comprehensive guides** (2,000+ lines total)
  - [docs/when-to-use.md](./docs/when-to-use.md) — 7 scenarios, 5 anti-patterns, 8 failure modes
  - [docs/generating-snapshots.md](./docs/generating-snapshots.md) — Code examples for search, recommendations, RAG
  - [docs/anchor-terminology.md](./docs/anchor-terminology.md) — Use case mapping and terminology clarification
  - [docs/thresholds-and-tuning.md](./docs/thresholds-and-tuning.md) — Threshold philosophy and calibration guide
  - [docs/README.md](./docs/README.md) — Documentation index with reading order

- **Honest limitation disclosure**
  - Known failure modes documented with symptoms and mitigations
  - Transparent about threshold origins (engineering judgment, not science)
  - Clear guidance on when NOT to use the tool

- **Integration examples**
  - FAISS, Pinecone, Elasticsearch snapshot generation pseudocode
  - CI/CD pipeline integration examples
  - Threshold tuning workflow

#### Examples

- **Runnable examples** demonstrating all risk levels
  - `01_basic_comparison/` — Identical snapshots (exit code 0)
  - `02_anchor_mismatch/` — Low anchor Jaccard (exit code 1)
  - `03_high_churn/` — High neighbor drift (exit code 2)
  - `api_usage.py` — Python API demonstration with decision logic

- **Example READMEs** explaining scenarios and expected outcomes

#### CLI Report Format

- Human-readable text format with:
  - Metric explanations (plain-language descriptions)
  - Contextual interpretations (✓/⚠/✗ indicators based on values)
  - Percentage equivalents alongside decimals
  - Threshold values shown in risk breakdown
  - Actionable recommendations based on risk level

---

### Design Decisions

#### Conservative by Default

- Strict thresholds to err on side of caution
- False alarms preferred over missed regressions
- Manual review expected for WARNING/CRITICAL signals

#### Architecture-Agnostic

- No dependencies on specific vector stores
- Simple JSON snapshot format (anchor_id → [neighbor_ids])
- Works with any retrieval system that produces ranked results

#### Offline-Only

- Not designed for real-time monitoring
- Snapshot-based comparison for pre-deployment checks
- Complements (doesn't replace) production observability

#### Explainable Outputs

- Human-readable text reports
- Per-anchor metrics available for debugging
- Clear reasoning in verdict summaries

#### Tunable Risk Thresholds

- All thresholds configurable via `ThresholdPreset`
- Calibration guide provided
- Defaults are starting points, not gospel

---

### Non-Goals (Explicit Scope Boundaries)

The following are intentionally out of scope for v0.1:

- ❌ Real-time drift monitoring or production telemetry
- ❌ Quality measurement (NDCG, MRR, precision/recall)
- ❌ Automatic deployment decisions or rollback
- ❌ Embedding model training or optimization
- ❌ Vector index serving or storage
- ❌ Statistical significance testing or confidence intervals
- ❌ Multi-dimensional drift analysis (beyond identity metrics)
- ❌ UI dashboards or visualization
- ❌ Integration with specific MLOps platforms

These may be considered for future releases based on user feedback.

---

### Dependencies

**Runtime:**
- `numpy>=1.26`
- `pydantic>=2.6`

**Development:**
- `pytest>=9.0.2`
- `pytest-cov>=7.0.0`
- `ruff>=0.14.10`

**Optional:**
- `rich>=13.7` (for enhanced CLI output, not required)

---

### Compatibility

**Python:** Requires Python 3.10 or higher

**Snapshot format:** JSON files, cross-platform compatible

**CLI:** Works on Linux, macOS, Windows (any platform with Python 3.10+)

---

### Breaking Changes

None (initial release).

**Future breaking change policy:**
- Breaking changes to CLI, API, or snapshot format will increment minor version (0.x.0)
- Deprecation warnings will precede breaking changes where possible
- Changelog will clearly mark breaking changes

---

### Migration Guide

Not applicable (initial release).

---

### Contributors

- Rohit Sharma (@RohitSh26) — Core implementation and design

**Acknowledgments:**
- Design influenced by operational experience with embedding model drift in production systems
- Documentation philosophy: transparency and honesty over marketing

---

### Known Issues

1. **Non-deterministic systems produce noise** — Systems with randomness, timestamps, or concurrency will show false drift. Mitigation: run regression tests to establish noise baseline.

2. **Threshold tuning required** — Default thresholds (0.70/0.50 overlap) are conservative estimates. Most users will need to calibrate for their domain.

3. **No statistical significance** — Metrics are point estimates without confidence intervals. Use larger anchor sets (100+) for stability.

4. **Limited to top-K** — Only compares top-K results. Changes outside top-K are invisible. Set K to match user-facing display limit.

5. **Anchor selection critical** — Unrepresentative anchor sets produce misleading results. Sample from production usage patterns.

See [Known Limitations & Failure Modes](./docs/when-to-use.md#known-limitations--failure-modes) for full details and mitigations.

---

### Roadmap (Non-Committal)

Potential future work (no promises, pending feedback):

- Streaming comparison for large snapshots
- Anchor set validation and coverage analysis
- Historical trend tracking (compare across multiple snapshots)
- Additional metrics (e.g., neighbor diversity, position bias)
- Integration examples for common MLOps platforms
- Performance optimizations for 100K+ anchor comparisons

**Feedback welcome:** Open an issue to discuss priorities or propose new capabilities.

---

## Links

- **Repository:** https://github.com/RohitSh26/vector-guardrails
- **Documentation:** [docs/README.md](./docs/README.md)
- **Examples:** [examples/README.md](./examples/README.md)
- **Design Philosophy:** [DESIGN.md](./DESIGN.md)
- **License:** Apache-2.0

---

## Versioning Policy

Vector Guardrails follows [Semantic Versioning](https://semver.org/):

- **MAJOR (x.0.0):** Breaking changes to public API, CLI, or snapshot format
- **MINOR (0.x.0):** New features, non-breaking changes, significant improvements
- **PATCH (0.0.x):** Bug fixes, documentation updates, minor tweaks

**Current status:** v0.1.0 is the first stable release. The core comparison logic, CLI, and API are considered stable. Breaking changes will be clearly documented and versioned appropriately.

**Pre-1.0 caveat:** While v0.1 is stable for its intended use cases, the version number reflects early-stage maturity. Use in production with manual review gates and domain-specific calibration.
