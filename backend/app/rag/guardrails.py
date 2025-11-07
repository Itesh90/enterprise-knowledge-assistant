from __future__ import annotations

from typing import List, Dict

from app.core.config import settings


def assess_confidence(results: List[Dict]) -> float:
    if not results:
        return 0.2
    # simple heuristic: average of top-3 scores clipped to [0,1]
    top = [r.get('score', 0.0) for r in results[:3]]
    if not top:
        return 0.3
    avg = sum(top) / len(top)
    # FAISS IP scores generally within [-1,1], map to [0,1]
    conf = max(0.0, min(1.0, (avg + 1.0) / 2.0))
    return conf


def enforce_min_similarity(results: List[Dict]) -> bool:
    if not results:
        return False
    best = results[0].get('score', 0.0)
    # Accept if similarity mapped to [0,1] exceeds threshold
    norm = (best + 1.0) / 2.0
    return norm >= settings.citation_sim_threshold


