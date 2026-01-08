# How to Generate Snapshots

A **snapshot** is a JSON file mapping anchor IDs to their retrieved neighbor IDs. This guide explains how to generate snapshots from your retrieval system.

---

## Snapshot Format Recap

```json
{
  "anchor_1": ["neighbor_a", "neighbor_b", "neighbor_c"],
  "anchor_2": ["neighbor_x", "neighbor_y", "neighbor_z"]
}
```

- **Keys:** Anchor IDs (queries, items, users—depends on your use case)
- **Values:** Ordered lists of neighbor IDs (retrieval results, ranked by relevance)
- **Order matters:** First neighbor is most relevant

---

## General Pattern (Architecture-Agnostic)

Regardless of your vector store or retrieval system, the process is:

1. **Select your anchor set** (queries, items, or users to test)
2. **For each anchor, run retrieval** (query your system for top-K neighbors)
3. **Collect results into a dict** (`anchor_id → [neighbor_ids]`)
4. **Write to JSON**

### Pseudocode

```python
import json

def generate_snapshot(anchors, retrieval_system, k=10, output_path="snapshot.json"):
    """
    Generate a retrieval snapshot.

    Args:
        anchors: List of anchor IDs to query
        retrieval_system: Your retrieval engine (with a .search() method)
        k: Number of neighbors to retrieve per anchor
        output_path: Where to save the snapshot
    """
    snapshot = {}

    for anchor_id in anchors:
        # Query your retrieval system
        results = retrieval_system.search(query=anchor_id, k=k)

        # Extract neighbor IDs (order matters!)
        neighbor_ids = [result.id for result in results]

        snapshot[anchor_id] = neighbor_ids

    # Write to JSON
    with open(output_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"Snapshot saved: {len(snapshot)} anchors, top-{k} neighbors each")
```

---

## Use Case 1: Search Queries

**Scenario:** You have a document search system. Users submit text queries, and you return relevant documents.

**Anchor = Query ID**
**Neighbors = Document IDs**

### Example: Text Search

```python
import json

def generate_search_snapshot(query_set, search_engine, k=10):
    """
    Generate snapshot for text search system.

    Args:
        query_set: Dict mapping query_id → query_text
                   e.g., {"q1": "how to install python", "q2": "best practices for REST APIs"}
        search_engine: Your search system with a .search(query_text, k) method
        k: Number of results to retrieve
    """
    snapshot = {}

    for query_id, query_text in query_set.items():
        # Run the search
        results = search_engine.search(query_text, k=k)

        # Extract document IDs
        doc_ids = [doc.id for doc in results]

        snapshot[query_id] = doc_ids

    with open("snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot

# Example usage
query_set = {
    "q1": "python machine learning tutorial",
    "q2": "vector database comparison",
    "q3": "how to deploy fastapi"
}

snapshot = generate_search_snapshot(query_set, my_search_engine, k=10)
```

### Choosing Your Query Set

**Option 1: Real user queries (recommended)**
- Sample 100–1000 actual queries from production logs
- Ensures anchors reflect real usage patterns
- Captures long-tail and edge cases

**Option 2: Curated test queries**
- Manually craft queries representing key use cases
- Easier to debug and understand
- May miss real-world edge cases

**Option 3: Synthetic queries**
- Generate queries from your document corpus (e.g., extract titles, summaries)
- Useful when you don't have user logs yet
- May not reflect actual user intent

**Recommendation:** Start with 50–200 queries. Too few = unreliable signal, too many = slow comparisons.

---

## Use Case 2: Item-to-Item Recommendations

**Scenario:** "Users who viewed X also viewed Y". Given an item, recommend similar items.

**Anchor = Item ID**
**Neighbors = Recommended Item IDs**

### Example: Product Recommendations

```python
import json

def generate_item_similarity_snapshot(item_ids, recommender, k=10):
    """
    Generate snapshot for item-to-item recommendations.

    Args:
        item_ids: List of item IDs to use as anchors
                  e.g., ["product_123", "product_456", "product_789"]
        recommender: Your recommendation system with a .get_similar_items(item_id, k) method
        k: Number of recommendations per item
    """
    snapshot = {}

    for item_id in item_ids:
        # Get similar items
        similar_items = recommender.get_similar_items(item_id, k=k)

        # Extract item IDs (preserve ranking order)
        similar_item_ids = [item.id for item in similar_items]

        snapshot[item_id] = similar_item_ids

    with open("snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot

# Example usage
# Use popular items as anchors (better coverage than random items)
popular_items = ["product_001", "product_042", "product_099"]

snapshot = generate_item_similarity_snapshot(popular_items, my_recommender, k=20)
```

