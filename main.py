from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import olla

# -----------------------------
# Routers
# -----------------------------
from routers import plan_router
from routers import album_router
from routers import recommend_router
from routers import bookmark_router
from routers import chatbot_router
from routers import review_router
MODEL = "gemma3:1b"
OLLAMA_BASE_URL = "http://localhost:11434"

# -----------------------------
# Lifespan (시작/종료 처리)
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("----- Server Starting -----")

    # album_router 모델 로드
    album_router.load_model(app.state)

    yield  # 서버 가동 중

    print("----- Server Shutting Down -----")
    # album_router 메모리 정리
    album_router.clear_model(app.state)


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
    allow_origins=["*"],  # 개발용
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
app.include_router(review_router.router)

# -----------------------------
# Ollama 모델 preload
# -----------------------------
@app.on_event("startup")
async def preload_model():
    try:
        client = olla.AsyncClient()
        # 빈 프롬프트로 모델 로드 + 영구 유지
        await client.generate(
            model=MODEL,
            prompt=" ",
            keep_alive=-1
        )
        print(f"{MODEL} 모델이 미리 로드되었습니다. (메모리에 영구 유지)")

    except Exception as e:
        print(f"모델 preload 실패 : {e}")


# -----------------------------
# Root 엔드포인트
# -----------------------------
@app.get("/")
def read_root():
    return {"message": "Samsung RAG Agent Backend Running"}
