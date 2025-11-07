from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.rag.retriever import retrieve
from app.rag.prompt_builder import build_prompt
from app.rag.generate import call_gemini_json
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.config import settings
from app.db.crud import create_interaction, create_citation
from app.rag.guardrails import assess_confidence, enforce_min_similarity
from app.safety.classifier import classify


class QueryRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    top_k: int = 20
    k_final: int = 5


router = APIRouter()


@router.post("/query")
async def post_query(req: QueryRequest, db: Session = Depends(get_db)):
    if classify(req.query) == 'unsafe':
        return {
            "answer": "I’m not sure I can help with that.",
            "citations": [],
            "confidence": 0.0,
            "telemetry": {"latency_ms": 0, "tokens_prompt": 0, "tokens_completion": 0, "cost_usd": 0},
            "snippets": [],
        }
    try:
        results = retrieve(req.query, req.top_k, req.k_final)
    except FileNotFoundError as e:
        return {
            "answer": f"I'm not sure. The search index is not available. {str(e)} Please ingest some documents first.",
            "citations": [],
            "confidence": 0.0,
            "telemetry": {"latency_ms": 0, "tokens_prompt": 0, "tokens_completion": 0, "cost_usd": 0},
            "snippets": [],
        }
    
    if not results:
        return {
            "answer": "I'm not sure. I could not find enough relevant context.",
            "citations": [],
            "confidence": 0.2,
            "telemetry": {"latency_ms": 0, "tokens_prompt": 0, "tokens_completion": 0, "cost_usd": 0},
            "snippets": [],
        }
    if not enforce_min_similarity(results):
        return {
            "answer": "I’m not sure. The retrieved context did not meet the similarity threshold.",
            "citations": [],
            "confidence": 0.2,
            "telemetry": {"latency_ms": 0, "tokens_prompt": 0, "tokens_completion": 0, "cost_usd": 0},
            "snippets": results,
        }
    prompt = build_prompt(req.query, results)
    gen = await call_gemini_json(prompt)
    gen["snippets"] = results
    # Update confidence if model didn't provide one
    if "confidence" not in gen or not isinstance(gen["confidence"], (int, float)):
        gen["confidence"] = assess_confidence(results)
    # persist interaction and citations if possible
    telemetry = gen.get("telemetry", {})
    interaction = create_interaction(
        db,
        query=req.query,
        llm_model=settings.llm_model,
        embed_model=settings.embedding_model,
        latency_ms=int(telemetry.get("latency_ms", 0) or 0),
        tokens_prompt=int(telemetry.get("tokens_prompt", 0) or 0),
        tokens_completion=int(telemetry.get("tokens_completion", 0) or 0),
        cost_usd=float(telemetry.get("cost_usd", 0) or 0.0),
        confidence=float(gen.get("confidence", 0.0) or 0.0),
    )
    for r in results:
        chunk_id = r.get("chunk_id")
        if chunk_id:
            create_citation(db, interaction.id, int(chunk_id), int(r.get("rank", 0)), float(r.get("score", 0.0)))
    db.commit()
    return gen


