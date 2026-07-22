# backend/orchestrator/llm_client.py
import anthropic
from dotenv import load_dotenv
from backend.orchestrator.tools import ASSESS_RISK_TOOL

load_dotenv()  # .env 파일 내용을 현경 변수로 읽어들임

client = anthropic.Anthropic()  # 환경 변수에서 키 자동으로 읽음
MODEL_NAME = "claude-haiku-4-5-20251001"


def assess_risk(function_name: str, complexity: int, threshold: int) -> tuple[dict, dict]:
    """
    findings 테이블에 저장된 위험 코드 1건에 대해 LLM 판단을 요청한다.
    반환값: (action_result, usage)
      - action_result: {"action_type", "risk_reason", "confidence"}
      - usage: {"input_tokens", "output_tokens}
    """  
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1024,
        tools=[ASSESS_RISK_TOOL],
        tool_choice={"type": "tool", "name": "assess_risk"},
        messages=[{
            "role": "user",
            "content": (
                f"다음 함수를 평가하시오.\n"
                f"함수명: {function_name}\n"
                f"순환 복잡도: {complexity} (임계값 {threshold} 초과)\n"
                f"테스트 존재 여부: 없음\n\n"
                f"테스트를 작성해야 하는지, 로직 수정이 필요한지, "
                f"아니면 사람이 검토해야 할지 판단하시오."
            )
        }]
    )
    
    usage = {
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
    }
    
    for block in message.content:
        if block.type == "tool_use":
            return block.input, usage
        
    # tool_use 블록이 하나도 없는 이례적인 경우 대비
    raise RuntimeError("assess_risk 호출에서 tool_use 응답을 받지 못했습니다.")

CONFIDENCE_THRESHOLD = 0.6

def finalize_action(raw_result: dict) -> dict:
    """
    assess_risk()의 원본 응답에 백엔드 안전장치(confidence override)를 적용한다.
    반환값에 raw 값과 최종 확정 값을 모두 포함해 감사(audit) 가능하게 한다.
    """    
    raw_action_type = raw_result["action_type"]
    confidence = raw_result["confidence"]
    
    was_overriden = confidence < CONFIDENCE_THRESHOLD and raw_action_type != "escalate_human"
    final_action_type = "escalate_human" if was_overriden else raw_action_type
    
    return {
        "raw_action_type": raw_action_type,      # 모델이 원래 고른 값
        "final_action_type": final_action_type,  # 백엔드 확정 후 최종 값
        "risk_reason": raw_result["risk_reason"],
        "confidence": confidence,
        "escalation_source": (
            "confidence_override" if was_overriden
            else "model_choice" if final_action_type == "escalate_human"
            else None
        )
    } 
    
# Claude Haiku 4.5 가격 (2026-07 기준, 100만 토큰당 달러)
# 출처: https://www.anthropic.com/news/claude-haiku-4-5 (공식 발표)

PRICE_PER_MILLION_INPUT = 1.0
PRICE_PER_MILLION_OUTPUT = 5.0


def calculate_cost(usage: dict) -> float:
    """
    토튼 사용량을 실제 달러 비용으로 환산한다.
    """    
    input_cost = (usage["input_tokens"] / 1_000_000) * PRICE_PER_MILLION_INPUT
    output_cost = (usage["output_tokens"] / 1_000_000) * PRICE_PER_MILLION_OUTPUT
    return round(input_cost + output_cost, 8)
    