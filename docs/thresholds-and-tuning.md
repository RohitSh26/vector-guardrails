# Threshold Philosophy & Calibration Guide

Vector Guardrails uses thresholds to classify retrieval changes as SAFE, WARNING, or CRITICAL. This guide explains the philosophy behind the defaults and how to tune them for your use case.

---

## Default Thresholds (v0.1)

```python
class ThresholdPreset(BaseModel):
    overlap_warning: float = 0.70      # < 70% overlap → WARNING
    overlap_critical: float = 0.50     # < 50% overlap → CRITICAL

    displacement_warning: float = 3.0  # > 3 positions → WARNING
    displacement_critical: float = 5.0 # > 5 positions → CRITICAL

    churn_warning: float = 0.20        # > 20% of anchors churning → WARNING
    churn_critical: float = 0.35       # > 35% of anchors churning → CRITICAL

    anchor_jaccard_warning: float = 0.90  # < 90% anchor overlap → WARNING
```

---

## Why These Defaults?

### Philosophy: Conservative by Default

The defaults are intentionally **strict** to err on the side of caution. The reasoning:

1. **False negatives are expensive** — Missing a real regression that impacts users is worse than a false alarm
2. **You can always tune looser** — Starting strict and relaxing is safer than starting loose and tightening
3. **Noise should be investigated** — Even "false positives" often reveal something worth knowing

### Where They Come From

**Honest answer:** These are **engineering judgment**, not empirically derived from large-scale studies.

They're based on:
- Experience with embedding model changes (e.g., switching OpenAI models)
- Common-sense expectations (70% overlap = "most neighbors stayed the same")
- Preference for false alarms over silent failures

**What they're NOT:**
- ❌ Scientifically validated across diverse domains
- ❌ Optimized for any specific use case (search vs recommendations)
- ❌ Guaranteed to match your organization's risk tolerance

**You will likely need to tune them.** That's expected and encouraged.

---

## Understanding Each Threshold

### 1. Overlap Thresholds

**Metric:** For each anchor, what fraction of top-K neighbors appeared in both baseline and candidate?

```
Overlap = |baseline_neighbors ∩ candidate_neighbors| / K
```

**Thresholds:**
- `overlap_warning = 0.70` → If < 70% of neighbors are shared, flag as WARNING
- `overlap_critical = 0.50` → If < 50% of neighbors are shared, flag as CRITICAL

**Interpretation:**

| Overlap | Meaning | Example (K=10) |
|---------|---------|----------------|
| 1.00 | Perfect stability | All 10 neighbors identical |
| 0.80 | Strong stability | 8 out of 10 neighbors same |
| **0.70** | **Moderate drift (WARNING)** | 7 out of 10 neighbors same |
| 0.60 | Noticeable drift | 6 out of 10 neighbors same |
| **0.50** | **High drift (CRITICAL)** | Only 5 out of 10 neighbors same |
| 0.30 | Severe drift | Only 3 out of 10 neighbors same |
| 0.00 | Complete change | No neighbors in common |

**When to adjust:**

- **Tighten (0.80/0.60):** High-stakes systems where even small drift matters (e.g., medical search, legal RAG)
- **Loosen (0.60/0.40):** Recommendation systems where some churn is healthy (e.g., content discovery, exploration-heavy UIs)

---

### 2. Rank Displacement Thresholds

**Metric:** For neighbors that appear in both baseline and candidate, how much did their position change on average?

```
Displacement = Mean(|baseline_rank - candidate_rank|) for shared neighbors
```

**Thresholds:**
- `displacement_warning = 3.0` → If average shift > 3 positions, flag WARNING
- `displacement_critical = 5.0` → If average shift > 5 positions, flag CRITICAL

**Interpretation:**

| Displacement | Meaning | Example |
|--------------|---------|---------|
| 0.0 | Identical ranking | Neighbors in exact same order |
| 1.5 | Minor shuffling | Top result might swap with #2 |
| **3.0** | **Noticeable reordering (WARNING)** | #1 might drop to #4 |
| **5.0** | **Major reordering (CRITICAL)** | #1 might drop to #6 |
| 10.0 | Dramatic reordering | Top results now mid-pack |

**When to adjust:**

- **Tighten (2.0/3.0):** Ranking order is critical (e.g., search where position 1 vs 3 matters for CTR)
- **Loosen (5.0/8.0):** Ranking is less important than presence (e.g., "related items" widgets where all top-10 are equally visible)

