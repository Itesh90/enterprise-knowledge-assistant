from __future__ import annotations

import json
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .routes_query import router as query_router
from .routes_ingest import router as ingest_router
from .routes_feedback import router as feedback_router
from app.core.deps import init_db
from app.core.rate_limit import RateLimitMiddleware
from app.core.config import settings


app = FastAPI(title="Enterprise Knowledge Assistant")

origins = ["http://localhost:3000", "http://localhost:3001"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.middleware("http")
async def json_logger(request: Request, call_next):
    t0 = time.time()
    response = await call_next(request)
    latency_ms = int((time.time() - t0) * 1000)
    print(
        json.dumps(
            {
                "message": "request",
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
            }
        )
    )
    return response


app.include_router(query_router)
app.include_router(ingest_router)
app.include_router(feedback_router)


@app.on_event("startup")
async def on_startup():
    init_db()
    # Diagnostic: Check if Gemini API key is loaded
    import os
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
    if api_key:
        print(json.dumps({
            "message": "startup",
            "gemini_api_key_loaded": True,
            "model": settings.llm_model,
            "note": "API key found, generation enabled"
        }))
    else:
        print(json.dumps({
            "message": "startup",
            "gemini_api_key_loaded": False,
            "model": settings.llm_model,
            "warning": "No GEMINI_API_KEY found. Add GEMINI_API_KEY=your-key to backend/.env and restart."
        }))


