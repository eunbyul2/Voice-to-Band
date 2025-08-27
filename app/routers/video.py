# app/routers/video.py
import os, subprocess, uuid
from fastapi import APIRouter, HTTPException, Query
from ..processing import STATIC_DIR

router = APIRouter(tags=["video"])

def _make_mp4_from_wav(wav_path: str, title: str) -> str:
    if not os.path.exists(wav_path):
        raise FileNotFoundError(wav_path)
    out = os.path.join(STATIC_DIR, f"{uuid.uuid4().hex}.mp4")
    # 단색 배경(1280x720) + 오디오 → MP4(H.264 + AAC), 길이는 오디오에 맞춤(-shortest)
    # drawtext는 폰트 문제 생길 수 있어 생략. 필요하면 나중에 커버이미지/썸네일 사용.
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=1280x720",
        "-i", wav_path,
        "-shortest",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        out
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out

@router.post("/video/make")
def make_video(filename: str = Query(...), title: str = Query("Voice2Band")):
    wav = os.path.join(STATIC_DIR, filename)
    try:
        mp4 = _make_mp4_from_wav(wav, title)
    except subprocess.CalledProcessError as e:
        err = (e.stderr or b"").decode(errors="ignore")
        raise HTTPException(500, f"ffmpeg failed: {err}")
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True, "video_url": f"/api/static/{os.path.basename(mp4)}"}