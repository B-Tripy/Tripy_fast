# 1. 가벼운 파이썬 이미지
FROM python:3.12-slim

# 2. 작업 디렉토리
WORKDIR /app

# 3. 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. pip 업그레이드 (Python 3.12 호환성 위해 권장)
RUN pip install --upgrade pip

# 5. 의존성 설치
COPY requirements.txt .
# CPU 전용 PyTorch 설치 (용량 절약)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# 6. 소스 코드 전체 복사
# .dockerignore에 등록된 파일 제외하고 모두 복사됨
COPY . .

# 7. 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]