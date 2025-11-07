from __future__ import annotations

import json
import tempfile
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, Depends
from pydantic import BaseModel
from sqlalchemy import func

from app.ingest.build_index import build, rebuild_from_database
from app.core.deps import get_db
from app.db.models import Document, Chunk


class IngestRequest(BaseModel):
    paths: list[str]
    max_chunk_tokens: int = 512
    overlap: int = 64


router = APIRouter()


@router.post("/ingest")
async def post_ingest(req: IngestRequest):
    # Process files from paths (adds to database)
    build(req.paths, req.max_chunk_tokens, req.overlap)
    # Rebuild index from ALL documents in database
    rebuild_from_database(req.max_chunk_tokens, req.overlap)
    return {"status": "ok", "message": "Index rebuilt from all documents in database"}


@router.post("/ingest/upload")
async def post_ingest_upload(
    files: list[UploadFile] = File(...),
    max_chunk_tokens: int = Form(512),
    overlap: int = Form(64),
):
    """Upload files and ingest them."""
    # Create temporary directory for uploaded files
    temp_dir = Path(tempfile.mkdtemp(prefix="eka_upload_"))
    file_paths = []
    uploaded_filenames = []
    
    try:
        # Save uploaded files to temp directory in parallel
        import asyncio
        
        async def save_file(file: UploadFile) -> tuple[str, str] | None:
            try:
                filename = file.filename or "unknown"
                lower = filename.lower()
                if not (lower.endswith((".md", ".markdown", ".pdf", ".html", ".htm"))):
                    return None
                
                # Check file size (limit to 50MB per file)
                content = await file.read()
                if len(content) > 50 * 1024 * 1024:  # 50MB limit
                    return None
                
                # Handle duplicate filenames by adding a counter
                file_path = temp_dir / filename
                counter = 1
                while file_path.exists():
                    name_parts = filename.rsplit('.', 1)
                    if len(name_parts) == 2:
                        file_path = temp_dir / f"{name_parts[0]}_{counter}.{name_parts[1]}"
                    else:
                        file_path = temp_dir / f"{filename}_{counter}"
                    counter += 1
                
                file_path.write_bytes(content)
                return (str(file_path), file_path.name)
            except Exception as e:
                # Log error but don't fail entire upload
                print(json.dumps({"error": f"Failed to save file {file.filename}: {str(e)}"}))
                return None
        
        # Process files in parallel (continue even if some fail)
        results = await asyncio.gather(*[save_file(file) for file in files], return_exceptions=True)
        for result in results:
            # Skip exceptions and None results
            if isinstance(result, Exception):
                continue
            if result:
                file_path, filename = result
                file_paths.append(file_path)
                uploaded_filenames.append(filename)
        
        if not file_paths:
            return {"status": "error", "message": "No supported files uploaded"}
        
        # Get document count before processing
        from app.core.deps import SessionLocal
        db_before = SessionLocal()
        doc_count_before = db_before.query(func.count(Document.id)).scalar()
        chunk_count_before = db_before.query(func.count(Chunk.id)).scalar()
        db_before.close()
        
        # Process files through ingest pipeline (adds to database, skips index building)
        from app.ingest.build_index import add_chunks_to_index
        try:
            new_chunk_ids = build(file_paths, max_chunk_tokens, overlap, skip_index=True)
        except Exception as e:
            import traceback
            return {"status": "error", "message": f"Error processing files: {str(e)}", "traceback": traceback.format_exc()}
        
        # Incrementally add only NEW chunks to index (much faster than full rebuild)
        try:
            if new_chunk_ids:
                db_for_index = SessionLocal()
                try:
                    add_chunks_to_index(new_chunk_ids, db_for_index)
                finally:
                    db_for_index.close()
        except Exception as e:
            import traceback
            # If incremental update fails, fall back to full rebuild
            print(json.dumps({"warning": f"Incremental update failed, falling back to full rebuild: {str(e)}"}))
            try:
                rebuild_from_database(max_chunk_tokens, overlap)
            except Exception as rebuild_error:
                return {"status": "error", "message": f"Error updating index: {str(rebuild_error)}", "traceback": traceback.format_exc()}
        
        # Get document count after processing
        db_after = SessionLocal()
        doc_count_after = db_after.query(func.count(Document.id)).scalar()
        chunk_count_after = db_after.query(func.count(Chunk.id)).scalar()
        
        # Get recently added documents (last 10)
        recent_docs = db_after.query(Document).order_by(Document.created_at.desc()).limit(10).all()
        recent_doc_info = [
            {
                "id": doc.id,
                "title": doc.title,
                "source": doc.source,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
            }
            for doc in recent_docs
        ]
        db_after.close()
        
        return {
            "status": "ok",
            "files_processed": len(file_paths),
            "filenames": uploaded_filenames,
            "documents_added": doc_count_after - doc_count_before,
            "chunks_added": chunk_count_after - chunk_count_before,
            "total_documents": doc_count_after,
            "total_chunks": chunk_count_after,
            "recent_documents": recent_doc_info,
        }
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


@router.post("/ingest/rebuild")
async def post_rebuild_index():
    """Rebuild the FAISS index from all documents in the database."""
    try:
        rebuild_from_database()
        return {"status": "ok", "message": "Index rebuilt from all documents in database"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/ingest/status")
async def get_ingest_status(db = Depends(get_db)):
    """Get ingestion status - documents and chunks in database."""
    from sqlalchemy import func
    
    total_docs = db.query(func.count(Document.id)).scalar()
    total_chunks = db.query(func.count(Chunk.id)).scalar()
    
    # Get recent documents
    recent_docs = db.query(Document).order_by(Document.created_at.desc()).limit(20).all()
    documents = [
        {
            "id": doc.id,
            "title": doc.title,
            "source": doc.source,
            "url": doc.url,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "chunk_count": db.query(func.count(Chunk.id)).filter(Chunk.doc_id == doc.id).scalar(),
        }
        for doc in recent_docs
    ]
    
    return {
        "status": "ok",
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "documents": documents,
    }


