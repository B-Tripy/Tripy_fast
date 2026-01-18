import ollama
import os

MODEL = "gemma3:1b"
# OLLAMA_BASE_URL = "http://localhost:11434"    # 로컬
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434")   # Docker

async def plan(word: str):
    try:
        client = ollama.AsyncClient(host=OLLAMA_BASE_URL)
        
        response = await ollama.AsyncClient().generate(
            model=MODEL,
            prompt=word,
            options={"temperature": 1},
            keep_alive=-1  # 필요 시 후속 요청에서도 유지
        )
        return {"result": response["response"]}

    except Exception as e:
        print("에러 정보 >>>> ", e)