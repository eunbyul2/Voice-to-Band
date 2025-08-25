# app/routers/presets.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json, os

router = APIRouter(tags=["presets"])

# 컨테이너/서버 어디서 실행해도 안정적인 절대경로 사용
DATA_DIR = os.getenv("DATA_DIR", "/data")
os.makedirs(DATA_DIR, exist_ok=True)
PRESETS_PATH = os.path.join(DATA_DIR, "presets.json")

class Preset(BaseModel):
    name: str
    data: dict

@router.get("/presets")
def list_presets():
    if not os.path.exists(PRESETS_PATH):
        return {}
    try:
        with open(PRESETS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 파일이 깨진 경우라도 200과 빈 객체로 대응
        return {}

@router.post("/presets")
def upsert_preset(p: Preset):
    db = {}
    if os.path.exists(PRESETS_PATH):
        try:
            with open(PRESETS_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
        except json.JSONDecodeError:
            db = {}

    db[p.name] = p.data

    # 원자적 쓰기: 임시파일에 쓰고 rename
    tmp_path = PRESETS_PATH + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, PRESETS_PATH)
    except Exception as e:
        # 실패 시 임시파일 제거 시도
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        finally:
            raise HTTPException(status_code=500, detail=str(e))

    return {"ok": True}