from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import shutil
import os

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
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # try:
        #     num_chunks = rag_service.ingest_document(temp_file_path, file.filename)
        #     total_chunks += num_chunks
        #     processed_files.append(file.filename)
        # finally:
        #     if os.path.exists(temp_file_path):
        #         os.remove(temp_file_path)

    # return {"status": "success", "processed_files": processed_files, "total_chunks": total_chunks}
    return "ok"

@router.get("/stats")
def get_stats():
    return {
        # "count": rag_service.get_document_count(),
        # "sources": rag_service.get_unique_sources()

         "count": 10,
         "sources": [1, 2, 3, 4, 5]

        # "result" : "ok"
    }


# @app.post("/reset")
# def reset_db(db: Session = Depends(get_db)):
#     rag_service.reset_database()
#     db.query(ChatMessage).delete()
#     db.commit()
#     return {"status": "Database Reset"}