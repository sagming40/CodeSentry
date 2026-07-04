from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "CodeSentry 서버 살아있음"}