# Vector Guardrails — Design Document

**Version:** 0.1.0-design  
**Status:** Design approved, implementation in progress

---

## Project Goal

Vector Guardrails helps teams detect risky or unintended semantic changes in
embedding-based retrieval systems *before* those changes impact users.

---

## Core Principles

- Conservative by default
- Architecture-agnostic
- Retrieval-output comparison (not embeddings)
- Explainable, human-readable outputs
- Easy to disable or remove

---

## Comparison Primitive

The library compares **retrieval outputs**:

anchor_id → ordered list of neighbors


It does not inspect raw vectors or embedding internals.

---

## Metrics (v0.1)

- Overlap@K (primary)
- Rank displacement (shared neighbors only)
- Churn rate (aggregate)

---

## Risk Levels

SAFE → INFO → WARNING → CRITICAL

Risk classification is conservative and configurable.

---

## Anchor Alignment Strategy

Baseline and candidate snapshots may differ in anchor_ids.

Strategy:
- Compare the intersection
- Warn if |A∩B| / |A∪B| < 0.90
- Report missing anchors
- Proceed with comparison

---

## Out of Scope (v0.1)

- Training embeddings
- Online serving
- Real-time monitoring
- Automatic decisions
- UI dashboards

---

## Implementation Approach

- Test-first development
- Small, reviewable commits
- Clear contracts before logic
