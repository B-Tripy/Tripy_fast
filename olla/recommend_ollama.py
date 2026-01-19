# services/recommend_ollama.py
import os
import ollama
import re
import json

MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")

def safe_json_parse(raw: str):
    """AI가 반환한 JSON 문자열을 안전하게 파싱"""
    try:
        match = re.search(r"```json(.*?)```", raw, flags=re.DOTALL | re.IGNORECASE)
        json_str = match.group(1).strip() if match else raw.strip()
        return json.loads(json_str)
    except Exception as e:
        print("❌ JSON 파싱 실패:", e)
        print(raw)
        return []

async def evaluate_satisfaction(trips: list):
    """AI를 사용해 만족도 점수 평가"""
    client = ollama.AsyncClient()
    summaries = "\n".join([f"{t.id}. {t.title}: {t.description}" for t in trips])

    prompt = f"""
아래 여행 기록 각각에 대해 만족도를 1~5 중 하나로 평가하세요.
1: 불만족, 5: 매우 만족
출력(JSON 배열):
[{{ "trip_id": number, "score": number }}]

[기록]
{summaries}
"""
    res = await client.generate(
        model=MODEL,
        prompt=prompt,
        options={"temperature": 0},
        keep_alive=-1
    )
    return safe_json_parse(res.get("response", ""))

async def extract_categories(trip_texts: list):
    """AI를 사용해 만족 요인(카테고리) 추출"""
    client = ollama.AsyncClient()
    joined_text = "\n".join(trip_texts)
    prompt = f"""
아래 기록에서 만족 요인을 핵심 키워드로 추출하세요.
출력(JSON 배열):
["자연", "음식", "휴식"]

[기록]
{joined_text}
"""
    res = await client.generate(
        model=MODEL,
        prompt=prompt,
        options={"temperature": 0},
        keep_alive=-1
    )
    return safe_json_parse(res.get("response", ""))

async def generate_recommendations(existing_titles: list, categories: list, count: int):
    """AI를 사용해 새로운 여행지 추천"""
    client = ollama.AsyncClient()
    category_text = ", ".join(categories)
    prompt = f"""
카테고리: {category_text}
아래 여행지는 이미 다녀간 곳입니다. 추천 목록에서 제외하세요:
{", ".join(existing_titles)}

요청: 최소 {count}개의 여행지를 JSON 배열로 추천해주세요.
출력(JSON):
[{{ "title": "string", "reason": "string" }}]
"""
    res = await client.generate(
        model=MODEL,
        prompt=prompt,
        options={"temperature": 0},
        keep_alive=-1
    )
    recs = safe_json_parse(res.get("response", ""))
    return [r for r in recs if r.get("title") not in existing_titles]
