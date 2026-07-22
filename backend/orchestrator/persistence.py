# backend/orchestrator/persistence.py

from backend.database import SessionLocal
from backend.models import LlmCall, Action


def save_action(
    finding_id: int, 
    usage: dict, 
    cost: float, 
    finalized: dict, 
    tool_name: str = "assess_risk",
    attempt_number: int = 1
  ) -> dict:
    """
    LLM 판단 1건의 결과를 llm_calls, actions 테이블에 저장한다.
    finalized는 finalize_action()의 반환값을 그대로 받는다.
    반환값: {"llm_call_id", "action_id"}
    """
    db = SessionLocal()
    
    llm_call = LlmCall(
        finding_id=finding_id,
        tool_name=tool_name,
        input_tokens=usage["input_tokens"],
        output_tokens=usage["output_tokens"],
        estimated_cost_usd=cost,
    )
    db.add(llm_call)
    
    action = Action(
        finding_id=finding_id,
        raw_action_type=finalized["raw_action_type"],
        final_action_type=finalized["final_action_type"],
        risk_reason=finalized["risk_reason"],
        confidence=finalized["confidence"],
        escalation_source=finalized["escalation_source"],
        attempt_number=attempt_number,
    )
    db.add(action)
    
    db.commit()
    db.refresh(llm_call)
    db.refresh(action)
    
    # 세션을 닫기 전 필요한 값을 미리 변수로 복사 (지난번 DetachedInstanceError 교훈 그대로 적용)
    llm_call_id = llm_call.id
    action_id = action.id
    db.close()
    
    return {"llm_call_id": llm_call_id, "action_id": action_id}
     