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

## Known Limitations & Failure Modes

Vector Guardrails v0.1 has real limitations. Understanding them helps you interpret results safely.

### 1. Non-Deterministic Systems Produce Noise

**Problem:** If your retrieval system returns different results for the same query (due to randomness, concurrency, or timestamps), you'll see false drift.

**Symptoms:**
- Comparing identical systems yields overlap < 1.00
- Repeated snapshots from the same system differ
- Random WARNING signals on unchanged systems

**Common causes:**
- Random tie-breaking in ranking
- Timestamp-based scoring (recency bias)
- Concurrent index updates during snapshot generation
- Load balancer distributing queries across inconsistent shards

**What to do:**
- Run regression tests first (compare system to itself, expect overlap = 1.00)
- If you see noise, fix the non-determinism or accept looser thresholds
- Snapshot during low-traffic windows or maintenance mode
- Generate 3 snapshots, compare pairwise to quantify noise floor

**You cannot trust drift signals if your baseline has noise.**

---

### 2. Personalization and Context-Dependent Ranking

**Problem:** If retrieval results depend on context beyond the anchor (user profile, session state, location, time), snapshots capture a single context snapshot, not the full behavior.

**Example:**
- User-based recommendations change as user profiles update
- Location-based search returns different results by geography
- Session-aware ranking depends on click history

**Symptoms:**
- High drift when nothing changed (context shifted between snapshots)
- Results don't reproduce in testing (context not captured in anchor ID)

**What to do:**
- Use synthetic, stateless test queries (not real user sessions)
- Include context in anchor IDs if possible (e.g., `user_new_york` vs `user_london`)
- Accept that you're measuring "anchor + frozen context" drift, not full system behavior
- Consider this a smoke test, not comprehensive validation

**Guardrails measures retrieval drift for fixed inputs, not personalized/dynamic systems.**

---

### 3. False Negatives: High Overlap, Terrible Results

**Problem:** Overlap measures stability, not quality. A system can have 90% overlap but the changed 10% are the most important results.

**Example:**
- Top-1 result changes from correct → wrong, but positions 2-10 are unchanged
- Overlap = 0.90 (good), but user experience is broken
- Rank displacement might catch this, but only if you inspect per-anchor metrics

**What to do:**
- Don't blindly trust exit code 0 (SAFE/INFO)
- Manually inspect a sample of comparisons, especially for high-traffic queries
- Use complementary quality metrics (NDCG, MRR) in addition to stability
- Pay attention to rank displacement, not just overlap

**Stability ≠ quality. A stable broken system is still broken.**

---

### 4. Anchor Selection Bias

**Problem:** If your anchor set doesn't represent real usage, you're measuring the wrong thing.

