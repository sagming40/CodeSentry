# backend/routers/ws_scans.py

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.database import SessionLocal
from backend.models import Scan

router = APIRouter(tags=["scans"])

POLL_INTERVAL_SECONDS = 0.5  # DB를 얼마나 자주 들여다볼지 (너무 짧으면 DB 부하, 너무 길면 느려 보임)


@router.websocket("/ws/scans/{scan_id}")
async def scan_progress_ws(websocket: WebSocket, scan_id: int):
    """
    비유: 택배 배송 조회 페이지를 새로고침하여 "몇 초마다 자동 갱신"해주는 것과 같음.
    진짜 이벤트 push(스캔 쪽에서 직접 알림을 쏘는 방식)는 아니고,
    서버가 짧은 간격으로 DB를 확인해서 바뀐 상태를 계속 흘려보내주는 폴링 방식.
    (규모가 커지면 진짜 pub/sub 구조로 바꾸는 걸 검토할 수 있음 — 지금은 이 정도로 충분)
    """
    await websocket.accept()
    
    try:
        while True:
            db = SessionLocal()
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            db.close()
            
            if scan is None:
                await websocket.send_json({"error": f"scan id{scan_id}를 찾을 수 없음"})
                break
            
            await websocket.send_json({
                "scan_id": scan.id,
                "status": scan.status,
                "files_processed": scan.files_processed,
                "total_files_scanned": scan.total_files_scanned,
            })
            
            if scan.status in ("completed", "failed"):
                break
            
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            
    except WebSocketDisconnect:
        # 클라이언트가 브라우저 닫기 등으로 먼저 연결을 끊은 경우 — 에러 아니고 조용히 빠져나감
        pass        
    