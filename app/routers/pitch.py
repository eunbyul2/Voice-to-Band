# routers/pitch.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import base64, numpy as np
from ..config import settings
from ..services.pitch_crepe import estimate_f0

router = APIRouter(tags=["pitch"])

class PitchReq(BaseModel):
    pcm_base64: str
    sr: int = Field(16000, ge=8000, le=48000)

@router.post("/pitch")
def pitch(req: PitchReq):
    try:
        raw = base64.b64decode(req.pcm_base64)
        if len(raw) < 2:
            raise HTTPException(status_code=400, detail="empty pcm")
        pcm = np.frombuffer(raw, dtype=np.int16)
        # 너무 긴 입력은 과금/부하 위험 → 10초 제한
        max_len = req.sr * 10
        if pcm.size > max_len:
            pcm = pcm[:max_len]
        x = pcm.astype(np.float32) / 32768.0
        f0 = estimate_f0(x, req.sr, settings.CREPE_ONNX_PATH or "")
        return {"f0_hz": float(f0)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))