# app/processing.py
import os, subprocess, uuid
from typing import Tuple
import librosa, soundfile as sf
from loguru import logger

STATIC_DIR = os.getenv("STATIC_DIR", "/data/static")
os.makedirs(STATIC_DIR, exist_ok=True)

def _to_wav(input_path: str) -> str:
    out = os.path.join(STATIC_DIR, f"{uuid.uuid4().hex}.wav")
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", out]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        msg = (e.stderr or b"").decode(errors="ignore")
        logger.error(f"ffmpeg failed: {msg}")
        raise RuntimeError(f"ffmpeg convert failed: {msg}") from e
    return out

def _apply_fx(wav_path: str, pitch_semitones: float, time_stretch: float) -> str:
    y, sr = librosa.load(wav_path, sr=None, mono=True)   # ffmpeg에서 이미 16k mono로 변환
    steps = float(pitch_semitones)
    rate  = float(time_stretch)
    # 안전 범위(프론트/스키마에서도 제한하지만 한번 더)
    rate = max(0.25, min(4.0, rate))

    if abs(steps) > 1e-2:
        y = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=steps)
    if abs(rate - 1.0) > 1e-3:
        y = librosa.effects.time_stretch(y=y, rate=rate)

    out = os.path.join(STATIC_DIR, f"{uuid.uuid4().hex}_fx.wav")
    sf.write(out, y, sr, subtype="PCM_16")
    return out

def process_file(tmp_upload_path: str, pitch_semitones: float, time_stretch: float) -> Tuple[str, str]:
    wav = _to_wav(tmp_upload_path)
    try:
        out = _apply_fx(wav, pitch_semitones, time_stretch)
    finally:
        # 중간 파일 정리
        try: os.remove(wav)
        except Exception: pass
    return out, os.path.basename(out)