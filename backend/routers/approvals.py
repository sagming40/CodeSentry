# backend/routers/approvals.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.orchestrator.approval_manager import approve_approval, reject_approval

router = APIRouter(prefix="/approvals", tags=["approvals"])


class ApprovalDecision(BaseModel):
    decision: str  # "approve" 또는 "reject"
    
    
@router.patch("/{approval_id}")
def update_approval(approval_id: int, body: ApprovalDecision):
    """
    비유: 결재함 문서를 하나 열어서 승인/반려 도장을 찍는 창구
    """        
    if body.decision == "approve":
        try:
            return approve_approval(approval_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    elif body.decision == "reject":
        try:
            return reject_approval(approval_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=422, detail="decision은 'approve' 또는 'reject'여야 함")        
