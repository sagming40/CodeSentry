import anthropic

client = anthropic.Anthropic() # 환경변수에서 키를 자동으로 찾아 읽음

# 설계 문서 6장의 assess_risk tool 스펙 그대로
tools = [
    {
        "name": "assess_risk",
        "description": "코드 조각의 위험도를 판단하고 조치 방향을 결정한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "enum": ["write_test", "propose_fix", "escalate_human"],
                    "description": "이 코드에 대해 취해야 할 조치"
                },
                "risk_reason": {
                    "type": "string",
                    "description": "왜 위험하다고 판단했는지 근거"
                },
                "confidence": {
                    "type": "number",
                    "description": "판단에 대한 확신도 (0~1 사이)"
                }
            },
            "required": ["action_type", "risk_reason", "confidence"]
        }
    }
]

message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "tool", "name": "assess_risk"},
    messages=[{
        "role": "user",
        "content": (
            "다음 함수를 평가해줘.\n"
            "함수명: process_order\n"
            "순환 복잡도: 14 (임계값 10 초과)\n"
            "테스트 존재 여부: 없음\n\n"
            "테스트를 작성해야 할지, 로직 수정이 필요한지, "
            "아니면 사람이 검토해야 할지 판단해줘."
        )
    }]
)

for block in message.content:
    if block.type == "tool_use":
        print("action_type:", block.input["action_type"]) 
        print("risk_reason:", block.input["risk_reason"]) 
        print("confidence:", block.input["confidence"]) 