from __future__ import annotations

from typing import List, Dict

from sentence_transformers import CrossEncoder

from app.core.config import settings


_cross_encoder: CrossEncoder | None = None


def get_cross_encoder() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        _cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    return _cross_encoder


def rerank(query: str, results: List[Dict], top_k: int) -> List[Dict]:
    if not results:
        return results
    model = get_cross_encoder()
    pairs = [(query, r.get('title', '') + ' ' + r.get('section', '')) for r in results]
    scores = model.predict(pairs)
    rescored = [({**r}, float(s)) for r, s in zip(results, scores)]
    rescored.sort(key=lambda x: x[1], reverse=True)
    out = []
    for rank, (r, s) in enumerate(rescored[:top_k], start=1):
        r['score'] = float(s)
        r['rank'] = rank
        out.append(r)
    return out


