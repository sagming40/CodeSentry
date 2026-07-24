# backend/scanner/run_scan.py

from backend.scanner.walker import find_python_files
from backend.scanner.complexity import analyze_file
from backend.scanner.test_check import has_test_file
from backend.database import SessionLocal, engine
from backend.models import Base, Scan, Finding

COMPLEXITY_THRESHOLD = 10


def create_scan_record(repo_path: str) -> int:
    """
    비유: 병원 접수대에서 "접수증(scan_id)"부터 먼저 끊어주는 것.
    실제 진료(파일 스캔)는 뒤에서 따로 진행하고, 일단 손님에게 접수 번호부터 배정한다.
    DB에 INSERT 한 번후 거의 즉시 반환됨 — API가 기다릴 필요 없는 부분. 
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    scan = Scan(repo_path=repo_path, status="running")
    db.add(scan)
    db.commit()
    db.refresh(scan)
    scan_id = scan.id
    db.close()
    
    return scan_id


def execute_scan(scan_id: int, repo_path: str) -> None:
    """
    비유: 접수증을 받아놓은 뒤 실제 진료 진행(파일 순회 + 복잡도 계산 + 판정 + DB 저장)
    시간이 걸릴 수 있는 작업이라 API 라우터 에서는 이 함수를 백그라운드에 던져 놓고,
    응답은 create_scan_record() 결과만 먼저 반환한다.
    """
    db = SessionLocal()
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    
    try:
        files = find_python_files(repo_path)
        
        for filepath in files:
            results = analyze_file(filepath)
            test_exists = has_test_file(filepath)
            
            for r in results:
                if r["complexity"] >= COMPLEXITY_THRESHOLD and not test_exists:
                    finding = Finding(
                        scan_id=scan_id,
                        file_path=filepath,
                        function_name=r["function_name"],
                        complexity_score=r["complexity"],
                        has_test=test_exists,
                        line_number=r["line_number"],
                        end_line_number=r["end_line_number"],
                        status="found",
                    )
                    db.add(finding)
        
        scan.status = "completed"
        scan.total_files_scanned = len(files)
        db.commit()
    
    except Exception:
        # 스캔 도중 에러가 나도 status가 "running"에서 영원히 멈춰있지 않게
        # (백그라운드 작업이라 실패해도 콘솔에 에러가 보이지 않을 수 있어서,
        # DB에 "failed"로 명확히 남겨두는 게 나중에 확인하기 편함)
        scan.status = "failed"
        db.commit()
        raise
    
    finally:
        db.close()                


def run_scan(repo_path: str) -> int:
    """
    기존 CLI(`python -m backend.scanner.run_scan`) 실행용 동기 래퍼.
    접수(create_scan_record) → 진료(execute_scan)를 순서대로 이어서 처리해버리는 것.
    API 라우터에서는 이 함수를 쓰지 않고 두 단계를 따로 호출함(하나는 즉시, 하나는 백그라운드).
    """
    scan_id = create_scan_record(repo_path)
    execute_scan(scan_id, repo_path)
    return scan_id


if __name__ == "__main__":
    scan_id = run_scan("backend")
    print(f"스캔 완료. scan_id={scan_id}") 
           