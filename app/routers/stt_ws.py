# routers/stt_ws.py
import asyncio, base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import numpy as np
from ..services.stt_whisper import transcribe_pcm16

router = APIRouter(tags=["stt"])

# 1초 창 처리 기준(샘플레이트 16k 가정), 최대 보유 2초로 제한
MAX_SECONDS_BUFFER = 2

@router.websocket("/ws/stt")
async def ws_stt(ws: WebSocket):
    await ws.accept()
    buf = np.zeros(0, dtype=np.int16)
    try:
        while True:
            msg = await ws.receive_json()
            t = msg.get("t")
            if t == "pcm":
                data_b64 = msg["data"]
                sr = int(msg.get("sr", 16000))
                if sr <= 0 or sr > 48000:
                    await ws.send_json({"t":"error", "message": "invalid sample rate"})
                    continue

                chunk = np.frombuffer(base64.b64decode(data_b64), dtype=np.int16)
                if chunk.size == 0:
                    continue
                # 누적 + 최대 2초만 유지
                buf = np.concatenate([buf, chunk])
                max_len = sr * MAX_SECONDS_BUFFER
                if buf.size > max_len:
                    buf = buf[-max_len:]

                # 최근 1초 창으로 partial
                if buf.size >= sr:
                    window = buf[-sr:]
                    text, conf = transcribe_pcm16(window, sr=sr)
                    if text:
                        await ws.send_json({"t":"partial", "text":text, "conf":float(conf)})

            elif t == "flush":
                sr = int(msg.get("sr", 16000))
                if buf.size > 0:
                    text, conf = transcribe_pcm16(buf, sr=sr)
                    await ws.send_json({"t":"final", "text":text or "", "conf":float(conf)})
                    buf = np.zeros(0, dtype=np.int16)

            elif t == "ping":
                await ws.send_json({"t":"pong"})

    except WebSocketDisconnect:
        return
    except Exception as e:
        # ws가 이미 끊겼을 수도 있으니 best-effort
        try:
            await ws.send_json({"t":"error", "message": str(e)})
        except Exception:
            pass