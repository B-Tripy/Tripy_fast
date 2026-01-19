from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import plan_mysql
from olla import plan_ollama

from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from rag import rag_service

UPLOAD_DIR = "pdf"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# app/routers/board.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/ai/plan",
        tags=["plan"],
)

# @router.get("")
# def plan_check():
#     return {"status": "plan_ok"}


@router.post("/upload")
def upload_documents(files: List[UploadFile] = File(...)):
    total_chunks = 0
    processed_files = []

    for file in files:
        filename = file.filename.lower()
        if not (filename.endswith('.pdf') or filename.endswith('.txt')):
            continue  # Skip unsupported, or raise error? Let's skip for now or better warn.

        temp_file_path = f"temp_{file.filename}"
        full_path = os.path.join(UPLOAD_DIR, temp_file_path)
        with open( full_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            num_chunks = rag_service.ingest_document(full_path, file.filename)
            total_chunks += num_chunks
            processed_files.append(file.filename)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    return {"status": "success", "processed_files": processed_files, "total_chunks": total_chunks}
    # return "ok"

@router.get("/stats")
def get_stats():
    return {
        "count": rag_service.get_document_count(),
        "sources": rag_service.get_unique_sources()

         # "count": 10,
         # "sources": [1, 2, 3, 4, 5]

        # "result" : "ok"
    }
class PlanRequest(BaseModel):
    departure: str
    destination: str
    startDate: str
    endDate: str
    people: str
    activities: List[str]
    food: str | None = ""
    ageGroup: str | None = ""
    purpose: str | None = ""
    extra: str | None = ""
    userId: int

# 일반 generate 엔드포인트 (스트리밍 없이 전체 응답)
# @router.post("/")
# async def generate(request: Request):
#     # form에 넣어놓은 데이터를 다 거내서 변수에 넣어주어야함.
#     try :
#
#         # 내일은 form데이터 가지고 와서 하나의 문자열로 연결해서 word에 넣어줘도 되고
#         # axios로 값을 전달할 때 보내는 쪽에서 json으로 가지고 오면
#         # json으로 가지고 온 데이터를 word로 통째로 넣어줘도 됨.!!
#         prompt = f"""
#         너는 여행 일정 플래너 AI야.
#
#         - 출발지: {request.departure}
#         - 목적지: {request.destination}
#         - 여행 기간: {request.startDate} ~ {request.endDate}
#         - 인원: {request.people}명
#         - 선호 활동: {", ".join(request.activities)}
#         - 음식 선호: {request.food}
#         - 연령대: {request.ageGroup}
#         - 여행 목적: {request.purpose}
#         - 추가 요청: {request.extra}
#
#         위 조건을 반영해서
#         1일차, 2일차 형식으로
#         아침 / 점심 / 저녁 / 추천 장소를 포함해
#         일정을 만들어줘.
#         """
#         answer = await plan_ollama.plan(prompt)
#         return answer
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@router.post("/")
async def generate(request: PlanRequest):
    try:
        print("🔥 받은 데이터:", request)


        ### 크로마 pdf읽어와서 그거를 prompt에 넣어주면 됨.

        query_text = f'''
            {request.destination}지역의 
            휴관일을 아주 간단하게 답답형으로 알려줘.
        '''

        rag_info = await rag_service.query_rag_info(query_text)

        print(rag_info)
        prompt = f"""
         너는 여행 일정 플래너 AI야.
        목적지: {request.destination} 의 휴관일이야
        해당 지역에 휴관일도 같이 결과로 넣어줘.
        휴관일 정보는 {rag_info}야.
        
         - 출발지: {request.departure}
         - 목적지: {request.destination}
         - 여행 기간: {request.startDate} ~ {request.endDate}
         - 인원: {request.people}명
         - 선호 활동: {", ".join(request.activities)}
         - 음식 선호: {request.food}
         - 연령대: {request.ageGroup}
         - 여행 목적: {request.purpose}
         - 추가 요청: {request.extra}

         위 조건을 반영해서
         1일차, 2일차 형식으로
         아침 / 점심 / 저녁 / 추천 장소를 포함해
         일정을 만들어줘.
         
        """

        print("🔥 생성된 프롬프트:", prompt)

        answer = await plan_ollama.plan(prompt)

        print("🔥 Ollama 응답:", answer)

        # plan_mysql를 import
        print("================>> " + str(request.userId))
        # await  plan_redis.redis_insert("plan:" + str(request.userId), answer)
        plan_mysql.create_plan(
            title=request.departure,
            description=request.destination,
            start_date= request.startDate,
            end_date= request.endDate,
            plan=answer['result']
        )

        tripId = plan_mysql.read_plan_last()

        plan_mysql.create_usertrip(request.userId, tripId)

        return answer

    except Exception as e:
        print("🔥 서버 에러:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/select")
def redis_get(request: PlanRequest):
    print(request.userId)
    # # answer = plan_redis.redis_select(str(request.userId))
    # return answer