**Note:** Displacement only measures **shared** neighbors. If all neighbors changed (overlap = 0), displacement is undefined.

---

### 3. Churn Rate Thresholds

**Metric:** What fraction of anchors have overlap below the `overlap_warning` threshold?

```
Churn Rate = (# anchors with overlap < overlap_warning) / (total anchors)
```

**Thresholds:**
- `churn_warning = 0.20` → If > 20% of anchors are churning, flag WARNING
- `churn_critical = 0.35` → If > 35% of anchors are churning, flag CRITICAL

**Interpretation:**

| Churn Rate | Meaning | Example (100 anchors) |
|------------|---------|----------------------|
| 0.00 | No churn | All anchors stable |
| 0.10 | Isolated issues | 10 anchors problematic |
| **0.20** | **Widespread issues (WARNING)** | 20 anchors problematic |
| **0.35** | **Systemic issues (CRITICAL)** | 35 anchors problematic |
| 0.50 | Majority affected | 50 anchors problematic |
| 1.00 | Total breakdown | All anchors unstable |

**When to adjust:**

- **Tighten (0.10/0.20):** You expect very few anchors to change (e.g., deterministic system, no corpus updates)
- **Loosen (0.30/0.50):** Some churn is expected (e.g., you updated the corpus, added new documents)

**Why it matters:** Even if mean overlap is high (0.85), if 40% of anchors have overlap < 0.70, you have a problem. Churn rate captures this.

---

### 4. Anchor Jaccard Threshold

**Metric:** How similar are the anchor ID sets between baseline and candidate?

```
Anchor Jaccard = |baseline_anchors ∩ candidate_anchors| / |baseline_anchors ∪ candidate_anchors|
```

**Threshold:**
- `anchor_jaccard_warning = 0.90` → If < 90% of anchors are shared, flag WARNING

**Interpretation:**

| Jaccard | Meaning | Example |
|---------|---------|---------|
| 1.00 | Identical anchor sets | Same queries/items in both |
| **0.90** | **Minor mismatch (WARNING)** | 90% overlap, 10% different |
| 0.70 | Moderate mismatch | 70% overlap, 30% different |
| 0.50 | Major mismatch | Only half of anchors in common |
| 0.00 | No overlap | Completely different anchor sets |

**When to adjust:**

- **Tighten (0.95):** You expect near-perfect anchor alignment (e.g., using a fixed test set)
- **Loosen (0.80):** Some anchor differences are expected (e.g., different sampling of production queries)

**Why it matters:** Low Jaccard means you're comparing apples to oranges. The comparison is still valid for the anchors that overlap, but the coverage is limited.

---

## Calibration Process

### Step 1: Establish a Baseline of Noise

Before using guardrails for real changes, measure your **system's inherent variability**.

**Process:**

1. Generate two snapshots from the **same system** (no changes), back-to-back
2. Compare them: `vector-guardrails compare --baseline snap1.json --candidate snap2.json --k 10`
3. Note the results

**Expected result:** Exit code 0 (SAFE/INFO), perfect overlap (1.00), no churn.

**If you see WARNING or CRITICAL:**
- Your system is non-deterministic (randomness in retrieval, concurrent updates)
- Fix the non-determinism, or accept that you'll need looser thresholds

**Example:**

```bash
# Generate baseline
python snapshot.py --output baseline.json

# Generate candidate (no changes!)
python snapshot.py --output candidate.json

# Compare
vector-guardrails compare --baseline baseline.json --candidate candidate.json --k 10
```

If overlap < 1.00, investigate why. Common causes:
- Random tie-breaking in retrieval
- Concurrent index updates
- Timestamp-based ranking

---

### Step 2: Measure Typical Change Magnitude

Make a **small, controlled change** (e.g., retrain model, add 5% new documents) and measure the impact.

**Process:**

1. Generate baseline (before change)
2. Make the change
3. Generate candidate (after change)
4. Compare and note metrics

**Goal:** Understand what "normal change" looks like for your system.

**Example results:**

| Change | Mean Overlap | Churn Rate | Risk Level |
|--------|--------------|------------|------------|
| No change (regression test) | 1.00 | 0.00 | SAFE |
| Model retrained (same data) | 0.95 | 0.05 | INFO |
| Model switched (ada-002 → v3-large) | 0.62 | 0.45 | CRITICAL |
| Corpus +10% new docs | 0.88 | 0.12 | INFO |
| Index rebuilt (same config) | 1.00 | 0.00 | SAFE |

