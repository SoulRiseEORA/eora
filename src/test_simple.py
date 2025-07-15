from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/test")
async def test():
    return {"message": "테스트 성공", "status": "ok"}

@app.get("/api/test")
async def api_test():
    return {"message": "API 테스트 성공", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 간단한 테스트 서버 시작...")
    uvicorn.run(app, host="127.0.0.1", port=8002) 