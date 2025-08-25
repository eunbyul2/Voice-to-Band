
# Voice2Band FastAPI Backend

FastAPI 백엔드 스켈레톤입니다. **STT(faster‑whisper) WebSocket**, **TTS(Piper)**, **프리셋/메트릭 API**, (옵션) **피치(CREPE/ONNX)** 를 제공합니다.
프런트(React/WebAudio/Tone.js)와 결합해 **실시간은 브라우저**, **모델/저장은 서버**로 분리하는 아키텍처를 가정합니다.

## ✅ 파이썬 버전 추천
- **Python 3.10 권장**: 오디오/ML 휠 호환성이 가장 넓고 안정적.
- 3.11도 대부분 동작하나, 일부 라이브러리/바이너리(특히 오디오) 설치 이슈가 있을 수 있습니다.
- Dockerfile은 3.10 기준으로 제공.

## 🔧 빠른 시작 (로컬)
```bash
# conda python=3.10 버전으로 설치
pip install -r requirements.txt
cp .env.example .env              # 환경변수 설정
uvicorn app.main:app --reload
# http://localhost:8000/docs
```

## 🐳 Docker
```bash
docker build -t voice2band-api .
docker run --rm -it -p 8000:8000 --env-file .env voice2band-api
# 또는
docker compose up --build
```

## 📡 엔드포인트

### 1) WebSocket STT (faster‑whisper)
- `GET ws://<host>:8000/api/ws/stt`
- 메시지 형식
```json
# 클라 → 서버
{ "t": "pcm", "sr": 16000, "data": "<base64 pcm16 mono>" }
{ "t": "flush" }

# 서버 → 클라
{ "t": "partial", "text": "부분 인식", "conf": -0.2 }
{ "t": "final", "text": "최종 문장", "conf": -0.1 }
```
- `.env`에서 모델/디바이스 설정
  - `STT_MODEL=tiny|base|small...`
  - `STT_DEVICE=cpu|cuda`
  - `STT_COMPUTE_TYPE=int8|int8_float16|fp16 ...`

### 2) TTS (Piper)
- `POST /api/tts`
```json
{ "text": "안녕하세요, 보이스 투 밴드!" }
```
- 응답: `{ "wav_base64": "..." }` (16-bit WAV 바이트, base64 인코딩)
- 필요 환경변수
  - `PIPER_PATH` : piper 실행 파일 경로
  - `PIPER_MODEL`: onnx 모델 경로 (예: ko_KR-kss-low.onnx)
  - `PIPER_SPEAKER`: 스피커 id (기본 0)

### 3) 프리셋
- `GET /api/presets` : 모든 프리셋
- `POST /api/presets`
```json
{ "name": "house", "data": { "hat_period_ms": 140, "ride_period_ms": 420 } }
```

### 4) 메트릭
- `POST /api/metrics` : 클라이언트에서 성능/사용 통계 전송

### 5) (옵션) 피치 (CREPE/ONNX)
- `POST /api/pitch` : 간단한 래퍼 (샘플/플레이스홀더)
  - 실제 구현 시 프레임/특징 추출을 ONNX I/O에 맞춰 작성 필요

## 🧩 프런트(React/WebAudio) 연결 가이드
- 실시간 오디오는 **브라우저**에서 처리(지연 최소)  
- STT: 마이크 PCM 청크를 **WS로 전송** → partial 결과를 받아 **장르 전환/드랍/콜앤리스폰스** 트리거  
- TTS: 짧은 문장을 **사전합성** 또는 이벤트 시 호출 → `AudioContext.decodeAudioData`로 재생  
- 프리셋/메트릭: 단순 REST 호출

## 📝 참고
- faster‑whisper는 CTranslate2 기반이라 CPU도 충분히 빠릅니다 (tiny/base 모델 권장).
- Piper는 별도 **CLI 바이너리**가 필요합니다. Docker 사용 시 모델/바이너리를 볼륨 마운트하세요.
- 피치는 브라우저 ACF로 충분하면 서버 호출이 필요 없습니다. 더 정교한 F0가 필요할 때만 CREPE를 쓰세요.

행복한 합주 되세요! 🎤🥁🎹
