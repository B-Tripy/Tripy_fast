from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
<<<<<<< HEAD
<<<<<<< Updated upstream
import shutil
import os
=======
import os
=======
>>>>>>> origin/master
import ollama
from db import plan_redis
# -----------------------------
# Routers
# -----------------------------
<<<<<<< HEAD
>>>>>>> Stashed changes
=======
>>>>>>> origin/master
from routers import plan_router
from routers import album_router
from routers import recommend_router
from routers import bookmark_router
from routers import chatbot_router


<<<<<<< HEAD
<<<<<<< Updated upstream
=======

MODEL = "gemma3:1b"
# OLLAMA_BASE_URL = "http://localhost:11434"    # 로컬
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434")   # Docker
=======

MODEL = "gemma3:1b"
OLLAMA_BASE_URL = "http://localhost:11434"
>>>>>>> origin/master

# -----------------------------
# Lifespan (시작/종료 처리)
# -----------------------------
<<<<<<< HEAD
>>>>>>> Stashed changes
=======
>>>>>>> origin/master
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("----- Server Starting -----")
<<<<<<< HEAD
<<<<<<< Updated upstream
=======
    print("올라마 로딩 시작..======================")
    try:
        # 빈 프롬프트로 모델 로드 + 영구 유지
        await ollama.AsyncClient(host=OLLAMA_BASE_URL).generate(
=======
    print("올라마 로딩 시작..======================")
    try:
        # 빈 프롬프트로 모델 로드 + 영구 유지
        await ollama.AsyncClient().generate(
>>>>>>> origin/master
            model=MODEL,
            prompt=" ",  # 빈 프롬프트 (또는 "preload" 같은 더미 텍스트)
            keep_alive=-1  # -1: 영구적으로 메모리에 유지
        )
        print(f"{MODEL} 모델이 미리 로드되었습니다. (메모리에 영구 유지)")
<<<<<<< HEAD
>>>>>>> Stashed changes
=======
>>>>>>> origin/master

        await plan_redis.preload_redis()

<<<<<<< HEAD
<<<<<<< Updated upstream
    yield  # 서버 가동 중...
=======
        # album_router 모델 로드
        album_router.load_model(app.state)
>>>>>>> Stashed changes
=======
        # album_router 모델 로드
        # album_router.load_model(app.state)
>>>>>>> origin/master

        yield  # 서버 가동 중

<<<<<<< HEAD
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
=======
        print("----- Server Shutting Down -----")
        # album_router 메모리 정리
        # album_router.clear_model(app.state)

    except Exception as e:
        print(f"모델 preload 실패 또는 album_router 실패: {e}")
>>>>>>> origin/master


# -----------------------------
# FastAPI 앱 생성
# -----------------------------
app = FastAPI(
    title="Samsung RAG Agent",
    description="RAG Chatbot with Black Theme",
    lifespan=lifespan
)

# -----------------------------
# CORS 설정
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Router 등록
# -----------------------------
app.include_router(plan_router.router)
app.include_router(album_router.router)
app.include_router(recommend_router.router)
app.include_router(bookmark_router.router)
app.include_router(chatbot_router.router)


# -----------------------------
# Root 엔드포인트
# -----------------------------
@app.get("/")
def read_root():
    return {"message": "Samsung RAG Agent Backend Running"}
