# backend/routers/findings.py

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from backend.database import SessionLocal
from backend.models import Finding

router = APIRouter(prefix="/findings", tags=["findings"])


class FindingOut(BaseModel):
    """
    비유: Finding 테이블(창고 재고 원본, SQLAlchemy 객체)을 그대로 밖으로 내보내지 않고,
    API 응답용으로 필요한 항목만 담아서 포장하는 '배송 상자'.
    (DB 원본을 그대로 노출하면 나중에 컬럼 하나 바꿀 때 API 응답까지 통째로 흔들리니까,
     이 상자 안에 뭘 담을지는 내가 직접 정한다.)
    """
    
    # SQLAlchemy 객체(Finding 인스턴스)를 바로 넣어도 알아서 필드를 꺼내 담게 허용하는 옵션
    # (이게 없으면 "Dictionary만 받는다"고 pydantic이 거부함)
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    scan_id: int
    file_path: str
    function_name: str
    complexity_score: int
    has_test: bool
    status: str
    line_number: Optional[int] = None
    end_line_number: Optional[int] = None
    
    
@router.get("", response_model=list[FindingOut])
def list_findings(
    status: Optional[str] = Query(
        default=None,
        description="findings.status 값으로 필터 (예: found, awaiting_approval, fix_applied 등). 안 주면 전체 조회."
    )
):
    """
    비유: 창고 전체 재고 목록을 보여주는 창구.
    status를 지정하면 "그 상태인 것만" 걸러서 보여주고(편의점에서 '유통기한 임박'만 추려내듯),
    지정 하지 않으면 창고에 있는 걸 전부 다 보여준다.
    """
    db = SessionLocal()
    query = db.query(Finding)
    if status is not None:
        query = query.filter(Finding.status == status)
    findings = query.all()
    db.close()
    return findings 


@router.get("/{finding_id}", response_model=FindingOut)
def get_finding(finding_id: int):
    """
    비유: 창고 재고 중 바코드(id) 하나로 특정 물건 하나만 딱 집어서 꺼내오는 것.
    빈 화면만 보여주면 헷갈리기 쉬우므로,
    없는 바코드를 스캔하면 "그런 물건 없음(404)"으로 명확히 알려주는 게 자연스러움.
    """
    db = SessionLocal()
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    db.close()
    
    if not finding:
        raise HTTPException(status_code=404, detail=f"finding id={finding_id}를 찾을 수 없음") 
    return finding      
    