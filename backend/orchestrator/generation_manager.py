# backend/orchestrator/generation_manager.py

from backend.database import SessionLocal
from backend.models import Finding, Action
from backend.sandbox.executor import run_test_isolated
from backend.orchestrator.llm_client import generate_test, calculate_cost
from backend.orchestrator.persistence import save_generation_action
import tempfile
import os

MAX_ATTEMPTS = 2  # "1회 재시도"= 최초 시도 1번 + 재시도 1번 = 총 2번


def process_write_test(finding_id: int, function_name: str, function_code: str, risk_reason: str) -> None:
    """
    write_test로 판정된 finding 하나를 끝까지 처리한다.
    generate_test → 샌드박스 실행 → (실패 시) 실패 로그 포함 재생성 → 재실행
    → 최종 상태(passed/needs_review)를 Findings에 반영한다.
    """
    previous_failure = None  # 1차 시도는 "이전 실패"가 없으니 None
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            # 1. LLM에게 테스트 코드 생성 요청 (재시도라면 이전 실패 로그도 같이 넘김)
            gen_result, usage = generate_test(
                function_name=function_name,
                function_code=function_code,
                risk_reason=risk_reason,
                previous_failure=previous_failure
        )
        except RuntimeError as e:
            # generate_test 자체가 실패한 경우(max_tokens 잘림 등)도
            # "이번 시도는 실패했다"로 취급하고 재시도 흐름에 그대로 태움.
            # 비유: 자판기에서 음료가 아예 나오지 않은 것도 "실패한 시도"로 카운트하는 것 —
            # 음료가 나오긴 나왔는데 다른 맛으로 나온 것과, 아예 나오지 않은 것은 결과적으로 "다시 눌러봐야 한다"는 점은 같음
            previous_failure = f"[생성 자체 실패] {e}"
            continue  # 이번 attempt는 여기서 끝, 다음 attempt로
        
        cost = calculate_cost(usage)
        
        # 2. 생성된 test_code를 임시 파일로 저장
        # 비유: 요리(test_code)를 접시(임시 파일)에 담아야 손님(pytest)이 먹어볼 수 있음
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_test.py", delete=False, encoding="utf-8"
        ) as f:
            f.write(gen_result["test_code"])
            temp_path = f.name
            
        try:
            # 3. 샌드박스에서 격리 실행
            exec_result = run_test_isolated(temp_path)
        finally:
            # 성공/실패 상관없이 임시 파일은 항상 정리 (디스크에 흔적 안 남기기)
            os.remove(temp_path)
            
        execution_status = "passed" if exec_result["passed"] else "failed"
        
        # 4. 이번 시도 결과를 DB에 저장 (성공이든 실패든 매 attempt마다 row 하나씩)
        save_generation_action(
            finding_id=finding_id,
            usage=usage,
            cost=cost,
            tool_name="generate_test",
            action_type="write_test",
            content=gen_result["test_code"],
            detail=gen_result["covered_cases"],
            attempt_number=attempt,
            execution_status=execution_status,
        )
        
        if exec_result["passed"]:
            _update_finding_status(finding_id, "passed")
            return  # 성공했으니 재시도 루프 여기서 종료
        
        # 실패했으면 다음 시도를 위해 실패 로그를 기억해둠
        previous_failure = exec_result["output"]
        
    # for 루프를 MAX_ATTEMPTS번 다 돌고도 여기 도달했다는 건 마지막 시도까지 실패했다는 뜻
    _update_finding_status(finding_id, "needs_review")
    
    
def _update_finding_status(finding_id: int, new_status: str) -> None:
    """Finding.status를 갱신한다. run_pipeline.py의 패턴과 동일하게 세션을 짧게 열고 닫음."""
    db = SessionLocal()
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    finding.status = new_status
    db.commit()
    db.close()
    
def run_write_test_phase() -> int:
    """
    status='write_test' 상태인 모든 Finding에 대해 process_write_test()를 실행한다.
    run_piprline()의 assess_risk 자동순회와 같은 패턴 — 판단 단계가 아니라 생성 단계 버전.
    반환값: 처리한 finding 개수
    """
    db = SessionLocal()
    targets = db.query(Finding).filter(Finding.status == "write_test").all()
    
    target_data = []
    for f in targets:
        # 이 finding을 write_test로 판단했던 assess_risk의 risk_reason을 가져옴
        # (가장 최근 것 하나 — assess_risk는 finding당 보통 1번만 호출되니 문제없음)
        last_judgement = (
            db.query(Action)
            .filter(Action.finding_id == f.id, Action.final_action_type == "write_test")
            .order_by(Action.created_at.desc())
            .first()
        )
        target_data.append((
            f.id, f.file_path, f.function_name,
            f.line_number, f.end_line_number,
            last_judgement.risk_reason if last_judgement else "",
        ))
    db.close()  # 조회만 하고 바로 닫음 (run_pipeline.py와 같은 패턴)
    
    processed_count = 0
    for finding_id, file_path, function_name, line_number, end_line_number, risk_reason in target_data:
        print(f"[{finding_id}] {function_name} 테스트 생성 중...")
        
        function_code = _read_function_source(file_path, line_number, end_line_number)
        process_write_test(
            finding_id=finding_id,
            function_name=function_name,
            function_code=function_code,
            risk_reason=risk_reason,
        )
        processed_count += 1
        
    return processed_count                                
    

def _read_function_source(file_path: str, line_number: int, end_line_number: int) -> str:
    """
    파일에서 함수 하나의 소스코드만 정확히 잘라서 읽어온다.
    비유: 책 한 권(file_path) 전체를 다 주는게 아니라,
    "몇 페이지부터 몇 페이지까지가 이 챕터다"(line_number ~ end_line_number)라고
    알려주면 그 챕터만 복사해서 건네주는 것.
    """
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()
        
    # 리스트 인덱스는 0부터 시작하는데 radon의 line_number는 1부터 시작(사람이 세는 방식)이라
    # line_number - 1 해줘야 실제 그 줄부터 정확히 잘림.
    # end_line_number는 슬라이싱 끝 지점이라 그대로 써도 "그 줄까지 포함"이 맞음
    # (파이썬 슬라이싱 lst[a:b]는 b번째 "직전"까지인데, 1-based → 0-based 변환 상쇄로 딱 맞아떨어짐)
    function_lines = lines[line_number - 1 : end_line_number]
    return "".join(function_lines)    
     