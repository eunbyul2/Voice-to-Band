# routers/tts.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..services.tts_piper import synthesize_to_wav_bytes
import base64

router = APIRouter(tags=["tts"])

class TTSReq(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    # (선택) 향후 옵션 확장
    # speaker: int | None = None
    # speed: float = Field(1.0, gt=0.5, lt=2.0)

@router.post("/tts")
def tts(req: TTSReq):
    try:
        txt = req.text.strip()
        if not txt:
            raise HTTPException(status_code=400, detail="text is empty")
        wav = synthesize_to_wav_bytes(txt)
        return {"wav_base64": base64.b64encode(wav).decode("ascii")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))