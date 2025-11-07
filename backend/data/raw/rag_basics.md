# Retrieval-Augmented Generation (RAG)

RAG systems retrieve relevant context and then generate answers grounded in that context.
This approach combines the benefits of dense retrieval with large language model generation.

## RAG Pipeline

1. **Ingestion**: Documents are loaded, cleaned, and chunked into smaller pieces
2. **Embedding**: Chunks are embedded using a sentence transformer model (e.g., BGE)
3. **Indexing**: Embeddings are stored in a vector database (e.g., FAISS)
4. **Retrieval**: User queries are embedded and matched against the index
5. **Reranking** (optional): Retrieved chunks are reranked using a cross-encoder
6. **Generation**: Top chunks are passed to an LLM as context for answer generation

## Best Practices

- High-quality chunking: Preserve semantic boundaries, maintain overlap between chunks
- Metadata preservation: Store source, title, section, URL, position for citation
- Normalized embeddings: Use normalized embeddings for cosine similarity
- Context packing: Deduplicate and enforce token budgets when constructing prompts

