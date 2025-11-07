from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer


class BGEEmbedder:
    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)
        # Enable batch processing for better performance
        self.batch_size = 32  # Process in batches for better GPU/CPU utilization

    def encode(self, texts: list[str]) -> np.ndarray:
        # Use batch processing for large lists
        if len(texts) > self.batch_size:
            vecs = self.model.encode(
                texts, 
                normalize_embeddings=True, 
                show_progress_bar=False,
                batch_size=self.batch_size,
                convert_to_numpy=True
            )
        else:
            vecs = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vecs, dtype=np.float32)