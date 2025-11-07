from __future__ import annotations

from typing import List, Dict


def get_fewshots() -> List[Dict[str, str]]:
    # Lightweight few-shots derived from seed docs
    return [
        {
            "q": "What is RAG?",
            "a": "Retrieval-augmented generation retrieves relevant context and then generates an answer grounded in that context [1].",
        },
        {
            "q": "Which embedding model is recommended?",
            "a": "BAAI/bge-large-en-v1.5 with normalized embeddings is recommended [2].",
        },
        {
            "q": "What is FAISS used for?",
            "a": "FAISS enables efficient similarity search over dense vectors and can persist indices locally [3].",
        },
    ]


