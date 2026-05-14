# Vector Databases: pgvector

## What is a Vector Database?

A **vector database** stores and searches high-dimensional vectors (like face embeddings) by similarity.

### Traditional Database vs Vector Database

| Feature | Regular DB | Vector DB |
|---------|-----------|-----------|
| Query type | Exact match | Similarity match |
| Example query | `WHERE name = 'John'` | Find 5 most similar faces |
| Index type | B-tree | IVFFlat, HNSW, LSH |
| Usefulness | Precise data | Fuzzy/semantic search |

## pgvector: PostgreSQL Extension

**pgvector** adds vector support to PostgreSQL without needing a separate database.

### Advantages
- ✅ No new database to learn
- ✅ Works with existing PostgreSQL knowledge
- ✅ Seamless integration with relational data
- ✅ ACID transactions
- ✅ Full SQL support

### How It Works

1. **New Data Type**: `VECTOR(N)` for N-dimensional vectors
2. **Distance Operators**: `<->`, `<#>`, `<=>` for different metrics
3. **Indexes**: IVFFlat and HNSW for fast search
4. **SQL Integration**: Works with standard SQL queries

## Vector Data Type

### Declaring Vector Columns

```sql
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    embedding VECTOR(512)  -- 512-dimensional vector
);
```

### Inserting Vectors

```python
# In Python
embedding = np.array([0.23, -0.45, 0.67, ...])  # 512 numbers
embedding_list = embedding.tolist()

cursor.execute(
    "INSERT INTO embeddings (user_id, embedding) VALUES (%s, %s)",
    (user_id, embedding_list)
)
```

## Distance Metrics

### Cosine Similarity (`<=>`)

- Measures angle between vectors
- **Best for**: Face embeddings (our use case!)
- **Range**: 0 (opposite) to 1 (identical)
- **Distance** = 1 - similarity

```sql
SELECT 1 - (embedding <=> query_vector) as similarity
FROM embeddings
ORDER BY embedding <=> query_vector  -- Distance
LIMIT 1
```

### L2 Distance (`<->`)

- Euclidean distance
- **Best for**: Dense numerical data
- **Slower** than cosine for normalized vectors

```sql
SELECT 1 / (1 + (embedding <-> query_vector)) as similarity
FROM embeddings
```

### Inner Product (`<#>`)

- Dot product of vectors
- **Best for**: Fast approximate search
- **Fastest** but less intuitive

```sql
SELECT embedding <#> query_vector as dot_product
FROM embeddings
```

## Vector Indexing

### Why Index?

Without index: Check every vector (O(N)) - slow!
With index: Skip dissimilar vectors (O(log N)) - fast!

### IVFFlat Index

**IVFFlat** = Inverted File with Flat (product) quantization

```sql
CREATE INDEX idx_embedding
ON embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**How it works**:
1. Divides all vectors into 100 clusters (lists)
2. For query, finds closest clusters first
3. Only searches vectors in nearby clusters

**Trade-offs**:
- `lists` = 100: Fast but approximate
- `lists` = 1000: More accurate but slower
- Typical: 1/sqrt(N) where N = number of vectors

### HNSW Index

**HNSW** = Hierarchical Navigable Small World

```sql
CREATE INDEX idx_embedding_hnsw
ON embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Advantages**:
- ✅ Better recall (finding correct matches)
- ✅ More flexible accuracy/speed trade-off
- ✅ Works for very large datasets (millions+)

**Disadvantages**:
- ❌ Higher memory usage
- ❌ Slower index construction
- ❌ More parameters to tune

## Query Examples

### Find Most Similar

```sql
SELECT user_id, 1 - (embedding <=> query_vector) as similarity
FROM embeddings
ORDER BY embedding <=> query_vector
LIMIT 1;
```

### Find Top-K Similar

```sql
SELECT user_id, 1 - (embedding <=> query_vector) as similarity
FROM embeddings
ORDER BY embedding <=> query_vector
LIMIT 5;
```

### Find Above Threshold

```sql
SELECT user_id, 1 - (embedding <=> query_vector) as similarity
FROM embeddings
WHERE 1 - (embedding <=> query_vector) >= 0.55
ORDER BY embedding <=> query_vector
LIMIT 1;
```

### Batch Search

```sql
-- Find closest match for each query embedding
WITH queries AS (
    SELECT 1 as id, 'query_vector1'::vector as emb UNION
    SELECT 2 as id, 'query_vector2'::vector as emb
)
SELECT q.id, e.user_id, 1 - (e.embedding <=> q.emb) as similarity
FROM queries q
CROSS JOIN LATERAL (
    SELECT user_id, embedding
    FROM embeddings
    ORDER BY embedding <=> q.emb
    LIMIT 1
) e;
```

## Performance

### Index Building

```sql
-- Building IVFFlat index on 1M vectors
CREATE INDEX idx_vector
ON embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);
-- Time: ~30-60 seconds
```

### Query Speed

| Vectors | No Index | IVFFlat | HNSW |
|---------|----------|---------|------|
| 10K | 5ms | 1ms | 1ms |
| 100K | 50ms | 2ms | 2ms |
| 1M | 500ms | 10ms | 5ms |
| 10M | 5000ms | 50ms | 20ms |

### Storage

```
1 vector (512-dim float32): 2KB
1M vectors: 2GB
Index overhead (IVFFlat): ~20%
Index overhead (HNSW): ~40%
```

## Best Practices

### 1. Normalize Vectors

```python
# L2 normalize embeddings
embedding = embedding / np.linalg.norm(embedding)

# Now cosine distance = 1 - dot_product
assert abs(np.linalg.norm(embedding) - 1.0) < 0.001
```

### 2. Index After Loading Data

```sql
-- First, load all data
INSERT INTO embeddings (...) SELECT ...;

-- Then, build index
CREATE INDEX idx_vector 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops);
```

### 3. Tune Lists Parameter

```python
num_vectors = 1000000
num_lists = int(num_vectors ** 0.5)  # ≈ 1000
# Or: num_lists = 50 to 1000 depending on accuracy needs
```

### 4. Monitor Query Plans

```sql
EXPLAIN ANALYZE
SELECT user_id, 1 - (embedding <=> query_vector) as sim
FROM embeddings
ORDER BY embedding <=> query_vector
LIMIT 1;

-- Output should show: "Index Scan using idx_vector"
-- If not, index isn't being used - check the <=> operator matches index type
```

## Troubleshooting

### ❌ Queries are slow

Check if index is being used:
```sql
EXPLAIN SELECT ... ORDER BY embedding <=> query LIMIT 1;
```

If not using index, rebuild it:
```sql
DROP INDEX idx_embedding;
CREATE INDEX idx_embedding ON embeddings USING ivfflat (embedding vector_cosine_ops);
```

### ❌ Wrong results returned

Increase `lists`:
```sql
DROP INDEX idx_embedding;
CREATE INDEX idx_embedding ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1000);
```

### ❌ Index takes too long to build

Use HNSW instead:
```sql
CREATE INDEX idx_embedding ON embeddings USING hnsw (embedding vector_cosine_ops);
```

## Next Steps

1. ➡️ See [database/operations.py](../../database/operations.py) for Python examples
2. ➡️ Run `02_pgvector_tutorial.ipynb` for hands-on experience
3. ➡️ Experiment with different `lists` values
4. ➡️ Monitor performance with production data
