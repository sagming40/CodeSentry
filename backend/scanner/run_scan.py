# backend/scanner/run_scan.py

from backend.scanner.walker import find_python_files
from backend.scanner.complexity import analyze_file
from backend.scanner.test_check import has_test_file
from backend.database import SessionLocal, engine
from backend.models import Base, Scan, Finding

COMPLEXITY_THRESHOLD = 10

def run_scan(repo_path: str) -> int:
    Base.metadata.create_all(bind=engine)  # 테이블 없으면 만들어줌
    db = SessionLocal()
    
    scan = Scan(repo_path=repo_path, status="running")
    db.add(scan)
    db.commit()
    db.refresh(scan)   # DB가 채번한 scan.id를 Python 객체로 다시 가져옴
    scan_id = scan.id  # ← 여기서 미리 복사해둠 (이후엔 이 변수만 씀)
    
    files = find_python_files(repo_path)
    
    for filepath in files:
        results = analyze_file(filepath)
        test_exists = has_test_file(filepath)
        
        for r in results:
            if r["complexity"] >= COMPLEXITY_THRESHOLD and not test_exists:
                finding = Finding(
                    scan_id=scan_id,  # ← scan.id 대신 scan_id 변수 씀
                    file_path=filepath,
                    function_name=r["function_name"],
                    complexity_score=r["complexity"],
                    has_test=test_exists,
                    line_number=r["line_number"],           # 신규 추가
                    end_line_number=r["end_line_number"],   # 신규 추가
                    status="found",
                )
                db.add(finding)
        
    scan.status = "completed"
    scan.total_files_scanned = len(files)
    db.commit()
    db.close()
    
    return scan_id  # scan.id 아니고 scan_id

if __name__ == "__main__":
    scan_id = run_scan("backend")
    print(f"스캔 완료. scan_id={scan_id}") 
           