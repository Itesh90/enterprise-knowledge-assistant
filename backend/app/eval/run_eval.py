from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Dict

from app.rag.vector_store import FaissStore
from app.ingest.build_index import build as build_index
from app.eval.metrics import recall_at_k, ndcg_at_k, mrr_at_k


def ensure_index() -> None:
    # Assumes seed docs exist
    try:
        store = FaissStore()
        _ = store.index.ntotal  # noqa: F841
    except Exception:
        build_index(["backend/data/raw"], 512, 64)


def evaluate(k: int) -> Dict:
    ensure_index()
    store = FaissStore()
    golden_path = Path("backend/app/eval/golden.jsonl")
    lines = [json.loads(l) for l in golden_path.read_text(encoding="utf-8").splitlines()]
    rows: List[Dict] = []
    recall_scores: List[float] = []
    ndcg_scores: List[float] = []
    mrr_scores: List[float] = []
    for item in lines:
        query = item["query"]
        gt_titles = item["doc_titles"]
        hits = store.search(query, k)
        titles = [store.get_meta(idx).get("title", "") for idx, _ in hits]
        r = recall_at_k(gt_titles, titles, k)
        recall_scores.append(r)
        nd = ndcg_at_k(gt_titles, titles, k)
        ndcg_scores.append(nd)
        mr = mrr_at_k(gt_titles, titles, k)
        mrr_scores.append(mr)
        rows.append({"query": query, "recall@k": r, "nDCG@k": nd, "MRR@k": mr})
    report = {
        "k": k,
        "recall@k": sum(recall_scores) / len(recall_scores),
        "nDCG@k": sum(ndcg_scores) / len(ndcg_scores),
        "MRR@k": sum(mrr_scores) / len(mrr_scores),
        "rows": rows,
    }
    out = Path("backend/app/eval/last_report.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=20)
    args = parser.parse_args()
    evaluate(args.k)


if __name__ == "__main__":
    main()


