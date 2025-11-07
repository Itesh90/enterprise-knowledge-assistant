from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str | None = None
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    llm_model: str = "gemini-1.5-pro"
    vector_store: str = "faiss"
    index_path: str = "backend/data/indices/faiss.index"
    doc_meta_path: str = "backend/data/indices/meta.jsonl"
    db_url: str = "sqlite:///./eka.db"
    enable_reranker: bool = False
    enable_langfuse: bool = False
    enable_query_expansion: bool = False
    rate_limit_per_minute: int = 60
    citation_sim_threshold: float = 0.30
    citation_coverage_threshold: float = 0.70

    class Config:
        # .env file should be in backend/ directory (where server runs from)
        env_file = ".env"
        case_sensitive = False


settings = Settings()


