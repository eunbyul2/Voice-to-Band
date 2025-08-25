
import base64, numpy as np, io, soundfile as sf, resampy

def b64_to_pcm16(data_b64: str, sr:int=16000) -> tuple[np.ndarray, int]:
    raw = base64.b64decode(data_b64)
    pcm = np.frombuffer(raw, dtype=np.int16)
    return pcm, sr

def wav_bytes_to_pcm16(b: bytes) -> tuple[np.ndarray, int]:
    f = io.BytesIO(b)
    audio, sr = sf.read(f, dtype='int16', always_2d=False)
    if audio.ndim == 2:
        audio = audio[:,0]  # mono
    return audio, sr

def resample_pcm16(pcm: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out: return pcm
    x = pcm.astype('float32')/32768.0
    y = resampy.resample(x, sr_in, sr_out)
    return (np.clip(y, -1, 1) * 32768.0).astype('int16')
