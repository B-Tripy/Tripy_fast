import os
import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from fastapi import APIRouter, UploadFile, File, Request, HTTPException, Depends

# 라우터 설정
router = APIRouter(
    prefix="/album",
    tags=["album"],
)

# -----------------------------------------------------------
# 1. 설정 및 클래스 정의
# -----------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 프로젝트 루트 경로 계산
MODEL_PATH = os.path.join(BASE_DIR, "model", "efficientnet_v2_final.pth")
CLASSES = ['건물', '문화', '음식', '숲', '산', '인물', '바다', '거리']


# -----------------------------------------------------------
# 2. 전처리 함수
# -----------------------------------------------------------
def transform_image(image_bytes):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return transform(image).unsqueeze(0)


# -----------------------------------------------------------
# 3. 모델 관리 함수 (Main.py에서 호출용)
# -----------------------------------------------------------
def load_model(app_state):
    """
    서버 시작 시 모델을 로드하여 app.state에 저장하는 함수
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Album] {MODEL_PATH}에서 {device}로 모델 로드중...")

    try:
        # 모델 구조 생성
        model = models.efficientnet_v2_s(weights=None)

        # Classifier 수정
        num_ftrs = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(num_ftrs, len(CLASSES))
        )

        # 가중치 로드
        if os.path.exists(MODEL_PATH):
            checkpoint = torch.load(MODEL_PATH, map_location=device)
            model.load_state_dict(checkpoint)
        else:
            print(f"[Error] 모델 파일이 없습니다: {MODEL_PATH}")
            # 개발 중 파일이 없을 때를 대비한 예외처리 (필요 시 제거)
            # raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

        model.to(device)
        model.eval()

        # app.state에 저장
        app_state.model = model
        app_state.device = device
        print("[Album] 모델 로드 성공")

    except Exception as e:
        print(f"[Album] 모델 로드 실패: {e}")
        # 실패해도 서버가 죽지 않게 하려면 raise를 빼거나, 
        # 필수 기능이면 raise e를 유지합니다.
        pass


def clear_model(app_state):
    """
    서버 종료 시 모델 메모리 해제
    """
    print("[Album] 모델 메모리 해제 시도")
    if hasattr(app_state, 'model'):
        del app_state.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    print("[Album] 모델 메모리 정리 완료")


# -----------------------------------------------------------
# 4. API 엔드포인트
# -----------------------------------------------------------
@router.get("")
def plan_check():
    return {"status": "album_ok"}


@router.post("/category")  # URL: /album/predict
async def predict_image(request: Request, file: UploadFile = File(...)):
    # app.state에서 모델 꺼내기
    model = getattr(request.app.state, "model", None)
    device = getattr(request.app.state, "device", "cpu")

    if model is None:
        raise HTTPException(status_code=503, detail="AI 모델이 로드되지 않았습니다.")

    try:
        # 이미지 읽기 및 전처리
        image_bytes = await file.read()
        tensor = transform_image(image_bytes).to(device)

        # 추론
        with torch.no_grad():
            outputs = model(tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)

        # 결과 포맷팅
        results = []
        probs = probabilities[0].tolist()

        for i, prob in enumerate(probs):
            results.append({
                "category": CLASSES[i],
                "score": round(prob, 4),
                "category_id": i + 1
            })

        # 점수 높은 순 정렬
        results.sort(key=lambda x: x['score'], reverse=True)

        return {"results": results}

    except Exception as e:
        print(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))



"""
[데이터 변환 과정]

file (UploadFile): FastAPI가 받은 택배 상자 ⬇️ await file.read() (상자 뜯기)

image_bytes (bytes): 01010... 진짜 데이터 (질문하신 파라미터) ⬇️ io.BytesIO(...) (파일인 척 포장하기)

In-Memory File: 메모리에 떠 있는 가짜 파일 ⬇️ Image.open(...)

PIL Image: 파이썬이 이해하는 그림 객체 ⬇️ transform(...)

Tensor: AI 모델이 이해하는 숫자 배열
"""