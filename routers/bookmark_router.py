# routers/bookmark_router.py
from fastapi import APIRouter, HTTPException, Body
from db import recommend_mysql

router = APIRouter(prefix="/bookmark", tags=["bookmark"])

# -----------------------------
# 즐겨찾기 추가
# -----------------------------
@router.post("/add")
async def add_bookmark(
    userid: int = Body(...),
    location: str = Body(...),
    description: str = Body(...)
):
    success = await recommend_mysql.add_bookmark(userid, location, description)
    if not success:
        return {"message": "이미 즐겨찾기한 여행지입니다."}
    return {"message": "북마크에 추가되었습니다."}

# -----------------------------
# 즐겨찾기 제거
# -----------------------------
@router.post("/remove")
async def remove_bookmark(
    userid: int = Body(...),
    location: str = Body(...)
):
    success = await recommend_mysql.remove_bookmark(userid, location)
    if not success:
        return {"message": "해당 북마크가 존재하지 않습니다."}
    return {"message": "북마크에서 제거되었습니다."}

# -----------------------------
# 즐겨찾기 목록
# -----------------------------
@router.get("/list")
async def list_bookmarks(userid: int):
    bookmarks = await recommend_mysql.get_bookmarks(userid)
    return {
        "bookmarks": [
            {"location": b.location, "description": b.description}
            for b in bookmarks
        ]
    }
