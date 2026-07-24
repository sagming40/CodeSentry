from fastapi import FastAPI
from backend.routers import approvals, findings, scans, ws_scans 

app = FastAPI()

app.include_router(approvals.router)
app.include_router(findings.router)   # ← 이 줄 추가(Task 5-1)
app.include_router(scans.router)      # ← 이 줄 추가(Task 5-2)
app.include_router(ws_scans.router)   # ← 이 줄 추가(Task 5-3)

@app.get("/")
def read_root():
    return {"message": "CodeSentry 서버 살아있음"}
