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

def save_generation_action(
    finding_id: int,
    usage: dict,
    cost: float,
    tool_name: str,
    action_type: str,
    content: str,
    detail: str,
    attempt_number: int,
    execution_status: str,
) -> dict:
    """
    generate_test(또는 propose_fix) 결과 1건을 llm_calls, actions 테이블에 저장한다.
    save_action()과 거의 같은 구조지만, 판단(assess_risk)이 아니라
    "생성물"을 저장하는 용도라 content/detail/execution_status를 채운다는 게 다름.
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
    
    # 생성 액션 ㅡ 사람의 승인/재검토 대상 → 백엔드가 override할 대상이 아님
    # raw_action_type == final_action_type로 그냥 동일하게 둠 (escalation_source도 해당 없음)
    action = Action(
        finding_id=finding_id,
        raw_action_type=action_type,
        final_action_type=action_type,
        risk_reason="",                     # 판단 단계가 아니라 생성 단계라 여기선 안 씀
        confidence=0.0,                     # 마찬가지
        escalation_source=None,
        attempt_number=attempt_number,
        content=content,
        detail=detail,
        execution_status=execution_status,  # ← 신규 추가 (이전엔 파라미터만 받고 안 씀)  
    )
    db.add(action)
    
    db.commit()
    db.refresh(llm_call)
    db.refresh(action)
    
    llm_call_id = llm_call.id
    action_id = action.id
    db.close()
    
    return {"llm_call_id": llm_call_id, "action_id": action_id}
     