**Example:**
- Test with 100 popular queries, miss drift on long-tail queries (which are 80% of traffic)
- Use synthetic queries that don't match user intent patterns
- Anchor set is outdated (represents last year's usage, not current)

**Symptoms:**
- Guardrails says SAFE, but users complain
- High drift on queries not in your anchor set
- A/B tests show different results than offline comparison

**What to do:**
- Sample anchors from production query logs (recent, representative)
- Include long-tail and edge-case queries, not just popular ones
- Refresh anchor sets periodically (quarterly or after major usage shifts)
- Stratify by category/segment if your system has diverse use cases

**Guardrails only measures what you test. Garbage in, garbage out.**

---

### 5. Threshold Tuning is Required

**Problem:** Default thresholds (0.70/0.50 overlap) are educated guesses, not empirical truth. They may be wrong for your domain.

**Example:**
- Recommendation systems often have healthy churn (users want variety) → defaults too strict
- Medical/legal search demands high precision → defaults too loose
- Your system has 5% inherent noise → you'll get constant false alarms

**Symptoms:**
- Every change triggers WARNING (alert fatigue)
- Real regressions pass with exit code 0 (thresholds too loose)
- You're constantly debating "is this a real issue?"

**What to do:**
- Follow the calibration guide (measure noise, define tolerance, tune)
- Budget 2-4 hours for initial threshold tuning
- Accept that thresholds may need adjustment as your system evolves
- Document your tuning rationale for your team

**Defaults are starting points. Expect to tune. If you don't, you're probably using this wrong.**

---

### 6. Snapshot Versioning and Consistency

**Problem:** If you lose track of what snapshot corresponds to what system state, comparisons are meaningless.

**Example:**
- Baseline snapshot is from 3 months ago, candidate is from today → corpus has changed
- You compare wrong snapshots (baseline = model A, but you thought it was model B)
- Anchor set differs between snapshots (different queries used)

**Symptoms:**
- Unexpected drift on supposedly unchanged systems
- Can't reproduce comparison results
- Low anchor Jaccard (< 0.90) when you expected identical sets

**What to do:**
- Include metadata with snapshots (model version, index config, timestamp, anchor set hash)
- Use filename conventions: `baseline_model-v1.2_2024-01-08.json`
- Store anchor sets separately and reuse them for consistency
- Version control snapshots or store in artifact repository

**Snapshot hygiene is critical. Sloppy snapshots = useless comparisons.**

---

### 7. Limited to Top-K Comparison

**Problem:** Guardrails only compares the top K results. Changes outside top-K are invisible.

**Example:**
- K=10, but a relevant document dropped from position 8 → position 15
- Overlap shows this as a loss, but doesn't tell you the document is still nearby
- You might be comparing K=10, but users see K=20 (pagination)

**What to do:**
- Set K to match your UI's display limit (if you show 20 results, use K=20)
- Understand that "not in top-K" could mean rank 11 or rank 10,000
- Consider running comparisons at multiple K values (K=5, K=10, K=20) to see stability curves

**Guardrails is blind to results outside top-K. Choose K carefully.**

---

### 8. No Statistical Significance Testing

**Problem:** Guardrails reports raw metrics (overlap = 0.68) without confidence intervals or p-values.

**Example:**
- 100 anchors, overlap = 0.69 → is this statistically different from 0.70?
- High variance across anchors (some 1.00, some 0.40) → mean doesn't tell the story
- Small anchor sets (N=20) → high sampling noise

**What to do:**
- Use larger anchor sets (100+) for more stable metrics
- Inspect per-anchor metrics (look for patterns, not just the mean)
- Treat thresholds as approximate guidelines, not hard lines
- If overlap is near a threshold boundary (0.68 vs 0.70), manually review

**Metrics are point estimates. There's no "95% confidence" here. Use judgment.**

---

## Failure Mode Summary Table

| Failure Mode | Symptom | Safe Interpretation |
|--------------|---------|---------------------|
| **Non-deterministic system** | Overlap < 1.00 on identical snapshots | Fix non-determinism first, or accept noise |
| **Personalized ranking** | Drift when nothing changed | Use stateless test queries, expect limitations |
| **High overlap, bad results** | Exit 0 but users complain | Always combine with quality metrics |
| **Unrepresentative anchors** | Guardrails says SAFE, A/B test disagrees | Sample anchors from real usage patterns |
| **Wrong thresholds** | Constant false alarms or missed issues | Calibrate thresholds for your domain |
| **Snapshot confusion** | Can't reproduce results | Version snapshots with metadata |
| **K is too small** | Misses changes in lower-ranked results | Set K to match user-facing display limit |
| **No statistical tests** | Metrics near threshold boundaries | Use judgment, inspect per-anchor details |

---

## How to Use This Safely

1. **Start with regression tests** — Compare your system to itself. Establish noise baseline.
2. **Don't trust exit codes blindly** — Always inspect metrics and flagged anchors.
3. **Combine with other signals** — Use quality metrics (NDCG, MRR), A/B tests, user feedback.
4. **Expect false positives** — WARNING doesn't mean "don't deploy," it means "look closer."
5. **Calibrate for your domain** — Default thresholds are guesses. Tune them.
6. **Keep snapshot hygiene** — Version everything, reuse anchor sets, document metadata.

**Vector Guardrails is a signal, not a verdict.** It tells you "something changed," not "this is bad" or "this will break production." Your judgment and domain expertise remain essential.

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

**Reality check:** v0.1 has limitations. Understand them. Use judgment. Don't automate decisions blindly.
