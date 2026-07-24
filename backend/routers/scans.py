# backend/routers/scans.py

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from backend.scanner.run_scan import create_scan_record, execute_scan

router = APIRouter(prefix="/scans", tags=["scans"])


class ScanCreateRequest(BaseModel):
    """
    비유: 스캔 접수 신청서 — "어느 스캔 저장소를 스캔해주세요."라는 요청 한 줄 
    """
    repo_path: str
    
    
class ScanCreateResponse(BaseModel):
    """
    비유: 접수증 — "요청 접수 했고 번호는 이겁니다, 지금 진행 중 입니다."
    """    
    scan_id: int
    status: str
    

@router.post("", response_model=ScanCreateResponse, status_code=202)
def trigger_scan(body: ScanCreateRequest, background_tasks: BackgroundTasks):
    """
    비유: 병원 접수대 — 접수증(scan_id)을 먼저 끊어서 손님한테 주고,
    실제 진료(파일 순회 + 판정 + DB 저장)는 뒤에서 진행 시킨다.
    클라이언트는 스캔(접수)이 끝날 때 까지 기다리지 않고 바로 scan_id(접수증)를 받아서,
    (다음 Task인) WS로 진행 상황을 구독하러 갈 수 있다.
    
    status_code=202(Accepted)를 쓴 이유: "요청은 받았으나 아직 끝나지 않았음"이라는 의미가
    200(성공, 이미 완료)보다 지금 상황에 더 정확한 표현임.
    """    
    scan_id = create_scan_record(body.repo_path)
    background_tasks.add_task(execute_scan, scan_id, body.repo_path)
    return ScanCreateResponse(scan_id=scan_id, status="running")
    