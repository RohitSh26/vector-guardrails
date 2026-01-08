# vector-guardrails

**Safety-first guardrails for embedding-based retrieval and recommendation systems.**

`vector-guardrails` helps teams detect **risky or unintended semantic changes**
in embedding-based search and recommendation systems *before* those changes
impact users.

---

## Why this exists

Modern search and recommendation systems rely heavily on embeddings and
nearest-neighbor retrieval.

When embeddings or retrieval logic change:
- nothing crashes
- metrics may look fine
- but recommendations can silently drift in meaning

This library answers a simple but critical question:

> **“Did ‘similar’ start meaning something different?”**

---

## What this library does

- Compares **retrieval outputs** (baseline vs candidate)
- Measures **stability of nearest neighbors**
- Produces **conservative, explainable risk signals**
- Works with *any* vector store or retrieval engine
- Designed for **offline checks and CI/CD gating**

---

## What this library does NOT do

- ❌ Train embeddings
- ❌ Serve vectors
- ❌ Optimize ranking quality
- ❌ Perform real-time monitoring
- ❌ Automatically roll back deployments

This is a **safety and understanding layer**, not an optimization engine.

## Quick Start

### Installation

```bash
pip install vector-guardrails
```

### CLI Usage

```bash
# Compare two retrieval snapshots
vector-guardrails compare \
  --baseline baseline.json \
  --candidate candidate.json \
  --k 10

# JSON summary to stdout
vector-guardrails compare \
  --baseline baseline.json \
  --candidate candidate.json \
  --k 10 \
  --format json

# Full report to file
vector-guardrails compare \
  --baseline baseline.json \
  --candidate candidate.json \
  --k 10 \
  --output report.json
```

### Python API

```python
from vector_guardrails import compare, ComparisonConfig

report = compare(
    baseline={"anchor_1": ["a", "b", "c"]},
    candidate={"anchor_1": ["a", "b", "d"]},
    config=ComparisonConfig(k=3),
)

print(report.overall_risk_level)  # INFO, WARNING, or CRITICAL
print(report.to_exit_code())      # 0, 1, or 2
```

### Exit Codes

| Code | Risk Level | CI/CD Action |
|------|------------|--------------|
| `0` | SAFE / INFO | Proceed |
| `1` | WARNING | Review recommended |
| `2` | CRITICAL | Review required |
| `3` | ERROR | Invalid input |

---

## Examples

See [`examples/`](./examples/) for runnable examples:

| Example | Scenario | Exit Code |
|---------|----------|-----------|
| `01_basic_comparison/` | Identical results | `0` |
| `02_anchor_mismatch/` | Different anchor sets | `1` |
| `03_high_churn/` | Significant drift | `2` |
| `api_usage.py` | Python API usage | — |

---

## Core Concepts

### Snapshots

A **snapshot** is a JSON file capturing your retrieval system's outputs at a point in time:

```json
{
  "query_1": ["result_a", "result_b", "result_c"],
  "query_2": ["result_x", "result_y", "result_z"]
}
```

- **Keys:** Anchor IDs (queries, items, users—depends on your use case)
- **Values:** Ordered lists of neighbor IDs (retrieval results, ranked by relevance)

**New to "anchor" terminology?** See **[Understanding Anchors and Neighbors](./docs/anchor-terminology.md)** for a detailed mapping to your use case.

**Need to generate snapshots?** See **[How to Generate Snapshots](./docs/generating-snapshots.md)** for code examples across different retrieval systems.

### Metrics

| Metric | Description | Default Thresholds |
|--------|-------------|-------------------|
| **Overlap@K** | Fraction of neighbors in common | < 0.70 → WARNING, < 0.50 → CRITICAL |
| **Rank Displacement** | Average position change of shared neighbors | > 3.0 → WARNING, > 5.0 → CRITICAL |
| **Churn Rate** | Fraction of anchors with low overlap | > 0.20 → WARNING, > 0.35 → CRITICAL |
| **Anchor Jaccard** | Similarity of anchor ID sets | < 0.90 → WARNING |

**Want to understand or tune thresholds?** See **[Threshold Philosophy & Calibration Guide](./docs/thresholds-and-tuning.md)**.

---

## Documentation

### Getting Started
- **[When to Use Vector Guardrails](./docs/when-to-use.md)** — Understand when (and when not) to run comparisons
- **[How to Generate Snapshots](./docs/generating-snapshots.md)** — Code examples for search, recommendations, and RAG systems
- **[Understanding Anchors and Neighbors](./docs/anchor-terminology.md)** — Clarify terminology for your use case

### Advanced Topics
- **[Threshold Philosophy & Calibration](./docs/thresholds-and-tuning.md)** — Why defaults exist and how to tune for your system
- **[Examples](./examples/)** — Runnable examples demonstrating different scenarios

---

## Status

🚧 **Early development (v0.1.0 in progress)**  
Design is finalized. Implementation is underway using a test-first approach.

See [`DESIGN.md`](./DESIGN.md) for the full design contract.

---

## License

Apache-2.0
