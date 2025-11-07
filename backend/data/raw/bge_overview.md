# BGE Embeddings

The BAAI BGE (BAAI General Embedding) family provides strong general-purpose embeddings.
The model "BAAI/bge-large-en-v1.5" is recommended with normalized embeddings.

## Model Details

- **Model**: BAAI/bge-large-en-v1.5
- **Dimensions**: 1024
- **Normalization**: L2 normalization recommended for cosine similarity
- **Usage**: Sentence-level embeddings via SentenceTransformers library

## Normalization

When using normalized embeddings, inner product (dot product) equals cosine similarity.
This allows efficient similarity search in FAISS using IndexFlatIP.

## Best Practices

- Normalize embeddings: `normalize_embeddings=True` in SentenceTransformers
- Batch encoding for efficiency
- Consistent normalization across query and document embeddings

