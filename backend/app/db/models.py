from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship

from .base import Base


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    source = Column(String)
    title = Column(String)
    url = Column(String)
    revision_date = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    chunks = relationship('Chunk', back_populates='document')


class Chunk(Base):
    __tablename__ = 'chunks'
    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, ForeignKey('documents.id'))
    text = Column(Text)
    tokens = Column(Integer)
    section = Column(String)
    position = Column(Integer)
    meta_json = Column(Text)
    document = relationship('Document', back_populates='chunks')


class Interaction(Base):
    __tablename__ = 'interactions'
    id = Column(Integer, primary_key=True)
    query = Column(Text)
    llm_model = Column(String)
    embed_model = Column(String)
    latency_ms = Column(Integer)
    tokens_prompt = Column(Integer)
    tokens_completion = Column(Integer)
    cost_usd = Column(Float)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Citation(Base):
    __tablename__ = 'citations'
    id = Column(Integer, primary_key=True)
    interaction_id = Column(Integer, ForeignKey('interactions.id'))
    chunk_id = Column(Integer, ForeignKey('chunks.id'))
    rank = Column(Integer)
    score = Column(Float)


class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    interaction_id = Column(Integer, ForeignKey('interactions.id'))
    rating = Column(Integer)
    comment = Column(Text)


