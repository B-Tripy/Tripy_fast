from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from routers import plan_router
import ollama
from db import plan_redis

app = FastAPI(title="Samsung RAG Agent", description="RAG Chatbot with Black Theme")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 여기에서 각각의 router를 등록
app.include_router(plan_router.router)

MODEL = "gemma3:1b"
OLLAMA_BASE_URL = "http://localhost:11434"


# 앱 시작 시 모델 미리 로드 (preload)
@app.on_event("startup")
async def preload_model():
    print("올라마 로딩 시작..======================")
    try:
        # 빈 프롬프트로 모델 로드 + 영구 유지
        await ollama.AsyncClient().generate(
            model=MODEL,
            prompt=" ",  # 빈 프롬프트 (또는 "preload" 같은 더미 텍스트)
            keep_alive=-1  # -1: 영구적으로 메모리에 유지
        )
        print(f"{MODEL} 모델이 미리 로드되었습니다. (메모리에 영구 유지)")

        await plan_redis.preload_redis()

    except Exception as e:
        print(f"모델 preload 실패 : {e}")


@app.get("/")
def read_root():
    return {"message": "Samsung RAG Agent Backend Running"}
