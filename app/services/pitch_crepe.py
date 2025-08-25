# app/services/pitch_crepe.py
import numpy as np
try:
    import onnxruntime as ort
except Exception:
    ort = None

_session = None

def load_crepe(onnx_path: str):
    global _session
    if ort is None:
        raise RuntimeError("onnxruntime not installed")
    if not onnx_path or not isinstance(onnx_path, str):
        raise RuntimeError("CREPE_ONNX_PATH not configured")
    if _session is None:
        _session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
    return _session

def estimate_f0(audio_f32: np.ndarray, sr: int, onnx_path: str) -> float:
    """TODO: CREPE ONNX 입출력 스펙에 맞춰 구현 필요.
    지금은 명확히 '미구현' 에러를 던져 오해를 방지한다."""
    load_crepe(onnx_path)
    raise RuntimeError("pitch(f0) estimation not implemented yet for CREPE-ONNX")