---

### Step 3: Define Your Risk Tolerance

Ask your team:

**"What level of change would require manual review before deployment?"**

Example answers:
- "If more than 10% of queries return different results, we review"
- "If top-3 results change for any query, we review"
- "We're okay with churn as long as mean overlap > 0.60"

Map these to thresholds:

| Risk Tolerance | Suggested Thresholds |
|----------------|---------------------|
| **Very conservative** (medical, legal, high-stakes) | overlap: 0.85/0.70, churn: 0.10/0.20 |
| **Conservative** (production search, RAG systems) | overlap: 0.70/0.50, churn: 0.20/0.35 (defaults) |
| **Moderate** (recommendations, content discovery) | overlap: 0.60/0.40, churn: 0.30/0.50 |
| **Permissive** (exploration-heavy, frequent updates) | overlap: 0.50/0.30, churn: 0.40/0.60 |

---

### Step 4: Tune and Validate

**Create a custom threshold preset:**

```python
from vector_guardrails import ComparisonConfig, ThresholdPreset

custom_thresholds = ThresholdPreset(
    overlap_warning=0.60,      # Relaxed from 0.70
    overlap_critical=0.40,     # Relaxed from 0.50
    churn_warning=0.30,        # Relaxed from 0.20
    churn_critical=0.50,       # Relaxed from 0.35
    anchor_jaccard_warning=0.85  # Relaxed from 0.90
)

config = ComparisonConfig(k=10, thresholds=custom_thresholds)

report = compare(baseline, candidate, config=config)
```

**Validation:**

1. Run comparisons on historical changes (if you have snapshots)
2. Check if WARNING/CRITICAL flags align with your intuition
3. Adjust thresholds if you see too many false positives or false negatives

**Iterate:** Threshold tuning is not one-and-done. Revisit as you learn more about your system's behavior.

---

## Common Tuning Scenarios

### Scenario 1: Too Many False Alarms

**Problem:** Every small change triggers WARNING or CRITICAL, even when you know the change is safe.

**Diagnosis:**
- Look at the metrics: Is overlap consistently in the 0.60–0.70 range?
- Is churn rate 0.25–0.30?

**Solution:** Your thresholds are too strict. Loosen them:

```python
ThresholdPreset(
    overlap_warning=0.60,  # Was 0.70
    overlap_critical=0.40,  # Was 0.50
    churn_warning=0.30,     # Was 0.20
    churn_critical=0.50     # Was 0.35
)
```

**Caution:** Don't loosen so much that real issues go undetected. Use historical incidents to guide.

---

### Scenario 2: Missing Real Issues

**Problem:** A change caused user complaints, but guardrails returned SAFE/INFO.

**Diagnosis:**
- Check the metrics: Was overlap 0.75, just above the WARNING threshold?
- Were only a few anchors problematic (low churn), but they were critical queries?

**Solutions:**

1. **Tighten thresholds** (if the issue was widespread but below threshold):
   ```python
   ThresholdPreset(overlap_warning=0.80, overlap_critical=0.60)
   ```

2. **Improve anchor selection** (if the issue was in queries not covered):
   - Add the problematic queries to your anchor set
   - Use more anchors (200 instead of 50)

3. **Use stricter gating** (if INFO is too permissive):
   - Treat INFO as "requires review" in your CI/CD, not auto-approve

---

### Scenario 3: Noisy System (Non-Deterministic)

**Problem:** Running the same snapshot twice gives different results (overlap < 1.00).

**Diagnosis:**
- Your system has inherent randomness or concurrency issues
- Overlap between identical systems is 0.90–0.95, not 1.00

**Solutions:**

1. **Fix the non-determinism** (preferred):
   - Remove random tie-breaking
   - Use deterministic seeds
   - Snapshot during maintenance windows (no concurrent updates)

