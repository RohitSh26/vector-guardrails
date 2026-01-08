# Understanding Anchors and Neighbors

Vector Guardrails uses the terms **anchor** and **neighbor** to describe retrieval comparisons in a use-case-agnostic way. This guide clarifies what these mean for your specific use case.

---

## The Core Concept

In any retrieval system, you have:

1. **An input** (what you're querying with)
2. **A set of outputs** (what the system returns)

We call:
- **Anchor** = The input to your retrieval system
- **Neighbors** = The outputs returned by your retrieval system

The library compares how **neighbors change** when something in your retrieval pipeline changes (model, index, corpus, etc.).

---

## Use Case Mapping Table

| Use Case | Anchor | Neighbors | Example Snapshot |
|----------|--------|-----------|-----------------|
| **Text Search** | Query text (or query ID) | Document IDs returned | `{"query_1": ["doc_a", "doc_b"]}` |
| **Semantic Search** | User question (or question ID) | Passage/chunk IDs returned | `{"q_42": ["chunk_100", "chunk_203"]}` |
| **Item-to-Item Recommendations** | Item ID (seed item) | Recommended item IDs | `{"product_123": ["product_456", "product_789"]}` |
| **User-Based Recommendations** | User ID (or persona ID) | Recommended item IDs | `{"user_alice": ["item_x", "item_y"]}` |
| **Image Similarity** | Image ID (query image) | Similar image IDs | `{"img_001": ["img_042", "img_099"]}` |
| **Document Deduplication** | Document ID | Near-duplicate document IDs | `{"doc_a": ["doc_a_v2", "doc_similar"]}` |
| **RAG (Retrieval-Augmented Generation)** | User prompt (or prompt ID) | Retrieved context chunk IDs | `{"prompt_5": ["ctx_12", "ctx_34"]}` |

---

## Detailed Examples

### Example 1: E-Commerce Product Search

**Your system:** Users search for products using text queries.

**Retrieval flow:**
```
User types: "wireless headphones"
  ↓
Embedding model converts to vector
  ↓
Vector search returns top 10 product IDs
  ↓
Products displayed to user
```

**In Vector Guardrails terms:**
- **Anchor:** `"query_wireless_headphones"` (you assign an ID to this query)
- **Neighbors:** `["prod_1001", "prod_2034", "prod_5678", ...]` (the product IDs returned)

**Snapshot structure:**
```json
{
  "query_wireless_headphones": ["prod_1001", "prod_2034", "prod_5678"],
  "query_running_shoes": ["prod_3021", "prod_4092", "prod_1233"],
  "query_coffee_maker": ["prod_8871", "prod_2201", "prod_9987"]
}
```

**What you're measuring:** When you change your embedding model or product catalog, do searches for "wireless headphones" return the same products?

---

### Example 2: Content Recommendation (Netflix-Style)

**Your system:** Given a movie a user watched, recommend similar movies.

**Retrieval flow:**
```
User watched: "Inception" (movie_id: tt1375666)
  ↓
Lookup movie embedding
  ↓
Find nearest neighbor movies in vector space
  ↓
Recommend top 20 similar movies
```

**In Vector Guardrails terms:**
- **Anchor:** `"tt1375666"` (Inception's movie ID)
- **Neighbors:** `["tt0816692", "tt1345836", "tt0482571", ...]` (similar movie IDs)

**Snapshot structure:**
```json
{
  "tt1375666": ["tt0816692", "tt1345836", "tt0482571"],
  "tt0111161": ["tt0068646", "tt0468569", "tt0137523"],
  "tt0468569": ["tt0111161", "tt0137523", "tt1345836"]
}
```

**What you're measuring:** When you retrain your movie embedding model, do recommendations for "Inception" stay consistent?

---

### Example 3: Customer Support RAG System

**Your system:** User asks a question, and you retrieve relevant KB articles to pass to an LLM.

**Retrieval flow:**
```
User asks: "How do I reset my password?"
  ↓
Embed the question
  ↓
Retrieve top 5 KB article chunks
  ↓
Pass chunks to LLM for answer generation
```

**In Vector Guardrails terms:**
- **Anchor:** `"question_password_reset"` (you assign an ID to this question)
- **Neighbors:** `["kb_chunk_42", "kb_chunk_103", "kb_chunk_299", ...]` (retrieved KB chunks)

**Snapshot structure:**
```json
{
  "question_password_reset": ["kb_chunk_42", "kb_chunk_103", "kb_chunk_299"],
  "question_billing_issue": ["kb_chunk_501", "kb_chunk_88", "kb_chunk_210"],
  "question_account_delete": ["kb_chunk_777", "kb_chunk_12", "kb_chunk_443"]
}
```

**What you're measuring:** When you update your KB or embedding model, does "How do I reset my password?" still retrieve the right articles?

---

## Common Confusion Points

### "Why not just call them queries and results?"

Because not all retrieval is query-based:

- In item-to-item recommendations, there's no "query"—you're finding similar items
- In user-based recommendations, the "query" is a user profile, not text
- In image similarity, the "query" is an image, not text

The terms **anchor** and **neighbor** work for all these cases.

---

### "What if my system uses both queries and items?"

Example: A hybrid search system where users can search by text OR by clicking "find similar" on an item.

**Solution:** Treat them as separate snapshots or prefix your anchor IDs:

```json
{
  "query:wireless_headphones": ["prod_1001", "prod_2034"],
  "item:prod_1001": ["prod_2034", "prod_5678"]
}
```

This works fine—Vector Guardrails just compares IDs as strings.

---

### "Can an anchor also be a neighbor?"

Yes, and this is common in recommendation systems.

Example: In item-to-item recommendations, `product_A` can be an anchor (seed item) in one entry and a neighbor (recommended item) in another.

```json
{
  "product_A": ["product_B", "product_C"],
  "product_B": ["product_A", "product_D"]
}
```

This is fine. Anchors and neighbors are just roles in a specific snapshot entry.

---

### "What if my neighbors aren't ordered?"

Vector Guardrails assumes **order matters**—the first neighbor is most relevant, the second is next-most relevant, etc.

If your retrieval system returns unordered sets (e.g., all equally relevant), you have two options:

1. **Impose an order** (e.g., alphabetical, by ID) consistently across snapshots
2. **Use a different tool**—Vector Guardrails isn't designed for unordered set comparison

---

### "How many anchors do I need?"

**Minimum:** 10–20 for a smoke test
**Recommended:** 50–200 for meaningful signal
**Maximum:** Thousands work fine, but comparisons get slower

**Quality > quantity:** 100 well-chosen anchors (representing real usage) are better than 10,000 random anchors.

---

## Terminology in the Report Output

When you run a comparison, the report uses these terms:

```
ANCHOR ALIGNMENT:
  Compared: 50 anchors present in both snapshots
  Baseline only: 5 anchors
  Candidate only: 3 anchors
  Jaccard similarity: 0.86 (86% anchor set overlap)
```

**What this means:**
- **Compared anchors:** 50 anchor IDs appeared in both baseline and candidate snapshots
- **Baseline only:** 5 anchor IDs only appeared in the baseline (missing in candidate)
- **Candidate only:** 3 anchor IDs only appeared in the candidate (missing in baseline)
- **Jaccard similarity:** How much overlap there is in anchor sets (1.0 = perfect match)

---

```
RETRIEVAL METRICS:
  Mean Overlap@10: 0.73 (73%)
    → Average fraction of neighbors that remained in top-10
```

**What this means:**
- On average, 73% of the top-10 neighbors in the baseline also appeared in the top-10 neighbors of the candidate
- For each anchor, we computed overlap, then averaged across all anchors

---

```
RISK BREAKDOWN:
  CRITICAL: 2 anchors (overlap < 0.50)
  WARNING:  8 anchors (overlap < 0.70)
  SAFE:     40 anchors
```

**What this means:**
- 2 anchors had very low overlap (< 50%)—their neighbors changed drastically
- 8 anchors had moderate overlap (50–70%)—significant but not catastrophic change
- 40 anchors had high overlap (≥ 70%)—stable results

---

## Quick Reference

**Need to know:**
- **Anchor** = What you input to retrieval
- **Neighbor** = What retrieval returns
- **Snapshot** = A JSON file mapping anchors → neighbors

**For your use case:**
1. Find your use case in the table above
2. Identify what your "anchor" and "neighbors" are
3. Generate a snapshot following that pattern

**Still confused?** See [generating-snapshots.md](./generating-snapshots.md) for code examples.

---

## Summary

| Term | Meaning | Example |
|------|---------|---------|
| **Anchor** | Input to your retrieval system | Query ID, item ID, user ID |
| **Neighbor** | Output from your retrieval system | Document ID, product ID, recommendation |
| **Snapshot** | JSON mapping anchors → neighbors | `{"anchor_1": ["neighbor_a", "neighbor_b"]}` |
| **Overlap** | Fraction of neighbors in common between baseline and candidate | `0.80` = 80% of neighbors stayed the same |
| **Churn** | Fraction of anchors with low overlap | `0.25` = 25% of anchors had significant drift |
| **Jaccard** | Similarity of anchor ID sets | `0.95` = 95% of anchors appeared in both snapshots |

The terminology is intentionally abstract to work across search, recommendations, RAG, and other retrieval use cases. Once you map it to your domain, it should be intuitive.
