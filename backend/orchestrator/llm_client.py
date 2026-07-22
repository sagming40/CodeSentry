# backend/orchestrator/llm_client.py
import anthropic
from dotenv import load_dotenv
from backend.orchestrator.tools import ASSESS_RISK_TOOL, GENERATE_TEST_TOOL, PROPOSE_FIX_TOOL

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


def generate_test(function_name: str, function_code: str, risk_reason: str,
                    previous_failure: str | None = None) -> tuple[dict, dict]:
    """
    write_test로 판정된 함수에 대해 pytest 테스트 코드를 생성 요청한다.
    previous_failure: 재시도(2차 시도)일 때만 값이 들어옴 — 1차 시도의 pytest 실패 로그.
                      None이면 "첫 번째 시도"라는 뜻.
    반환값: (generate_result, usage) 
      - generate_result: {"test_code", "covered_cases"}                  
    """
    # 자판기에 비유하면: previous_failure는 "직전에 뽑았다가 고장난 음료" 정보.
    # 그걸 알려주면 자판기(LLM)가 같은 버튼을 눌러도 다른(더 나은) 음료를 뽑아줄 확률이 올라감.
    retry_note = (
        f"\n\n[참고] 이전 시도가 다음 이유로 실패했다. 같은 실수를 반복하지 말 것:\n{previous_failure}"
        if previous_failure else ""
    )
    
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=3000,    # 1500 → 3000 (테스트 코드는 원래 장황해질 수 있는 산출물이라 여유 확보) 
        tools=[GENERATE_TEST_TOOL],
        tool_choice={"type": "tool", "name": "generate_test"},
        messages=[{
            "role": "user",
            "content": (
                f"다음 함수를 검증할 pytest 테스트 코드를 작성하시오.\n"
                f"함수명: {function_name}\n"
                f"코드: {function_code}\n\n"
                f"위험 판단 근거: {risk_reason}"
                f"{retry_note}"
            )
        }]
    )
    
    # max_tokens 한도에 걸려 응답이 중간에 잘렸는지 먼저 확인
    # 비유: 택배 상자(max_tokens)가 작아서 물건(응답)이 잘려나간 채로 도착한 걸
    # 모르고 뜯어보다가 "구성품이 없네?"라고 당황하는 대신, 상자 겉면에 "파손/부족" 딱지가
    # 붙어있는지부터 확인하는 것 — stop_reason이 그 딱지 역할을 함
    if message.stop_reason == "max_tokens":
        raise RuntimeError(
            "generate_test 응답이 max_tokens 제한에 걸려 중간에 잘렸습니다. "
            "max_tokens를 늘리거나 함수 코드가 지나치게 긴 건 아닌지 확인하세요."
        )
    
    usage = {
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
    }
    
    for block in message.content:
        if block.type == "tool_use":
            return block.input, usage
    
    raise RuntimeError("generate_test 호출에서 tool_use 응답을 받지 못했습니다.")


def propose_fix(function_name: str, function_code: str, risk_reason: str) -> tuple[dict, dict]:
    """
    propose_fix로 판정된 함수에 대해 수정안(diff)을 생성 요청한다.
    반환값: (fix_result, usage)
      - fix_result: {"fix_diff", "fix_explanation"}  
    """
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=3000,    # 여기도 1500 → 3000
        tools=[PROPOSE_FIX_TOOL],
        tool_choice={"type": "tool", "name": "propose_fix"},
        messages=[{
            "role": "user",
            "content": (
                f"다음 함수에 대한 수정안을 diff 형태로 제안하시오.\n"
                f"함수명: {function_name}\n"
                f"코드:\n{function_code}\n\n"
                f"위험 판단 근거: {risk_reason}"
            )
        }]
    )
    
    if message.stop_reason == "max_tokens":
        raise RuntimeError(
            "propose_fix 응답이 max_tokens 제한에 걸려 중간에 잘렸습니다. "
            "max_tokens를 늘리거나 함수 코드가 지나치게 긴 건 아닌지 확인하세요."
        )
    
    usage = {
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
    }
    
    for block in message.content:
        if block.type == "tool_use":
            return block.input, usage
    
    raise RuntimeError("propose_fix 호출에서 tool_use 응답을 받지 못했습니다.")    
    
    
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
    