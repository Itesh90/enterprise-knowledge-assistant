# Backend - Enterprise Knowledge Assistant

FastAPI backend with FAISS + BGE embeddings, SQLite persistence, and evaluation harness.

## Quick Start

```bash
# 1. Setup
cp .env.example .env
# Edit .env and add OPENAI_API_KEY (optional)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Build index from seed data
python -m app.ingest.build_index --paths backend/data/raw --max-chunk-tokens 512 --overlap 64

# 4. Run server
uvicorn app.api.main:app --reload --port 8000
```

## Structure

- `app/api/` - FastAPI routes (main, query, ingest, feedback)
- `app/core/` - Config, logging, dependencies, rate limiting
- `app/db/` - SQLAlchemy models and CRUD
- `app/ingest/` - Loaders, cleaner, chunker, embedder, index builder
- `app/rag/` - Vector store, retriever, prompt builder, generator, guardrails, scoring
- `app/safety/` - Safety classifier
- `app/eval/` - Evaluation harness with golden set
- `data/raw/` - Seed documents (markdown/PDF/HTML)
- `data/indices/` - FAISS index and meta JSONL
- `tests/` - Pytest tests

## Environment Variables

See `.env.example` for all options:
- `OPENAI_API_KEY` - Required for generation (or use fallback)
- `EMBEDDING_MODEL` - Default: BAAI/bge-large-en-v1.5
- `LLM_MODEL` - Default: gpt-4.1
- `ENABLE_RERANKER` - Enable cross-encoder reranking
- `ENABLE_QUERY_EXPANSION` - Enable query expansion
- `CITATION_SIM_THRESHOLD` - Minimum similarity threshold (default 0.30)

## CLI Commands

### Build Index
```bash
python -m app.ingest.build_index --paths backend/data/raw --max-chunk-tokens 512 --overlap 64
```

### Run Evaluation
```bash
python -m app.eval.run_eval --k 20
```

### Run Tests
```bash
pytest backend/tests
```

## API Documentation

Once running, visit:
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

