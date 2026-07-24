from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import approvals, findings, scans, ws_scans 

app = FastAPI()

# 비유: 건물 정문 경비한테 "5173번 방에서 오는 사람은 통과시켜라" 명단을 미리 등록해두는 것
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite 개발 서버 주소
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(approvals.router)
app.include_router(findings.router)   # ← 이 줄 추가(Task 5-1)
app.include_router(scans.router)      # ← 이 줄 추가(Task 5-2)
app.include_router(ws_scans.router)   # ← 이 줄 추가(Task 5-3)

@app.get("/")
def read_root():
    return {"message": "CodeSentry 서버 살아있음"}
