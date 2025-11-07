from __future__ import annotations

from typing import List, Dict

from .vector_store import FaissStore
from .scoring import rerank
from app.core.config import settings
from app.core.deps import SessionLocal
from app.db.models import Chunk


def _expand_query_with_titles(store: FaissStore, query: str, hits: List[tuple[int, float]], num_titles: int = 3) -> str:
    titles: List[str] = []
    for idx, _ in hits[:num_titles]:
        meta = store.get_meta(idx)
        t = meta.get('title')
        if t:
            titles.append(t)
    if not titles:
        return query
    return query + " " + " ".join(set(titles))


def retrieve(query: str, k: int = 20, k_final: int = 5) -> List[Dict]:
    store = FaissStore()
    hits = store.search(query, k)
    if settings.enable_query_expansion and hits:
        expanded = _expand_query_with_titles(store, query, hits)
        hits = store.search(expanded, k)
    
    # Batch fetch full text from database for better performance
    db = SessionLocal()
    
    # Collect all chunk IDs first
    chunk_ids_to_fetch = []
    meta_list = []
    for rank, (idx, score) in enumerate(hits[:k_final], start=1):
        meta = store.get_meta(idx)
        chunk_id = meta.get("chunk_id")
        if chunk_id:
            chunk_ids_to_fetch.append(chunk_id)
        meta_list.append((rank, idx, score, meta, chunk_id))
    
    # Batch fetch all chunks in one query
    chunk_text_map = {}
    if chunk_ids_to_fetch:
        chunks = db.query(Chunk).filter(Chunk.id.in_(chunk_ids_to_fetch)).all()
        chunk_text_map = {chunk.id: chunk.text for chunk in chunks if chunk.text}
    
    db.close()
    
    # Optional reranker can be added later; for now take top k_final
    results: List[Dict] = []
    for rank, idx, score, meta, chunk_id in meta_list:
        text = meta.get("text", "")
        
        # Use full text from database if available
        if chunk_id and chunk_id in chunk_text_map:
            text = chunk_text_map[chunk_id]
        
        results.append({
            "rank": rank,
            "score": score,
            "title": meta.get("title", ""),
            "url": meta.get("url", ""),
            "source": meta.get("source", ""),
            "section": meta.get("section", ""),
            "position": meta.get("position", 0),
            "index": idx,
            "chunk_id": chunk_id,
            "text": text,
        })
    
    if settings.enable_reranker and len(hits) > 0:
        # Batch fetch chunks for reranking
        rerank_chunk_ids = []
        rerank_meta_list = []
        for rank, (idx, score) in enumerate(hits, start=1):
            meta = store.get_meta(idx)
            chunk_id = meta.get("chunk_id")
            if chunk_id:
                rerank_chunk_ids.append(chunk_id)
            rerank_meta_list.append((rank, idx, score, meta, chunk_id))
        
        # Batch fetch all chunks for reranking
        rerank_chunk_text_map = {}
        if rerank_chunk_ids:
            rerank_db = SessionLocal()
            rerank_chunks = rerank_db.query(Chunk).filter(Chunk.id.in_(rerank_chunk_ids)).all()
            rerank_chunk_text_map = {chunk.id: chunk.text for chunk in rerank_chunks if chunk.text}
            rerank_db.close()
        
        # prepare pre-results from full k, then rerank and cut to k_final
        pre: List[Dict] = []
        for rank, idx, score, meta, chunk_id in rerank_meta_list:
            text = meta.get("text", "")
            
            # Use full text from database if available
            if chunk_id and chunk_id in rerank_chunk_text_map:
                text = rerank_chunk_text_map[chunk_id]
            
            pre.append({
                "rank": rank,
                "score": score,
                "title": meta.get("title", ""),
                "url": meta.get("url", ""),
                "source": meta.get("source", ""),
                "section": meta.get("section", ""),
                "position": meta.get("position", 0),
                "index": idx,
                "chunk_id": chunk_id,
                "text": text,
            })
        results = rerank(query, pre, k_final)
    
    return results


