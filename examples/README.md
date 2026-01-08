# Vector Guardrails Examples

This directory contains runnable examples demonstrating `vector-guardrails` usage.

## Prerequisites

```bash
# Install the package (from repo root)
pip install -e .
```

## Examples Overview

| Example | Scenario | Expected Exit Code |
|---------|----------|-------------------|
| `01_basic_comparison/` | Identical results | `0` (SAFE/INFO) |
| `02_anchor_mismatch/` | Different anchor sets | `1` (WARNING) |
| `03_high_churn/` | Significant neighbor drift | `2` (CRITICAL) |
| `api_usage.py` | Python API (no CLI) | N/A |

## Running the Examples

### CLI Examples

Each numbered directory contains `baseline.json` and `candidate.json` files.

```bash
# From repo root:

# Example 1: Basic comparison (expect exit code 0)
vector-guardrails compare \
  --baseline examples/01_basic_comparison/baseline.json \
  --candidate examples/01_basic_comparison/candidate.json \
  --k 3

# Example 2: Anchor mismatch (expect exit code 1)
vector-guardrails compare \
  --baseline examples/02_anchor_mismatch/baseline.json \
  --candidate examples/02_anchor_mismatch/candidate.json \
  --k 3

# Example 3: High churn (expect exit code 2)
vector-guardrails compare \
  --baseline examples/03_high_churn/baseline.json \
  --candidate examples/03_high_churn/candidate.json \
  --k 5
```

### Check Exit Code

```bash
vector-guardrails compare \
  --baseline examples/01_basic_comparison/baseline.json \
  --candidate examples/01_basic_comparison/candidate.json \
  --k 3
echo "Exit code: $?"
```

### JSON Output

```bash
# Summary to stdout
vector-guardrails compare \
  --baseline examples/01_basic_comparison/baseline.json \
  --candidate examples/01_basic_comparison/candidate.json \
  --k 3 \
  --format json

# Full report to file
vector-guardrails compare \
  --baseline examples/01_basic_comparison/baseline.json \
  --candidate examples/01_basic_comparison/candidate.json \
  --k 3 \
  --output report.json
```

### Python API

```bash
python examples/api_usage.py
```

## Exit Codes Reference

| Code | Risk Level | CI/CD Action |
|------|------------|--------------|
| `0` | SAFE / INFO | Proceed |
| `1` | WARNING | Review recommended |
| `2` | CRITICAL | Review required |
| `3` | ERROR | Invalid input / IO failure |

## Key Report Fields

When inspecting output (text or JSON), focus on:

- `overall_risk_level` — The final verdict (SAFE, INFO, WARNING, CRITICAL)
- `compared_anchors` — How many anchors were in both snapshots
- `mean_overlap` — Average neighbor overlap across anchors (0.0–1.0)
- `churn_rate` — Fraction of anchors below the overlap warning threshold
- `anchor_jaccard` — Similarity of anchor ID sets (1.0 = identical sets)

## Snapshot Format

Each snapshot is a JSON object mapping anchor IDs to ordered neighbor lists:

```json
{
  "anchor_id_1": ["neighbor_a", "neighbor_b", "neighbor_c"],
  "anchor_id_2": ["neighbor_x", "neighbor_y", "neighbor_z"]
}
```

- Keys are anchor IDs (strings)
- Values are ordered lists of neighbor IDs (strings)
- The `--k` flag controls how many neighbors are compared (truncates if longer)
