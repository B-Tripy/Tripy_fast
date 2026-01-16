from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from olla.review_ollama import review


router = APIRouter(
    prefix="/ai/review",
    tags=["review"],
)
MODEL = "gemma3:1b"
OLLAMA_BASE_URL = "http://localhost:11434"

class ReviewRequest(BaseModel):
    post: str
    tripId: str

@router.post("")
async def review_end(request: ReviewRequest):
    print(request.post)
    result = await review(request.post)

    # db에 저장하는 함수 호출할 예정(post, tripId)
    return result

