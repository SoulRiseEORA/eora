from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test", response_class=HTMLResponse)
async def test():
    return HTMLResponse(content="<h1>테스트 성공!</h1><p>서버가 정상 작동합니다.</p>")

if __name__ == "__main__":
    print("🚀 간단한 테스트 서버를 시작합니다...")
    print("📍 주소: http://127.0.0.1:8003")
    print("📋 테스트 페이지: http://127.0.0.1:8003/test")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8003) 