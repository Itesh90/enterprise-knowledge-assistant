from fastapi.testclient import TestClient
from app.api.main import app
from app.ingest.build_index import build


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_ingest_and_query_and_feedback():
    build(["data/raw"], 256, 32)
    # ingest endpoint
    r = client.post("/ingest", json={"paths": ["data/raw"], "max_chunk_tokens": 256, "overlap": 32})
    assert r.status_code == 200
    # query endpoint
    q = client.post("/query", json={"query": "What is RAG?", "top_k": 10, "k_final": 3})
    assert q.status_code == 200
    data = q.json()
    assert "answer" in data
    assert "snippets" in data
    # feedback endpoint
    fb = client.post("/feedback", json={"interaction_id": 1, "rating": 1, "comment": "ok"})
    assert fb.status_code == 200


