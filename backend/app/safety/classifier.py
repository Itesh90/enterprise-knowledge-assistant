from __future__ import annotations

from typing import Literal


def classify(query: str) -> Literal['safe', 'off_topic', 'unsafe']:
    q = query.lower()
    # Extremely simple heuristic baseline
    unsafe_terms = [
        'how to make a bomb', 'harm', 'self-harm', 'suicide', 'kill', 'explosive'
    ]
    if any(t in q for t in unsafe_terms):
        return 'unsafe'
    return 'safe'


