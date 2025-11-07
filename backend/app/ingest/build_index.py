from __future__ import annotations

import argparse
import faiss  # type: ignore
import json
from pathlib import Path
from typing import List

import numpy as np

from app.core.config import settings
from app.core.deps import SessionLocal, init_db
from app.db.crud import get_or_create_document, create_chunk
from app.db.models import Chunk, Document
from .loaders import iter_documents
from .clean import normalize_text
from .chunk import iter_chunk_records
from .embed import BGEEmbedder


def build(paths: list[str], max_chunk_tokens: int, overlap: int, skip_index: bool = False) -> List[int]:
    init_db()
    db = SessionLocal()
    
    # Collect documents from both files and directories
    docs: List[dict] = []
    for path_str in paths:
        path = Path(path_str)
        if path.is_file():
            # Single file - use load_file_from_path
            from .loaders import load_file_from_path
            doc = load_file_from_path(path)
            if doc:
                # For uploaded files, use filename as source instead of temp path
                path_lower = path_str.lower()
                if ("eka_upload_" in path_lower or 
                    path_str.startswith("/tmp") or 
                    "\\temp\\" in path_lower or
                    "appdata\\local\\temp" in path_lower):
                    # Use filename as both source and ensure title is clean
                    doc["source"] = f"uploaded:{path.name}"
                    doc["title"] = path.stem  # Ensure title is filename without extension
                docs.append(doc)
        elif path.is_dir():
            # Directory - use iter_documents
            docs.extend(list(iter_documents([path_str])))
        else:
            # Try as file path even if it doesn't exist yet
            from .loaders import load_file_from_path
            doc = load_file_from_path(path)
            if doc:
                path_lower = path_str.lower()
                if ("eka_upload_" in path_lower or 
                    path_str.startswith("/tmp") or 
                    "\\temp\\" in path_lower or
                    "appdata\\local\\temp" in path_lower):
                    doc["source"] = f"uploaded:{path.name}"
                    doc["title"] = path.stem  # Ensure title is filename without extension
                docs.append(doc)
    
    total_chunks = 0
    chunk_texts: List[str] = []
    metas: List[dict] = []
    new_chunk_ids: List[int] = []  # Collect all new chunk IDs across all documents

    # Batch process all documents for better performance
    try:
        for d in docs:
            d["text"] = normalize_text(d["text"])  # type: ignore[index]
            doc_row = get_or_create_document(db, source=d.get("source", ""), title=d.get("title", ""), url=d.get("url", ""))
            
            # Delete existing chunks for this document to avoid duplicates
            from app.db.models import Chunk
            deleted_count = db.query(Chunk).filter(Chunk.doc_id == doc_row.id).delete()
            if deleted_count > 0:
                db.flush()  # Flush delete before adding new chunks
            
            # Collect all chunks for this document
            doc_chunks = []
            for ch in iter_chunk_records(d, max_chunk_tokens, overlap):
                chunk_texts.append(ch["text"])  # type: ignore[index]
                preview = ch["text"][:700]
                meta_with_id = {**ch["meta"], "text": preview}
                metas.append(meta_with_id)  # type: ignore[index]
                
                # Create chunk object (not yet committed)
                chunk_obj = Chunk(
                    doc_id=doc_row.id,
                    text=ch["text"],
                    tokens=ch["tokens"],
                    section=ch["section"],
                    position=ch["position"],
                    meta_json=json.dumps(ch["meta"]),
                )
                doc_chunks.append((chunk_obj, meta_with_id))
                total_chunks += 1
            
            # Bulk insert all chunks for this document
            if doc_chunks:
                for chunk_obj, meta_with_id in doc_chunks:
                    db.add(chunk_obj)
                db.flush()  # Get IDs without committing
                
                # Update meta with chunk IDs and collect IDs for incremental update
                for (chunk_obj, meta_with_id), idx in zip(doc_chunks, range(len(doc_chunks))):
                    meta_idx = len(metas) - len(doc_chunks) + idx
                    metas[meta_idx]["chunk_id"] = chunk_obj.id
                    new_chunk_ids.append(chunk_obj.id)
        
        # Single commit for all documents and chunks
        db.commit()
    except Exception as e:
        db.rollback()  # Rollback on error
        raise

    print(json.dumps({"docs": len(docs), "chunks": total_chunks}))

    if skip_index:
        # Only add to database, don't build index (will be updated incrementally)
        db.close()
        return new_chunk_ids

    if not chunk_texts:
        print(json.dumps({"status": "error", "message": "No chunks to embed"}))
        db.close()
        return []

    embedder = BGEEmbedder(settings.embedding_model)
    embs = embedder.encode(chunk_texts)
    
    # Ensure embs is 2D array
    if len(embs.shape) == 1:
        embs = embs.reshape(1, -1)
    
    if embs.shape[0] == 0:
        print(json.dumps({"status": "error", "message": "Empty embeddings array"}))
        db.close()
        return
        
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    # vectors already normalized
    index.add(embs)

    out_index = Path(settings.index_path)
    out_index.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out_index))

    meta_path = Path(settings.doc_meta_path)
    with meta_path.open("w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m) + "\n")

    print(json.dumps({"status": "ok", "index_path": str(out_index), "meta_path": str(meta_path)}))
    db.close()
    return []  # Return empty list when building full index


def add_chunks_to_index(chunk_ids: List[int], db) -> None:
    """Incrementally add new chunks to existing FAISS index (much faster than full rebuild)."""
    from app.db.models import Chunk
    
    if not chunk_ids:
        return
    
    # Get chunks from database
    chunks = db.query(Chunk).join(Document).filter(Chunk.id.in_(chunk_ids)).all()
    if not chunks:
        return
    
    chunk_texts: List[str] = []
    metas: List[dict] = []
    
    for chunk in chunks:
        chunk_texts.append(chunk.text)
        metas.append({
            "title": chunk.document.title or "",
            "source": chunk.document.source or "",
            "url": chunk.document.url or "",
            "section": chunk.section or "",
            "position": chunk.position or 0,
            "chunk_id": chunk.id,
            "text": chunk.text[:700] if chunk.text else "",
        })
    
    # Generate embeddings only for new chunks
    embedder = BGEEmbedder(settings.embedding_model)
    embs = embedder.encode(chunk_texts)
    
    if len(embs.shape) == 1:
        embs = embs.reshape(1, -1)
    
    if embs.shape[0] == 0:
        return
    
    # Load existing index
    index_path = Path(settings.index_path)
    meta_path = Path(settings.doc_meta_path)
    
    if not index_path.exists() or not meta_path.exists():
        # No existing index, create new one
        dim = embs.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embs)
        faiss.write_index(index, str(index_path))
        
        with meta_path.open("w", encoding="utf-8") as f:
            for m in metas:
                f.write(json.dumps(m) + "\n")
    else:
        # Add to existing index
        index = faiss.read_index(str(index_path))
        index.add(embs)
        faiss.write_index(index, str(index_path))
        
        # Append to metadata file
        with meta_path.open("a", encoding="utf-8") as f:
            for m in metas:
                f.write(json.dumps(m) + "\n")
    
    print(json.dumps({"status": "incremental_update", "chunks_added": len(chunks)}))


