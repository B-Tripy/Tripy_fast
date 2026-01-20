from fastapi import FastAPI, HTTPException, Depends, Request

#리액트 fastapi 통신가능하게 해줌
from fastapi.middleware.cors import CORSMiddleware

#프론트엔드 형식 검사
from pydantic import BaseModel

from fastapi import APIRouter

import os
import ollama

router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
)
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")

class ChatRequest(BaseModel):
    message: str  # 사용자가 입력한 질문
    userId: int


@router.post("")
async def ask_chatbot(request: ChatRequest):

    try:
        # 비동기 클라이언트 생성
        client = ollama.AsyncClient(host=OLLAMA_BASE_URL)

        query_text =  f'''
            넌 여행 플레너 ai 챗봇이야
            {request.message}를 "여행" 키워드와 
            밀접한 답변으로 500자 이내로 설명해줘.        
        '''

        # 모델 생성 요청
        response = await client.generate(
            model=MODEL,
            prompt=query_text,
            options={
                "temperature": 0.7,  # 창의성 조절
            },
            keep_alive=-1  # main.py에서 로드한 모델을 계속 메모리에 유지
        )

        return {"result": response["response"]}

    except Exception as e:
        print(f"Chatbot Router Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))