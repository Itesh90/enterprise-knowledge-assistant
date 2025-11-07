from __future__ import annotations

from typing import List, Dict, Sequence
import math


def recall_at_k(ground_truth: Sequence[str], retrieved_titles: Sequence[str], k: int) -> float:
    gt = set(t.lower() for t in ground_truth)
    topk = set(t.lower() for t in retrieved_titles[:k])
    return 1.0 if gt & topk else 0.0


def dcg(relevances: Sequence[int]) -> float:
    return sum((rel / math.log2(i + 2)) for i, rel in enumerate(relevances))


def ndcg_at_k(ground_truth: Sequence[str], retrieved_titles: Sequence[str], k: int) -> float:
    gt = [t.lower() for t in ground_truth]
    rels = [1 if t.lower() in gt else 0 for t in retrieved_titles[:k]]
    ideal = sorted(rels, reverse=True)
    idcg = dcg(ideal)
    if idcg == 0:
        return 0.0
    return dcg(rels) / idcg


def mrr_at_k(ground_truth: Sequence[str], retrieved_titles: Sequence[str], k: int) -> float:
    gt = set(t.lower() for t in ground_truth)
    for i, t in enumerate(retrieved_titles[:k], start=1):
        if t.lower() in gt:
            return 1.0 / i
    return 0.0


