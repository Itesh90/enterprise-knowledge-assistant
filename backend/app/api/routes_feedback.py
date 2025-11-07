from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.db.crud import create_feedback


class FeedbackRequest(BaseModel):
    interaction_id: str
    rating: int
    comment: str | None = None


router = APIRouter()


@router.post("/feedback")
async def post_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    create_feedback(db, int(req.interaction_id), req.rating, req.comment)
    db.commit()
    return {"status": "ok"}


