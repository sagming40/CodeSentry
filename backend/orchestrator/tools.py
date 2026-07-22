# backend/orchestrator/tools.py

ASSESS_RISK_TOOL = {
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
                "description": "판단(action_type)에 대한 확신도 (0~1 사이)"
            }
        },
        "required": ["action_type", "risk_reason", "confidence"]
    }
}