# routers/recommend_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import ollama
from db import recommend_mysql
import json
import re
import os

router = APIRouter(prefix="/ai", tags=["recommend"])

MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")

# -----------------------------
# 안전한 JSON 파싱
# -----------------------------
def safe_json_parse(raw: str):
    try:
        match = re.search(r"```json(.*?)```", raw, flags=re.DOTALL | re.IGNORECASE)
        json_str = match.group(1).strip() if match else raw.strip()
        return json.loads(json_str)
    except Exception as e:
        print("❌ JSON 파싱 실패:", e)
        print(raw)
        return []

# -----------------------------
# 요청 모델
# -----------------------------
class TravelRequest(BaseModel):
    count: int = 3
    userId: int

# -----------------------------
# 여행 추천 엔드포인트
# -----------------------------
@router.post("/recommend/tour")
async def recommend_travel(req: TravelRequest):
    user_id = req.userId
    client = ollama.AsyncClient()

    # 1️⃣ 유저 여행 조회
    trips = await recommend_mysql.get_user_trips(user_id)
    if not trips:
        raise HTTPException(400, detail="여행 기록 없음")

    print(f"🧳 DB 여행 기록 개수: {len(trips)}")

    # 2️⃣ AI 만족도 평가
    summaries = "\n".join([f"{t.id}. {t.title}: {t.description}" for t in trips])
    sat_prompt = f"""
아래 여행 기록 각각에 대해 만족도를 1, 2, 3, 4, 5 중 하나로 평가하세요.
1에 가까울수록 불만족, 5에 가까울수록 만족입니다.
여행 제목을 새로 만들지 말고, 반드시 제공된 trip_id만 사용하세요.

출력(JSON 배열):
[{{ "trip_id": number, "score": number }}]

[기록]
{summaries}
"""
    sat_res = await client.generate(
        model=MODEL,
        prompt=sat_prompt,
        options={"temperature": 0},
        keep_alive=-1
    )
    satisfaction = safe_json_parse(sat_res.get("response", ""))
    print("📊 AI 만족도 결과:", satisfaction)

    # 3️⃣ DB 업데이트
    await recommend_mysql.update_trip_scores(satisfaction)

    # 4️⃣ 만족 여행 필터
    good_trip_ids = [s["trip_id"] for s in satisfaction if s.get("score", 0) >= 4]
    good_texts = [t.description for t in trips if t.id in good_trip_ids]
    if not good_texts:
        good_texts = [t.description for t in trips]

    # 5️⃣ 카테고리 추출
    joined_text = "\n".join(good_texts)
    reason_prompt = f"""
아래 기록에서 만족 요인을 핵심 키워드로 추출하세요.

출력(JSON 배열):
["자연", "음식", "휴식"]

[기록]
{joined_text}
"""
    reason_res = await client.generate(
        model=MODEL,
        prompt=reason_prompt,
        options={"temperature": 0},
        keep_alive=-1
    )
    categories = safe_json_parse(reason_res.get("response", ""))
    print("🏷️ 추출된 카테고리:", categories)

    # 6️⃣ 추천 생성
    existing_titles = [t.title for t in trips]
    category_text = ", ".join(categories)
    rec_prompt = f"""
카테고리: {category_text}

아래 여행지는 이미 다녀간 곳입니다. 추천 목록에서 절대 포함하지 마세요:
{", ".join(existing_titles)}

요청: 최소 {req.count}개의 여행지를 JSON 배열로 추천해주세요.

출력(JSON):
[{{ "title": "string", "reason": "string" }}]
"""
    rec_res = await client.generate(
        model=MODEL,
        prompt=rec_prompt,
        options={"temperature": 0},
        keep_alive=-1
    )
    recommendations = safe_json_parse(rec_res.get("response", ""))
    recommendations = [r for r in recommendations if r.get("title") not in existing_titles]

    return {"recommendations": recommendations[:req.count]}
