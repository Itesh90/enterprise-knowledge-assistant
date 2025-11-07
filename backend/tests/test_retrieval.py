from app.ingest.build_index import build
from app.rag.vector_store import FaissStore


def test_build_and_search():
    build(["data/raw"], max_chunk_tokens=256, overlap=32)
    store = FaissStore()
    hits = store.search("What is RAG?", 10)
    assert len(hits) > 0

