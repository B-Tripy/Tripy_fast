from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
import shutil
import os
from routers import plan_router
from routers import album_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # [시작 시]
    print("----- Server Starting -----")

    # album_router 안에 있는 모델 로드 함수 호출
    album_router.load_model(app.state)

    yield  # 서버 가동 중...

    # [종료 시]
    print("----- Server Shutting Down -----")

    # album_router 안에 있는 메모리 정리 함수 호출
    album_router.clear_model(app.state)


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


@app.get("/")
def read_root():
    return {"message": "Samsung RAG Agent Backend Running"}