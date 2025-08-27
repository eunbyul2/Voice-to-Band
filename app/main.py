# app/main.py (경로만 핵심 수정)
import os, tempfile
import uvicorn
from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from loguru import logger

from .config import settings
from .routers import stt_ws, tts, presets, metrics, pitch, video, public
from .utils.schemas import ProcessParams
from .processing import process_file, STATIC_DIR

app = FastAPI(title="Voice2Band Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUESTS = Counter("v2b_requests_total", "Total API requests", ["route"])

# 라우터는 이미 /api 프리픽스로 include 됨
app.include_router(stt_ws.router, prefix=settings.API_PREFIX)
app.include_router(tts.router,     prefix=settings.API_PREFIX)
app.include_router(presets.router, prefix=settings.API_PREFIX)
app.include_router(metrics.router, prefix=settings.API_PREFIX)   # POST /api/metrics/push
app.include_router(pitch.router,   prefix=settings.API_PREFIX)
app.include_router(video.router, prefix=settings.API_PREFIX)
app.include_router(public.router, prefix=settings.API_PREFIX)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics_endpoint():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ⬇️ 여기 두 개를 /api 하위로 이동
@app.post(f"{settings.API_PREFIX}/process")
async def process_audio(file: UploadFile = File(...), params: ProcessParams = Depends()):
    REQUESTS.labels(route=f"{settings.API_PREFIX}/process").inc()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        out_path, name = process_file(tmp_path, params.pitch_semitones, params.time_stretch)
        url = f"{settings.API_PREFIX}/static/{name}"   # ← /api/static/...
        return JSONResponse({"ok": True, "url": url})
    except Exception as e:
        logger.exception(e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
    finally:
        try: os.remove(tmp_path)
        except Exception: logger.warning(f"tmp cleanup failed: {tmp_path}")

@app.get(f"{settings.API_PREFIX}/static/{{filename}}")
def get_file(filename: str):
    return FileResponse(os.path.join(STATIC_DIR, filename))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)