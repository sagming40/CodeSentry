# backend/orchestrator/_test_assess_risk.py
# 임시 검증용 — 커밋 제외 대상

from backend.orchestrator.llm_client import assess_risk, finalize_action

# ── 1. 실제 API 호출 검증 (지난번에 이미 확인한 부분) ──
print("=== 실제 API 호출 ===")
result = assess_risk(function_name="process_order", complexity=14, threshold=10)
print(result)

# ── 2. finalize_action() 로직만 따로 검증 (가짜 데이터, API 호출 없음) ──
print("\n=== Case 1: confidence 높음 (0.85) + write_test 선택 ===")
fake_high = {"action_type": "write_test", "risk_reason": "테스트용", "confidence": 0.85}
print(finalize_action(fake_high))
# 기대값: final_action_type == "write_test", escalation_source == None

print("\n=== Case 2: confidence 낮음 (0.4) + write_test 선택 → override 발동 기대 ===")
fake_low = {"action_type": "write_test", "risk_reason": "테스트용", "confidence": 0.4}
print(finalize_action(fake_low))
# 기대값: final_action_type == "escalate_human", escalation_source == "confidence_override"

print("\n=== Case 3: confidence 낮음(0.4)인데 모델이 이미 escalate_human 선택 ===")
fake_edge = {"action_type": "escalate_human", "risk_reason": "테스트용", "confidence": 0.4}
print(finalize_action(fake_edge))
# 기대값: escalation_source == "confidence_override"면 안 됨! model_choice로 나와야 정상
# (지난번에 짚었던 "이미 escalate인데 override라고 표시하면 통계 부풀려짐" 그 부분)

print("\n=== Case 4: confidence 높음(0.85) + 모델이 스스로 escalate_human 선택 ===")
fake_model_choice = {"action_type": "escalate_human", "risk_reason": "테스트용", "confidence": 0.85}
print(finalize_action(fake_model_choice))
# 기대값: escalation_source == "model_choice"