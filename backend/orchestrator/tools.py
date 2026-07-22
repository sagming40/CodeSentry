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

GENERATE_TEST_TOOL = {
    "name": "generate_test",
    "description": "주어진 함수를 검증할 pytest 테스트 코드를 생성한다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "test_code": {
                "type": "string",
                # test_code는 "완성된 요리" — 그대로 접시(파일)에 담아서
                # 손님(sandbox executor)한테 내보내면 됨. 중간 설명 필요 없음.
                "description": "그대로 파일에 저장해 pytest로 실행 가능한 완전한 테스트 코드"
            },
            "covered_cases": {
                "type": "string",
                # covered_cases는 요리에 붙는 "메뉴판 설명" — 실행에는 안 쓰이지만
                # 사람이 나중에 "이 테스트가 뭘 검증하는지" 한눈에 보려고 붙여두는 라벨
                "description": "이 테스트가 어떤 케이스들을 검증하는지 간단히 요약"
            }
        },
        "required": ["test_code", "covered_cases"]
    }
}

PROPOSE_FIX_TOOL = {
    "name": "propose_fix",
    "description": "위험하다고 판단된 코드에 대한 수정안을 diff 형태로 제안한다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "fix_diff": {
                "type": "string",
                # fix_diff는 "고쳐야 할 부분에 붙이는 포스트잇" — 원본을 바로 바꾸는 게 아니라
                # "이렇게 바꾸면 어떨까요?"라고 제안만 하는 것. 실제 적용은 사람 승인(EPIC 4) 이후.
                "description": "unified diff 형식의 코드 수정 제안"
            },
            "fix_explanation": {
                "type": "string",
                "description": "왜 이렇게 고쳐야 하는지에 대한 설명 (사람이 승인 여부를 판단할 근거)"
            } 
        },
        "required": ["fix_diff", "fix_explanation"]
    }
}
