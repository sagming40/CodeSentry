import os

def find_python_files(repo_path: str) -> list[str]:
    """저장소 안의 모든 .py 파일 경로를 리스트로 반환"""
    excluded_dirs = {"venv", ".venv", "__pycache__", "node_modules", ".git"}
    py_files = []
    
    for root, dirs, files in os.walk(repo_path):
        # dirs를 제자리에서 수정하면 os.walk가 그 폴더들은 아예 안 들어감
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for filename in files:
            if filename.endswith(".py"):
                py_files.append(os.path.join(root, filename))
                
    return py_files
            