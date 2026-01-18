from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
<<<<<<< Updated upstream
import shutil
import os
=======
import os
import ollama
from db import plan_redis
# -----------------------------
# Routers
# -----------------------------
>>>>>>> Stashed changes
from routers import plan_router
from routers import album_router
import olla


<<<<<<< Updated upstream
=======

MODEL = "gemma3:1b"
# OLLAMA_BASE_URL = "http://localhost:11434"    # 로컬
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434")   # Docker

# -----------------------------
# Lifespan (시작/종료 처리)
# -----------------------------
>>>>>>> Stashed changes
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [시작 시]
    print("----- Server Starting -----")
<<<<<<< Updated upstream
=======
    print("올라마 로딩 시작..======================")
    try:
        # 빈 프롬프트로 모델 로드 + 영구 유지
        await ollama.AsyncClient(host=OLLAMA_BASE_URL).generate(
            model=MODEL,
            prompt=" ",  # 빈 프롬프트 (또는 "preload" 같은 더미 텍스트)
            keep_alive=-1  # -1: 영구적으로 메모리에 유지
        )
        print(f"{MODEL} 모델이 미리 로드되었습니다. (메모리에 영구 유지)")
>>>>>>> Stashed changes

    # album_router 안에 있는 모델 로드 함수 호출
    album_router.load_model(app.state)

<<<<<<< Updated upstream
    yield  # 서버 가동 중...
=======
        # album_router 모델 로드
        album_router.load_model(app.state)
>>>>>>> Stashed changes

    # [종료 시]
    print("----- Server Shutting Down -----")

<<<<<<< Updated upstream
    # album_router 안에 있는 메모리 정리 함수 호출
    album_router.clear_model(app.state)
=======
        print("----- Server Shutting Down -----")
        # album_router 메모리 정리
        album_router.clear_model(app.state)

    except Exception as e:
        print(f"모델 preload 실패 또는 album_router 실패: {e}")
>>>>>>> Stashed changes


app = FastAPI(title="Samsung RAG Agent", description="RAG Chatbot with Black Theme", lifespan=lifespan)

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
app.include_router(album_router.router)

MODEL = "gemma3:1b"
OLLAMA_BASE_URL = "http://localhost:11434"


# 앱 시작 시 모델 미리 로드 (preload)
@app.on_event("startup")
async def preload_model():
    try:
        # 빈 프롬프트로 모델 로드 + 영구 유지
        await olla.AsyncClient().generate(
            model=MODEL,
            prompt=" ",  # 빈 프롬프트 (또는 "preload" 같은 더미 텍스트)
            keep_alive=-1  # -1: 영구적으로 메모리에 유지
        )
        print(f"{MODEL} 모델이 미리 로드되었습니다. (메모리에 영구 유지)")

    except Exception as e:
        print(f"모델 preload 실패 : {e}")


@app.get("/")
def read_root():
    return {"message": "Samsung RAG Agent Backend Running"}
