# backend/orchestrator/run_pipeline.py

from backend.database import SessionLocal
from backend.models import Finding
from backend.orchestrator.llm_client import assess_risk, finalize_action, calculate_cost
from backend.orchestrator.persistence import save_action

# run_scan.py의 COMPLEXITY_THRESHOLD와 같은 값 — 판단 시 프롬프트에 넣어줄 임계값
COMPLEXITY_THRESHOLD = 10


def run_pipeline() -> int:
    """
    status='found' 상태인 모든 Finding에 대해 LLM 판단을 실행하고,
    결과를 llm_calls/actions 테이블에 저장한다.
    반환값: 처리한 finding 개수
    """
    db = SessionLocal()
    # status='found' → 아직 오케스트레이터가 손대지 않은 것만 대상으로 함
    targets = db.query(Finding).filter(Finding.status == "found").all()
    findings_ids = [(f.id, f.function_name, f.complexity_score) for f in targets]
    db.close()  # 조회만 하고 바로 닫음 (이후엔 findings_ids 변수만 사용)
    
    processed_count = 0
    
    for finding_id, function_name, complexity in findings_ids:
        print(f"[{finding_id}] {function_name} (complexity={complexity}) 판단 중...")
        
        raw_result, usage = assess_risk(
            function_name=function_name,
            complexity=complexity,
            threshold=COMPLEXITY_THRESHOLD,
        )
        finalized = finalize_action(raw_result)
        cost = calculate_cost(usage)
        
        save_action(finding_id=finding_id, usage=usage, cost=cost, finalized=finalized)
        
        # Finding 상태 갱신 — "found"에서 판단이 끝났다는 걸 표시 
        db = SessionLocal()
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        finding.status = finalized["final_action_type"]  # write_test / propose_fix / escalate_human
        db.commit()
        db.close()
        
        print(f"  → {finalized['final_action_type']} (confidence={finalized['confidence']})")
        processed_count += 1
    
    return processed_count

if __name__ == "__main__":
    count = run_pipeline()
    print(f"\n총 {count}건 처리 완료.") 
       