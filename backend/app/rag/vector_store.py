from __future__ import annotations

import faiss  # type: ignore
import json
from pathlib import Path
from typing import List, Tuple, Dict

import numpy as np

from app.core.config import settings
from app.ingest.embed import BGEEmbedder


class FaissStore:
    def __init__(self, index_path: str | None = None, meta_path: str | None = None) -> None:
        self.index_path = Path(index_path or settings.index_path)
        self.meta_path = Path(meta_path or settings.doc_meta_path)
        
        # Check if index exists
        if not self.index_path.exists():
            raise FileNotFoundError(f"FAISS index not found at {self.index_path}. Please ingest documents first.")
        if not self.meta_path.exists():
            raise FileNotFoundError(f"Meta file not found at {self.meta_path}. Please ingest documents first.")
        
        self.index = faiss.read_index(str(self.index_path))
        
        # Load metadata
        meta_lines = self.meta_path.read_text(encoding="utf-8").strip().splitlines()
        self.metas: List[Dict] = []
        for line in meta_lines:
            if line.strip():
                try:
                    self.metas.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        if not self.metas:
            raise ValueError(f"No metadata found in {self.meta_path}")
        
        self.embedder = BGEEmbedder(settings.embedding_model)

    def search(self, query: str, k: int = 20) -> List[Tuple[int, float]]:
        q = self.embedder.encode([query])  # already normalized
        D, I = self.index.search(q, k)
        return [(int(idx), float(score)) for idx, score in zip(I[0], D[0]) if idx != -1]

    def get_meta(self, idx: int) -> Dict:
        return self.metas[idx]


