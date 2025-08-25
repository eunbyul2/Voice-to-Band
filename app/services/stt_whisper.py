# app/services/stt_whisper.py
import numpy as np
from faster_whisper import WhisperModel
from ..config import settings

_model = None

def get_model() -> WhisperModel:
    global _model
    if _model is None:
        # threads 옵션은 CPU 성능에 맞춰 조정(기본 4~8 권장)
        _model = WhisperModel(
            settings.STT_MODEL,
            device=settings.STT_DEVICE,             # "cpu" | "cuda"
            compute_type=settings.STT_COMPUTE_TYPE, # "int8"|"float32"|...
            num_workers=1,                          # 오디오 디코딩 워커
            cpu_threads=4 if settings.STT_DEVICE == "cpu" else 0,
        )
    return _model

def transcribe_pcm16(pcm16: np.ndarray, sr: int = 16000) -> tuple[str, float]:
    """mono PCM16 → (text, avg_confidence). sr은 16k 권장."""
    if pcm16.size == 0:
        return "", 0.0

    # faster-whisper는 16k 기준이 안전. 다른 sr이면 내부 리샘플 권장(단, 지금은 16k 가정)
    if sr != 16000:
        # 간단한 방어적 처리: sr 불일치 시 바로 빈값 반환(또는 리샘플 추가)
        # 원하면 librosa로 리샘플 로직 넣어줄게.
        pass

    model = get_model()
    audio = (pcm16.astype(np.float32) / 32768.0)
    # 짧은 클립은 beam_size/temperature 너무 높이면 느려짐 → 빠른 설정
    segments, info = model.transcribe(
        audio,
        language='ko',
        vad_filter=True,
        word_timestamps=False,
        beam_size=1,
        best_of=1,
        temperature=0.0,
    )

    texts, confs = [], []
    for seg in segments:
        if seg.text:
            texts.append(seg.text)
        # avg_logprob가 없는 경우도 있음
        if getattr(seg, "avg_logprob", None) is not None:
            confs.append(float(seg.avg_logprob))

    text = " ".join(t.strip() for t in texts).strip()
    conf = float(np.mean(confs)) if confs else 0.0
    return text, conf