### Choosing Your Item Anchor Set

**Option 1: Popular items**
- Use top 100–500 items by view count or sales
- These items drive most recommendations
- Changes here have highest user impact

**Option 2: Representative items per category**
- Sample 10–20 items from each product category
- Ensures coverage across the catalog
- Good for detecting category-specific drift

**Option 3: Stratified sample**
- Mix of popular, mid-tier, and long-tail items
- Captures diverse behavior
- More comprehensive but slower

**Recommendation:** Start with popular items (top 200). Expand to stratified sampling if you see category-specific issues.

---

## Use Case 3: User-Based Recommendations

**Scenario:** Personalized recommendations for users based on their profile, history, or embeddings.

**Anchor = User ID**
**Neighbors = Recommended Item IDs**

### Example: Personalized Content Recommendations

```python
import json

def generate_user_recommendation_snapshot(user_ids, recommender, k=10):
    """
    Generate snapshot for user-based recommendations.

    Args:
        user_ids: List of user IDs to use as anchors
                  e.g., ["user_alice", "user_bob", "user_carol"]
        recommender: Your recommendation system with a .get_recommendations(user_id, k) method
        k: Number of recommendations per user
    """
    snapshot = {}

    for user_id in user_ids:
        # Get personalized recommendations
        recommendations = recommender.get_recommendations(user_id, k=k)

        # Extract item IDs
        item_ids = [rec.item_id for rec in recommendations]

        snapshot[user_id] = item_ids

    with open("snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot

# Example usage
# Use test/synthetic users, NOT real user IDs (privacy!)
test_users = ["test_user_new", "test_user_power", "test_user_casual"]

snapshot = generate_user_recommendation_snapshot(test_users, my_recommender, k=15)
```

### Choosing Your User Anchor Set

**⚠️ Privacy warning:** Do NOT use real user IDs in snapshots that will be committed to version control or shared.

**Option 1: Synthetic test users**
- Create fake user profiles with known characteristics
- Safe for version control
- Easier to debug (you know the expected behavior)

**Option 2: Anonymized cohorts**
- Create representative user personas (e.g., "new_user", "power_user", "category_enthusiast")
- Generate synthetic interaction histories
- Reflects real usage patterns without privacy risk

**Option 3: Deterministic test accounts**
- Maintain dedicated test accounts with stable interaction histories
- Useful for regression testing
- Requires upkeep to keep histories relevant

**Recommendation:** Use 20–100 synthetic users spanning different personas. Never use real user IDs.

---

## Best Practices for Snapshot Generation

### 1. Keep Anchor Sets Consistent

**Problem:** If your baseline uses queries A, B, C and your candidate uses queries X, Y, Z, you'll get a low Jaccard warning.

**Solution:** Store your anchor set separately and reuse it:

```python
# Save anchor set
anchor_set = ["query_1", "query_2", "query_3"]
with open("anchor_set.json", "w") as f:
    json.dump(anchor_set, f)

# Later, load and reuse
with open("anchor_set.json", "r") as f:
    anchor_set = json.load(f)

generate_snapshot(anchor_set, retrieval_system, k=10)
```

### 2. Use the Same K Value

**Problem:** Baseline with k=10 vs candidate with k=20 isn't a fair comparison.

**Solution:** Use the same `--k` value when comparing, and generate snapshots with at least that many neighbors.

```python
# Generate with k=20 (more than you'll compare)
generate_snapshot(anchors, system, k=20, output="snapshot.json")

# Compare only top-10
vector-guardrails compare --baseline baseline.json --candidate candidate.json --k 10
```

### 3. Handle Missing Neighbors Gracefully

**Problem:** An anchor might return fewer than K results (small corpus, strict filtering).

**Solution:** Return whatever you have. Vector Guardrails handles variable-length neighbor lists.

```python
# It's okay if some anchors return < k neighbors
results = retrieval_system.search(anchor, k=10)  # Might return 0–10 results
snapshot[anchor] = [r.id for r in results]  # Fine if len < 10
```

### 4. Strip Scores/Metadata

**Snapshot should only contain IDs**, not relevance scores, distances, or metadata.

```python
# ❌ Bad: includes scores
snapshot = {
    "q1": [
        {"id": "doc_a", "score": 0.95},
        {"id": "doc_b", "score": 0.87}
    ]
}

# ✓ Good: IDs only
snapshot = {
    "q1": ["doc_a", "doc_b"]
}
```

