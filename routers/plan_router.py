from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    prefix="/plan",
    tags=["plan"],
)

@router.get("")
def plan_check():
    return {"status": "plan_ok"}


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

# 일반 generate 엔드포인트 (스트리밍 없이 전체 응답)
@router.get("/plan")
async def generate(request: Request):
    # form에 넣어놓은 데이터를 다 거내서 변수에 넣어주어야함.
    try :
        word = "제주도";
        answer = await plan_ollama.plan(word);
        return answer

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# @app.post("/reset")
# def reset_db(db: Session = Depends(get_db)):
#     rag_service.reset_database()
#     db.query(ChatMessage).delete()
#     db.commit()
#     return {"status": "Database Reset"}