def rebuild_from_database(max_chunk_tokens: int = 512, overlap: int = 64) -> None:
    """Rebuild FAISS index from all chunks in the database."""
    init_db()
    db = SessionLocal()
    
    try:
        # Get all chunks from database with optimized query (eager loading)
        chunks = db.query(Chunk).join(Document).order_by(Chunk.id).all()
        
        if not chunks:
            print(json.dumps({"status": "error", "message": "No chunks found in database"}))
            return
        
        # Pre-allocate lists for better performance (Python lists grow dynamically, but we know the size)
        chunk_texts: List[str] = []
        metas: List[dict] = []
        
        # Process chunks in a single pass
        for chunk in chunks:
            chunk_texts.append(chunk.text)
            # Reconstruct meta from chunk data
            metas.append({
                "title": chunk.document.title or "",
                "source": chunk.document.source or "",
                "url": chunk.document.url or "",
                "section": chunk.section or "",
                "position": chunk.position or 0,
                "chunk_id": chunk.id,
                "text": chunk.text[:700] if chunk.text else "",  # Preview for UI
            })
        
        print(json.dumps({"chunks_from_db": len(chunks)}))
        
        if not chunk_texts:
            print(json.dumps({"status": "error", "message": "No chunks to embed"}))
            return
        
        # Generate embeddings with optimized batch processing
        embedder = BGEEmbedder(settings.embedding_model)
        embs = embedder.encode(chunk_texts)
        
        # Ensure embs is 2D array
        if len(embs.shape) == 1:
            embs = embs.reshape(1, -1)
        
        if embs.shape[0] == 0:
            print(json.dumps({"status": "error", "message": "Empty embeddings array"}))
            return
            
        dim = embs.shape[1]
        index = faiss.IndexFlatIP(dim)
        # vectors already normalized - add all at once
        index.add(embs)

        out_index = Path(settings.index_path)
        out_index.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(out_index))

        # Write metadata file efficiently
        meta_path = Path(settings.doc_meta_path)
        with meta_path.open("w", encoding="utf-8") as f:
            for m in metas:
                f.write(json.dumps(m) + "\n")

        print(json.dumps({"status": "ok", "index_path": str(out_index), "meta_path": str(meta_path), "total_chunks": len(chunks)}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Error rebuilding index: {str(e)}"}))
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="+", required=True)
    parser.add_argument("--max-chunk-tokens", type=int, default=512)
    parser.add_argument("--overlap", type=int, default=64)
    args = parser.parse_args()
    build(args.paths, args.max_chunk_tokens, args.overlap)


if __name__ == "__main__":
    main()


