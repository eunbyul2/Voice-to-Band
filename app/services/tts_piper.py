# app/services/tts_piper.py
import os, subprocess, tempfile, textwrap
from ..config import settings

# Piper 한 번에 너무 긴 문장 넣으면 실패하는 경우 대비(임계값 경험치)
_MAX_CHARS = 350

def _ensure_piper_ready():
    if not settings.PIPER_PATH or not settings.PIPER_MODEL:
        raise RuntimeError("Piper not configured. Set PIPER_PATH and PIPER_MODEL in .env")

def _synthesize_one(text: str) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        out_wav = os.path.join(td, "out.wav")
        cmd = [
            settings.PIPER_PATH,
            "--model", settings.PIPER_MODEL,
            "--speaker", str(settings.PIPER_SPEAKER),
            "--output_file", out_wav,
        ]
        try:
            # stdin으로 텍스트 전달
            proc = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = proc.communicate(text, timeout=40)
        except subprocess.TimeoutExpired:
            proc.kill()
            raise RuntimeError("Piper timeout: input too long or model too slow")
        if proc.returncode != 0 or not os.path.exists(out_wav):
            err = (stderr or "").strip()
            raise RuntimeError(f"Piper failed (code {proc.returncode}): {err}")
        with open(out_wav, "rb") as f:
            return f.read()

def synthesize_to_wav_bytes(text: str) -> bytes:
    _ensure_piper_ready()
    txt = (text or "").strip()
    if not txt:
        raise RuntimeError("text is empty")

    # 너무 길면 문장 단위로 나눠 합성 후 순차 연결(간단한 join: wav concat은 후속 과제)
    # 여기선 편의상 여러 조각을 개별 파일로 만들어 프런트에서 이어붙이게 하거나,
    # 단일 wav가 꼭 필요하면 librosa/sf로 concat 로직을 추가.
    if len(txt) <= _MAX_CHARS:
        return _synthesize_one(txt)

    chunks = textwrap.wrap(txt, _MAX_CHARS, break_long_words=False, replace_whitespace=False)
    # 단일 WAV로 합치는 간단한 방법(샘플레이트 동일 가정): soundfile로 이어붙이는 구현을 원하면 알려줘.
    # 지금은 첫 조각만 반환하지 말고, 실패 안내:
    raise RuntimeError(f"text too long ({len(txt)} chars). Please split on client side.")