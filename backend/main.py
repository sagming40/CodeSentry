from fastapi import FastAPI
from backend.routers import approvals, findings # ← Task 5-1 findings 추가

app = FastAPI()

app.include_router(approvals.router)
app.include_router(findings.router)   # ← 이 줄 추가(Task 5-1)

@app.get("/")
def read_root():
    return {"message": "CodeSentry 서버 살아있음"}
