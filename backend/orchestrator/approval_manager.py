# backend/orchestrator/approval_manager.py

from backend.database import SessionLocal
from backend.models import Approval
from datetime import datetime


def create_approval(action_id: int) -> int:
    """
    propose_fix 결과 하나를 결재함(approvals)에 '대기' 상태로 올린다.
    비유: 문서를 결재함에 넣는 행위 자체 — 아직 아무도 도장을 찍지 않은 상태
    반환값: 생성된 approval의 id 
    """
    db = SessionLocal()
    
    approval = Approval(
        action_id=action_id,
        status="pending",
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    
    approval_id = approval.id  # DetachedInstanceError 방지 — 닫기 전에 미리 복사
    db.close()
    
    return approval_id
