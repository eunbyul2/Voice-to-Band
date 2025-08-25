# routers/metrics.py
from fastapi import APIRouter, Request

router = APIRouter(tags=["metrics"])

# Prometheus 스크레이프용 GET /metrics 는 main.py가 담당.
# 이 엔드포인트는 임의 메트릭/로그 push용이므로 경로를 분리.
@router.post("/metrics/push")
async def metrics_push(req: Request):
    payload = await req.json()
    # TODO: pushgateway/Loki/DB 연동
    return {"ok": True, "received": payload}