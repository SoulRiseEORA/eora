#!/usr/bin/env python3
"""
간단한 테스트 서버 - 기본 기능 확인용
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime
import logging
import socket
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 템플릿 설정
templates_path = Path(__file__).parent
templates = Jinja2Templates(directory=str(templates_path))

# FastAPI 앱 생성
app = FastAPI(title="EORA Test Server", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse("test_chat_simple.html", {"request": request})

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "테스트 서버가 정상적으로 실행 중입니다."
    }

@app.get("/api/status")
async def api_status():
    return {
        "message": "EORA Test Server API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

def find_free_port(start_port=8000, max_attempts=100):
    """사용 가능한 포트를 찾습니다."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def kill_process_on_port(port):
    """특정 포트를 사용하는 프로세스를 종료합니다."""
    try:
        import subprocess
        # Windows에서 포트를 사용하는 프로세스 찾기
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True, capture_output=True, text=True
        )
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                            print(f"✅ 포트 {port}의 프로세스 {pid} 종료됨")
                        except:
                            pass
    except Exception as e:
        print(f"⚠️ 포트 {port} 프로세스 종료 실패: {e}")

if __name__ == "__main__":
    import uvicorn
    
    # 사용 가능한 포트 찾기
    port = find_free_port(8003, 50)
    if port is None:
        print("❌ 사용 가능한 포트를 찾을 수 없습니다.")
        print("🔧 다른 프로세스를 종료하고 다시 시도하세요.")
        sys.exit(1)
    
    print("🚀 간단한 테스트 서버를 시작합니다...")
    print(f"📍 주소: http://127.0.0.1:{port}")
    print(f"📋 테스트 페이지: http://127.0.0.1:{port}/test")
    print(f"🏥 헬스체크: http://127.0.0.1:{port}/health")
    print("=" * 50)
    
    try:
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=port, 
            log_level="info",
            reload=False  # 재시작 비활성화
        )
    except KeyboardInterrupt:
        print("\n🛑 서버가 종료되었습니다.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 포트 {port}가 이미 사용 중입니다.")
            print("🔧 다른 포트를 시도합니다...")
            # 다른 포트 시도
            port = find_free_port(port + 1, 20)
            if port:
                print(f"🔄 포트 {port}로 재시작합니다...")
                uvicorn.run(
                    app, 
                    host="127.0.0.1", 
                    port=port, 
                    log_level="info",
                    reload=False
                )
            else:
                print("❌ 사용 가능한 포트를 찾을 수 없습니다.")
        else:
            print(f"❌ 서버 실행 중 오류 발생: {e}")
    except Exception as e:
        print(f"❌ 서버 실행 중 오류 발생: {e}") 