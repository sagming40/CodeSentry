from radon.complexity import cc_visit

def analyze_file(filepath: str) -> list[dict]:
    """파일 하나를 읽어서 함수별 순환 복잡도를 계산"""
    try:
        with open(filepath, encoding="utf-8") as f:
            code = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return [] # 읽을 수 없는 파일은 그냥 스킵
    
    try:
        blocks = cc_visit(code)
    except SyntaxError:
        return [] # 문법 오류 있는 파일도 스킵 (radon이 Parsing 못함)
    
    results = []
    for block in blocks:
        results.append({
            "function_name": block.name,
            "complexity": block.complexity,
            "line_number": block.lineno,
        })
    return results
                