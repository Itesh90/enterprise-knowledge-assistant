# Enterprise Knowledge Assistant (EKA)

EKA is an enterprise knowledge assistant that uses retrieval-augmented generation (RAG).
It combines a local FAISS index with BGE embeddings to answer questions with citations.
The system is designed for production use with strong error handling and observability.

## Key Features

- FastAPI backend with JSON logging
- FAISS vector store with BGE-large-en-v1.5 embeddings (normalized)
- SQLite persistence for documents, chunks, interactions, and citations
- Optional cross-encoder reranker for improved retrieval
- Safety guardrails and confidence scoring
- Evaluation harness with Recall@k, nDCG@k, and MRR metrics

