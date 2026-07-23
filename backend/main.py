from fastapi import FastAPI
from backend.routers import approvals

app = FastAPI()

app.include_router(approvals.router)

@app.get("/")
def read_root():
    return {"message": "CodeSentry 서버 살아있음"}
