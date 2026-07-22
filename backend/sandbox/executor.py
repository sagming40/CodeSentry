# backend/sandbox/executor.py — 격리 실행기 (subprocess 기반, Docker 아님 — 설계문서 5.3/8장)

import subprocess
import sys
import platform

# resource 모듈은 POSIX(Linux/Mac) 전용이라 Windows에선 import 자체가 실패함.
# 그래서 "일단 시도해보고 안 되면 없는 셈 친다" 식으로 조건부 import 처리.
# 비유: 자물쇠가 걸려있는 사물함과 걸려있지 않은 사물함
# 자물쇠(resource)가 있으면 걸고, 없으면 그냥 짐(코드)을 넣어놓되 그 사실을 인지하고 있는 것.
IS_POSIX = platform.system() != "Windows"
if IS_POSIX:
    import resource
    
MAX_MEMORY_MB = 256  # 테스트 코드 하나 실행하는데에는 충분 (일반 pytest 단위 테스트 기준)


def _limit_memory():
    """
    subprocess.run()의 preexec_fn으로 전달되는 함수.
    자식 프로세스(pytest를 실제로 실행하는 프로세스)가 "태어나는 순간" 스스로에게
    "나는 이 이상의 메모리를 쓰지 못한다"는 한도를 건다.
    비유: 신용카드 자체에 한도를 미리 걸어두는 것 —
    한도를 넘는 순간 카드(프로세스)가 알아서 결제(메모리 할당) 거부.
    """     
    limit_bytes = MAX_MEMORY_MB * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))
    
    
def run_test_isolated(test_code_path: str, timeout_sec: int = 10) -> dict:
    """
    주어진 테스트 파일(test_code_path)을 격리된 별도 프로세스에서 pytest로 실행한다.
    
    격리 수단:
      - 별도 프로세스(subprocess) — 이 프로세스가 죽어도 메인 서버는 죽지 않음
      - 메모리 상한 (POSIX만 적용됨, Windows는 미적용 — 위 IS_POSIX 참고)
      - 실행 시간 제한(timeout_sec) — 무한루프 코드가 서버 전체를 마비시키는 것을 방지
      
    반환값: {"passed": bool, "output": str, "timed_out": bool}  
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_code_path, "--tb=short"],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            preexec_fn=_limit_memory if IS_POSIX else None,
        )
        return {
            "passed": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "timed_out": False,
        }
        
    except subprocess.TimeoutExpired:
        # timeout_sec 안에 안 끝나면 subprocess가 강제 종료되며 여기로 옴.
        # 무한루프였을 수도 있으니, "실패"로 취급하고 그 사실을 output에 남겨둠 —
        # 나중에 generation_manager가 이 output을 재생성 프롬프트에 그대로 넘기므로
        # "타임아웃이 났었다"는 정보 자체가 재시도에 도움이 됨.
        return {
            "passed": False,
            "output": f"[timeout] {timeout_sec}초 안에 실행이 끝나지 않아 강제 종료함.",
            "timed_out": True,
        }    
        