import os
import ollama
from fastapi import HTTPException
from typing import List

MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")
# OLLAMA_BASE_URL = "http://localhost:11434"    # 로컬
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434")   # Docker

async def review(post: str):
    if not post:
        return {"result": "요약할 내용이 없습니다."}

    prompt_message = (f"다음은 여행에 대한 여러 사진의 설명들입니다:\n"
        f"{post}\n\n"
        f"위 내용들을 바탕으로 자연스러운 하나의 여행 요약글을 작성해주세요. "
        f"한국어로 3~5문장 정도로 요약해줘."
        f"공백 포함 200자 이내로 답변해줘.")
    try:
        # 비동기 클라이언트 생성
        client = ollama.AsyncClient(host=OLLAMA_BASE_URL)

        # 모델 생성 요청
        response = await client.generate(
            model=MODEL,
            prompt=prompt_message,
            options={
                "temperature": 0.7,  # 창의성 조절
            },
            keep_alive=-1  # main.py에서 로드한 모델을 계속 메모리에 유지
        )

        return {"summary": response["response"]}

    except Exception as e:
        print(f"Chatbot Router Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))