### 5. Version Your Snapshots

**Problem:** You generate a snapshot but forget what version of the model/index it came from.

**Solution:** Include metadata in the filename or a companion file:

```bash
# Filename convention
baseline_v1.2.3_2024-01-08.json
candidate_v1.3.0_2024-01-08.json

# Or companion metadata file
snapshot.json
snapshot_metadata.json  # {"model": "v1.2.3", "timestamp": "2024-01-08T10:30:00Z"}
```

---

## Integration Examples

### With FAISS

```python
import faiss
import json
import numpy as np

def generate_snapshot_faiss(index, query_embeddings, query_ids, k=10):
    """
    Generate snapshot from a FAISS index.

    Args:
        index: FAISS index object
        query_embeddings: numpy array of query vectors (n_queries, dimension)
        query_ids: List of query IDs corresponding to embeddings
        k: Number of neighbors to retrieve
    """
    # Search the index
    distances, indices = index.search(query_embeddings, k)

    snapshot = {}
    for i, query_id in enumerate(query_ids):
        # indices[i] contains the neighbor indices for query i
        neighbor_ids = [f"doc_{idx}" for idx in indices[i]]
        snapshot[query_id] = neighbor_ids

    with open("snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot
```

### With Pinecone

```python
import pinecone
import json

def generate_snapshot_pinecone(index, query_vectors, query_ids, k=10):
    """
    Generate snapshot from a Pinecone index.

    Args:
        index: Pinecone index object
        query_vectors: List of query vectors
        query_ids: List of query IDs
        k: Number of neighbors to retrieve
    """
    snapshot = {}

    for query_id, query_vector in zip(query_ids, query_vectors):
        # Query Pinecone
        results = index.query(vector=query_vector, top_k=k)

        # Extract matched IDs
        neighbor_ids = [match.id for match in results.matches]

        snapshot[query_id] = neighbor_ids

    with open("snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot
```

### With Elasticsearch/OpenSearch

```python
from elasticsearch import Elasticsearch
import json

def generate_snapshot_elasticsearch(client, queries, k=10):
    """
    Generate snapshot from Elasticsearch.

    Args:
        client: Elasticsearch client
        queries: Dict mapping query_id → query_text
        k: Number of results to retrieve
    """
    snapshot = {}

    for query_id, query_text in queries.items():
        # Run search
        response = client.search(
            index="documents",
            body={
                "query": {"match": {"content": query_text}},
                "size": k
            }
        )

        # Extract document IDs
        doc_ids = [hit["_id"] for hit in response["hits"]["hits"]]

        snapshot[query_id] = doc_ids

    with open("snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot
```

---

## Common Pitfalls

### ❌ Using Different Anchor Sets

```python
# Baseline
baseline_anchors = get_random_queries(n=100)  # ← Random!
generate_snapshot(baseline_anchors, old_system)

# Candidate
candidate_anchors = get_random_queries(n=100)  # ← Different random set!
generate_snapshot(candidate_anchors, new_system)
```

**Result:** Low anchor Jaccard, WARNING signal, but it's noise.

**Fix:** Use the same anchor set for both snapshots.

---

### ❌ Non-Deterministic Retrieval

```python
# Your retrieval system includes randomness
def search(query, k):
    results = vector_search(query, k=k*2)
    return random.sample(results, k)  # ← Non-deterministic!
```

**Result:** Identical systems produce different snapshots.

**Fix:** Remove randomness, or set a fixed seed for snapshot generation.

---

### ❌ Including Anchors with No Results

```python
snapshot = {}
for anchor in anchors:
    results = retrieval_system.search(anchor, k=10)
    if len(results) == 0:
        snapshot[anchor] = []  # ← Empty list
```

**Result:** These anchors contribute nothing to the comparison (0 overlap is expected).

**Fix:** Either exclude them, or understand they'll dilute your metrics. Not wrong, but may be noisy.

---

## Summary

**To generate a snapshot:**

1. Choose your anchors (queries, items, or users)
2. Query your retrieval system for each anchor
3. Collect results as `{anchor_id: [neighbor_ids]}`
4. Save as JSON

**Key principles:**

- **Consistency:** Use the same anchor set for baseline and candidate
- **Determinism:** Ensure your retrieval is stable (or snapshot multiple times and check)
- **Representativeness:** Anchors should reflect real usage, not random samples
- **Privacy:** Never use real user IDs in snapshots

**Next steps:** See [when-to-use.md](./when-to-use.md) for guidance on when to generate and compare snapshots.
