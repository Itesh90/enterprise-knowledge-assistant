from __future__ import annotations

import json
from typing import Optional

from sqlalchemy.orm import Session

from .models import Document, Chunk, Interaction, Citation, Feedback


def get_or_create_document(db: Session, source: str, title: str, url: str = "", revision_date: str = "") -> Document:
    doc = db.query(Document).filter(Document.source == source, Document.title == title).first()
    if doc:
        return doc
    doc = Document(source=source, title=title, url=url, revision_date=revision_date)
    db.add(doc)
    db.flush()
    return doc


def create_chunk(
    db: Session,
    doc: Document,
    text: str,
    tokens: int,
    section: str,
    position: int,
    meta: dict,
) -> Chunk:
    ch = Chunk(
        doc_id=doc.id,
        text=text,
        tokens=tokens,
        section=section,
        position=position,
        meta_json=json.dumps(meta),
    )
    db.add(ch)
    db.flush()
    return ch


def create_interaction(
    db: Session,
    query: str,
    llm_model: str,
    embed_model: str,
    latency_ms: int,
    tokens_prompt: int,
    tokens_completion: int,
    cost_usd: float,
    confidence: float,
) -> Interaction:
    it = Interaction(
        query=query,
        llm_model=llm_model,
        embed_model=embed_model,
        latency_ms=latency_ms,
        tokens_prompt=tokens_prompt,
        tokens_completion=tokens_completion,
        cost_usd=cost_usd,
        confidence=confidence,
    )
    db.add(it)
    db.flush()
    return it


def create_citation(db: Session, interaction_id: int, chunk_id: int, rank: int, score: float) -> Citation:
    ct = Citation(interaction_id=interaction_id, chunk_id=chunk_id, rank=rank, score=score)
    db.add(ct)
    db.flush()
    return ct


def create_feedback(db: Session, interaction_id: int, rating: int, comment: Optional[str]) -> Feedback:
    fb = Feedback(interaction_id=interaction_id, rating=rating, comment=comment or "")
    db.add(fb)
    db.flush()
    return fb