2. **Accept and compensate** (if you can't fix it):
   - Generate 3 snapshots, use the median overlap as your "true" baseline
   - Loosen thresholds to account for noise:
     ```python
     ThresholdPreset(overlap_warning=0.60, overlap_critical=0.40)
     ```

**Reality check:** If your system is non-deterministic, drift detection is harder. You're measuring signal + noise.

---

### Scenario 4: Different Thresholds for Different Use Cases

**Problem:** You use vector retrieval for both search (strict) and recommendations (permissive), but one threshold set doesn't fit both.

**Solution:** Use different threshold presets for different snapshot comparisons.

```python
# Strict thresholds for search
search_thresholds = ThresholdPreset(
    overlap_warning=0.80,
    overlap_critical=0.60
)

# Permissive thresholds for recommendations
recs_thresholds = ThresholdPreset(
    overlap_warning=0.60,
    overlap_critical=0.40
)

# Compare search snapshots
search_report = compare(
    baseline_search, candidate_search,
    config=ComparisonConfig(k=10, thresholds=search_thresholds)
)

# Compare recommendation snapshots
recs_report = compare(
    baseline_recs, candidate_recs,
    config=ComparisonConfig(k=20, thresholds=recs_thresholds)
)
```

---

## Interpreting Ambiguous Results

### Case 1: High Overlap, High Churn

**Metrics:**
- Mean overlap: 0.85 (good)
- Churn rate: 0.40 (bad)

**What this means:** Most anchors are stable, but 40% of anchors have significant drift. You have **isolated but widespread issues**.

**Action:** Investigate the churning anchors. Are they:
- Specific categories (e.g., all product searches in one department)?
- Edge cases (rare queries)?
- Critical queries (high-traffic searches)?

**Threshold tuning:** This is probably a real issue, not a threshold problem. Don't loosen—investigate.

---

### Case 2: Low Overlap, Low Churn

**Metrics:**
- Mean overlap: 0.55 (bad)
- Churn rate: 0.10 (good)

**What this means:** Most anchors are stable, but the few that changed, changed **dramatically**.

**Action:** Investigate the CRITICAL anchors. Why did they change so much?

**Threshold tuning:** Possibly tighten churn thresholds to catch this earlier:
```python
ThresholdPreset(churn_warning=0.05, churn_critical=0.10)
```

---

### Case 3: Moderate Metrics, Uncertain Risk

**Metrics:**
- Mean overlap: 0.68 (just below WARNING)
- Churn rate: 0.22 (just above WARNING)

**What this means:** You're in the "gray zone". Is this acceptable drift or a problem?

**Action:**
1. **Manual review:** Inspect a sample of anchors. Do the changes make sense?
2. **Context matters:** Is this a corpus update (expected) or a model swap (unexpected)?
3. **Use domain knowledge:** Would your users notice this change?

**Threshold tuning:** If this happens often and it's usually fine, loosen thresholds slightly.

---

## Red Flags (Don't Ignore These)

### 🚩 Overlap = 1.00 but Displacement > 5.0

**Meaning:** All neighbors are the same, but their order changed dramatically.

**Likely cause:** Ranking logic changed (e.g., new scoring function).

**Action:** This is a real change. Investigate if intentional.

---

### 🚩 Anchor Jaccard < 0.50

**Meaning:** Less than half of your anchors appear in both snapshots.

**Likely cause:**
- You used different anchor sets (bug in snapshot generation)
- Your retrieval system changed which queries return results (e.g., new filters)

**Action:** Fix your anchor consistency, or understand why coverage dropped.

---

### 🚩 Churn = 1.00

**Meaning:** Every single anchor has overlap below the WARNING threshold.

**Likely cause:**
- Complete model swap (expected if you changed models)
- Bug in snapshot generation (anchor IDs mismatched)
- Catastrophic system failure

**Action:** If this is unexpected, treat as a critical incident.

---

## Summary

### Default Thresholds Are Strict on Purpose

- Overlap: 0.70/0.50
- Churn: 0.20/0.35
- Jaccard: 0.90

These are **starting points, not gospel**. Tune based on your system and risk tolerance.

---

### Calibration Workflow

1. **Measure noise:** Compare identical systems (expect overlap = 1.00)
2. **Measure signal:** Compare before/after known changes
3. **Define tolerance:** Decide what level of change requires review
4. **Tune thresholds:** Encode your tolerance as thresholds
5. **Validate:** Test on historical changes

---

### When to Tighten vs Loosen

**Tighten (stricter) if:**
- High-stakes domain (medical, legal, finance)
- User complaints about changes you didn't catch
- You want conservative gating (false alarms > missed issues)

**Loosen (more permissive) if:**
- Too many false alarms on safe changes
- Frequent corpus updates make churn normal
- You have strong downstream validation (A/B tests, manual review)

---

### Final Advice

**Thresholds are policy, not science.** They encode your team's risk tolerance. Start with defaults, tune based on experience, and revisit as your system evolves.

**When in doubt, investigate.** A WARNING isn't a red light—it's a "look closer" signal. Better to review 10 false alarms than miss 1 real regression.
