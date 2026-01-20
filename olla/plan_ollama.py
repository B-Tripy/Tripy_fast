import ollama

MODEL = "gemma3:1b"
OLLAMA_BASE_URL = "http://localhost:11434"

async def plan(word: str):
    try:
        response = await ollama.AsyncClient().generate(
            model=MODEL,
            prompt=word,
            options={"temperature": 1},
            keep_alive=-1  # 필요 시 후속 요청에서도 유지
        )
        return {"result": response["response"]}

    except Exception as e:
        return {"error": str(e)}

