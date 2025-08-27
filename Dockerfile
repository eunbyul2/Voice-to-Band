FROM python:3.11-slim

# 시스템 패키지: ffmpeg, curl(헬스체크용), libsndfile1(soundfile용), CA
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl ca-certificates libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    STATIC_DIR=/data/static

WORKDIR /app

# 루트에 있는 requirements.txt 먼저 설치(레이어 캐시 이점)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 소스 복사
COPY app/ /app/app

# 정적 디렉토리
RUN mkdir -p /data/static

# 헬스체크 (curl 사용)
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -sf http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--proxy-headers"]