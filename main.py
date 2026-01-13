from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from routers import plan_router

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


@app.get("/")
def read_root():
    return {"message": "Samsung RAG Agent Backend Running"}
