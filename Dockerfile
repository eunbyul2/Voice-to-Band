FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl ca-certificates libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 STATIC_DIR=/data/static
WORKDIR /app

# requirements.txt 는 리포지토리 루트에 있음
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 소스 복사
COPY app/ /app/app
RUN mkdir -p /data/static

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -sf http://localhost:8000/health || exit 1
  
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--proxy-headers"]