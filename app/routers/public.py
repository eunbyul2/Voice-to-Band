import os
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["public"])

@router.get("/public/kakao-config.js")
def kakao_config():
    key = os.getenv("KAKAO_JS_KEY", "")
    return PlainTextResponse(f"window.KAKAO_JS_KEY='{key}';", media_type="application/javascript")