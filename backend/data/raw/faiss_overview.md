# FAISS Vector Store

FAISS (Facebook AI Similarity Search) is a library for efficient similarity search and clustering of dense vectors.
It supports various index types and can store indices locally as files.

## Index Types

- **IndexFlatIP**: Inner product for normalized embeddings (used in EKA)
- **IndexIVFFlat**: Inverted file index for larger datasets
- **IndexHNSW**: Hierarchical navigable small world graph

## Usage in EKA

- Embeddings are normalized (L2 normalized) before indexing
- IndexFlatIP is used for cosine similarity via inner product
- Index and metadata are persisted to `backend/data/indices/`
- Meta JSONL file maintains alignment between vectors and document chunks

## Persistence

- Index: `faiss.index` (binary format)
- Metadata: `meta.jsonl` (one JSON object per line, aligned with index)

