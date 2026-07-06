import os

def has_test_file(source_filepath: str) -> bool:
    """소스 파일에 대응하는 테스트 파일이 있는지 파일명 패턴으로 확인"""
    dir_path = os.path.dirname(source_filepath)
    filename = os.path.basename(source_filepath)
    name_without_ext = filename[:-3]    # ".py" 제거
    
    candidates = [
        f"test_{filename}",             # test_scanner.py
        f"{name_without_ext}_test.py"   # scanner_test.py
    ]
    
    # 같은 폴더
    for c in candidates:
        if os.path.exists(os.path.join(dir_path, c)):
            return True
        
    # tests/ 하위 폴더
    tests_dir = os.path.join(dir_path, "tests")
    for c in candidates:
        if os.path.exists(os.path.join(tests_dir, c)):
            return True
        
    return False  
          