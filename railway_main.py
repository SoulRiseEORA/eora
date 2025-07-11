import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from datetime import datetime
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="EORA AI System", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 정적 파일 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 환경변수 설정
def setup_environment():
    """환경변수 설정"""
    # Railway 환경변수에서 가져오기
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        logger.info("✅ OpenAI API 키가 Railway 환경변수에서 설정되었습니다.")
    else:
        logger.warning("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
    
    # 기타 필요한 환경변수들
    port = int(os.getenv("PORT", 8000))
    return port

# 전역 변수
chat_history = {}
sessions = {}

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    logger.info("🚀 EORA AI 시스템 시작 중...")
    port = setup_environment()
    logger.info(f"✅ 서버가 포트 {port}에서 시작되었습니다.")
    logger.info("🚀 EORA AI 시스템이 성공적으로 시작되었습니다!")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행"""
    logger.info("✅ 시스템 종료 중...")

# 기본 라우트 - home.html로 리다이렉트
@app.get("/")
async def root(request: Request):
    """루트 경로 - 홈페이지로 리다이렉트"""
    return RedirectResponse(url="/home")

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    """홈페이지"""
    try:
        return templates.TemplateResponse("home.html", {"request": request})
    except Exception as e:
        logger.error(f"홈페이지 로드 오류: {e}")
        return HTMLResponse(content=f"""
        <html>
        <head><title>EORA AI System</title></head>
        <body>
            <h1>🚀 EORA AI System</h1>
            <p>✅ 서버 상태: 정상 실행 중</p>
            <p>Railway 환경에서 성공적으로 배포되었습니다.</p>
            <p><a href="/chat">채팅 시작</a></p>
        </body>
        </html>
        """)

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    """채팅 페이지"""
    try:
        return templates.TemplateResponse("chat.html", {"request": request})
    except Exception as e:
        logger.error(f"채팅 페이지 로드 오류: {e}")
        return HTMLResponse(content=f"""
        <html>
        <head><title>채팅 - EORA AI System</title></head>
        <body>
            <h1>채팅 시스템</h1>
            <p>채팅 페이지를 로드할 수 없습니다: {e}</p>
            <p><a href="/home">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

# API 엔드포인트들
@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": "railway"
    }

@app.get("/api/sessions")
async def get_sessions():
    """세션 목록 조회"""
    return {"sessions": list(sessions.values())}

@app.post("/api/sessions")
async def create_session():
    """새 세션 생성"""
    session_id = f"session_{datetime.now().timestamp()}_{hash(datetime.now())}"
    sessions[session_id] = {
        "id": session_id,
        "name": "새 대화",
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    logger.info(f"✅ 새 채팅 세션 생성: {session_id}")
    return {"session_id": session_id}

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    """세션 메시지 조회"""
    if session_id in sessions:
        return {"messages": sessions[session_id]["messages"]}
    return {"messages": []}

@app.post("/api/messages")
async def save_message(request: Request):
    """메시지 저장"""
    data = await request.json()
    session_id = data.get("session_id")
    role = data.get("role", "user")
    content = data.get("content", "")
    
    if session_id and content:
        if session_id not in sessions:
            sessions[session_id] = {
                "id": session_id,
                "name": "새 대화",
                "created_at": datetime.now().isoformat(),
                "messages": []
            }
        
        message_data = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        sessions[session_id]["messages"].append(message_data)
        
        return {"success": True, "message": "메시지가 저장되었습니다."}
    
    return {"success": False, "message": "메시지 저장에 실패했습니다."}

@app.post("/api/chat")
async def chat_api(request: Request):
    """채팅 API"""
    try:
        data = await request.json()
        message = data.get("message", "")
        session_id = data.get("session_id")
        
        logger.info(f"💬 채팅 요청 - 메시지: {message[:50]}...")
        
        # OpenAI API 키 확인
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            response = "죄송합니다. 현재 OpenAI API 키가 설정되지 않아 AI 응답을 생성할 수 없습니다. Railway 환경변수에서 OPENAI_API_KEY를 설정해주세요."
        else:
            # 여기에 실제 GPT API 호출 로직을 추가할 수 있습니다
            response = f"안녕하세요! '{message}'에 대한 응답입니다. Railway에서 정상적으로 작동하고 있습니다."
        
        # 응답 저장
        if session_id and session_id in sessions:
            sessions[session_id]["messages"].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"채팅 API 오류: {e}")
        return {"response": f"오류가 발생했습니다: {str(e)}"}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    if session_id in sessions:
        del sessions[session_id]
        return {"success": True, "message": "세션이 삭제되었습니다."}
    return {"success": False, "message": "세션을 찾을 수 없습니다."}

# Railway 배포용 실행
if __name__ == "__main__":
    port = setup_environment()
    uvicorn.run(app, host="0.0.0.0", port=port) 