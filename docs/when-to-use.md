# When to Use Vector Guardrails

Vector Guardrails is designed for **offline, pre-deployment comparison** of retrieval outputs. This guide explains when—and when not—to use it.

---

## When to Run Comparisons

### 1. Before Deploying a New Embedding Model

**Scenario:** You've retrained your embedding model or switched to a different model (e.g., `text-embedding-ada-002` → `text-embedding-3-large`).

**What to do:**
1. Generate a baseline snapshot using your current production model
2. Generate a candidate snapshot using the new model
3. Compare with `vector-guardrails compare`

**Why it matters:** Embedding model changes can cause dramatic semantic drift, even if the new model has "better" benchmark scores. Guardrails helps you understand the impact before users see it.

**Example:**
```bash
# Baseline: current model
python scripts/generate_snapshot.py --model prod-v1 --output baseline.json

# Candidate: new model
python scripts/generate_snapshot.py --model candidate-v2 --output candidate.json

# Compare
vector-guardrails compare --baseline baseline.json --candidate candidate.json --k 10
```

---

### 2. After Rebuilding Your Vector Index

**Scenario:** You've rebuilt your vector index due to:
- Infrastructure changes (e.g., switching from FAISS to Pinecone)
- Index configuration changes (e.g., HNSW parameters, quantization settings)
- Data pipeline changes (e.g., new preprocessing logic)

**What to do:**
1. Generate a snapshot from the old index (before rebuild)
2. Generate a snapshot from the new index
3. Compare to ensure consistency

**Why it matters:** Index rebuilds should be deterministic if nothing else changed. Drift here indicates a bug or misconfiguration.

**Red flag:** If you see CRITICAL when only rebuilding an index with the same data and model, investigate immediately.

---

### 3. Before Major Corpus Updates

**Scenario:** You're adding, removing, or significantly updating documents in your retrieval corpus.

**What to do:**
1. Snapshot before the update
2. Snapshot after the update
3. Compare to understand how query results shifted

**Why it matters:** Large corpus changes can shift retrieval semantics. A query that previously returned "Python tutorials" might now return "Python snake facts" if you added wildlife content.

**Expectation:** Some drift is expected and healthy. Use this to understand the magnitude, not to block deployment.

---

### 4. Regression Testing for Determinism

**Scenario:** You want to ensure your retrieval system is deterministic (returns the same results for the same input).

**What to do:**
1. Generate two snapshots from the same system, back-to-back
2. Compare them—expect exit code 0 (INFO/SAFE)

**Why it matters:** Non-determinism can indicate:
- Randomness in indexing or retrieval
- Concurrent index updates
- Timestamp-based ranking

**Red flag:** If identical systems don't produce identical snapshots, your system isn't stable enough for meaningful drift detection.

---

### 5. Validating A/B Test Setup

**Scenario:** You're running an A/B test with a new retrieval variant and want to quantify the difference before exposing it to users.

**What to do:**
1. Generate snapshots from both variants (A and B)
2. Compare to understand the semantic delta
3. Use this to inform rollout decisions (gradual vs full)

**Why it matters:** "Try the new model and see what happens" is risky. Guardrails gives you a preview of the blast radius.

**Note:** This is a pre-deployment check, not a replacement for live A/B testing with engagement metrics.

---

### 6. Monitoring Scheduled Retraining Pipelines

**Scenario:** Your embedding model retrains weekly/monthly, and you want to ensure updates don't cause regressions.

**What to do:**
1. Add a comparison step to your retraining pipeline
2. Generate a snapshot before and after retraining
3. Gate deployment on WARNING/CRITICAL thresholds

**Why it matters:** Automated retraining can silently degrade quality. Guardrails acts as a safety check.

**Integration example:**
```yaml
# CI/CD pipeline
- name: Retrain model
  run: python train.py

- name: Generate snapshots
  run: |
    python snapshot.py --model prod --output baseline.json
    python snapshot.py --model retrained --output candidate.json

- name: Check for drift
  run: vector-guardrails compare --baseline baseline.json --candidate candidate.json --k 10
  continue-on-error: true  # Log but don't block on WARNING

- name: Block on CRITICAL
  run: |
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
      echo "CRITICAL drift detected - blocking deployment"
      exit 1
    fi
```

---

### 7. Debugging Unexpected Retrieval Behavior

**Scenario:** Users report that search/recommendations "feel different" but metrics look normal.

**What to do:**
1. Generate a snapshot from the current (suspect) system
2. Compare against a known-good baseline snapshot from days/weeks ago
3. Investigate anchors flagged as CRITICAL or WARNING

**Why it matters:** Guardrails can surface semantic drift that aggregate metrics miss. High churn with stable precision@k is possible.

**Limitation:** This requires you to have historical baseline snapshots. Start collecting them proactively.

---

## When NOT to Use Vector Guardrails

### ❌ Real-Time Monitoring

Vector Guardrails is **not** a production monitoring tool. It compares static snapshots, not live traffic.

**Use instead:** APM tools, retrieval latency/error rate dashboards, live A/B testing platforms.

---

### ❌ Measuring Retrieval Quality

Vector Guardrails measures **stability**, not **quality**. A perfectly stable system can still have bad results.

**Use instead:** Offline evaluation with relevance judgments (NDCG, MRR, Precision@K), user engagement metrics (CTR, dwell time).

---

### ❌ Optimizing Retrieval Performance

Guardrails doesn't tell you how to improve results, only if they've changed.

**Use instead:** Embedding model benchmarks, hyperparameter tuning, retrieval algorithm experimentation.

---

### ❌ Detecting Data Quality Issues

If your document corpus has low-quality or duplicate content, Guardrails won't flag it—it only detects changes.

**Use instead:** Data quality pipelines, deduplication tools, content audits.

---

### ❌ Replacing Human Judgment

WARNING and CRITICAL signals are not automatic "deploy" or "don't deploy" decisions. They're flags for human review.

**Use instead:** Domain expert review, user testing, phased rollouts.

---

## Recommended Workflow

```
┌─────────────────────────────────────┐
│ Change to retrieval system          │
│ (model, index, corpus, config)      │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Generate baseline snapshot          │
│ (current production state)          │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Generate candidate snapshot         │
│ (proposed new state)                │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│ Run vector-guardrails compare       │
└─────────────────┬───────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   Exit 0 (SAFE/INFO)   Exit 1/2 (WARNING/CRITICAL)
        │                   │
        ▼                   ▼
   Deploy with      Investigate & review
   confidence       - Check flagged anchors
                    - Validate with domain experts
                    - Consider phased rollout
                    - Adjust thresholds if noise
```

---

## Questions to Ask Yourself

Before running a comparison, clarify:

1. **What changed?** Model, index, corpus, or config?
2. **What's the baseline?** Current production, or a previous candidate?
3. **What's acceptable drift?** Is some change expected (e.g., corpus update)?
4. **What will I do with the result?** Block deployment? Investigate? Log and proceed?
5. **Do I have the right anchor set?** Does it represent real usage?

If you can't answer these, you're not ready to interpret the results meaningfully.

---

## Summary

**Use Vector Guardrails when:**
- You're about to change something in your retrieval pipeline
- You want to quantify semantic drift before users see it
- You need a safety check in automated workflows

**Don't use it when:**
- You need real-time monitoring (use APM instead)
- You need to measure quality (use offline eval instead)
- You need to optimize performance (use benchmarks instead)

**Golden rule:** Guardrails answers "did similar start meaning something different?" It doesn't answer "is this good?" or "should I deploy?"
