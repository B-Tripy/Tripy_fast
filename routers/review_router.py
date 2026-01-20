from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from olla.review_ollama import review
import os


router = APIRouter(
    prefix="/ai/review",
    tags=["review"],
)
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")

class ReviewRequest(BaseModel):
    post: str
    tripId: str
##test
@router.post("")
async def review_end(request: ReviewRequest):
    print(request.post)
    result = await review(request.post)

    # db에 저장하는 함수 호출할 예정(post, tripId)
    return result

