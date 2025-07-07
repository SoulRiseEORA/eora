#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway 안정 서버 - 파일 변경 감지 완전 차단
"""

import os
import sys
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
from datetime import datetime
import traceback

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경변수 설정
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

# 템플릿 설정
templates_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_path)

# 웹소켓 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"새로운 웹소켓 연결: {len(self.active_connections)}개 활성")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"웹소켓 연결 해제: {len(self.active_connections)}개 활성")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"메시지 전송 실패: {e}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"브로드캐스트 실패: {e}")

manager = ConnectionManager()

# 데이터 모델
class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

class SessionData(BaseModel):
    name: str
    messages: list = []

# 메모리 저장소 (Redis 대신 메모리 사용)
sessions = {}
chat_history = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    logger.info("🚀 Railway 안정 서버 시작")
    logger.info("📁 템플릿 경로: " + templates_path)
    logger.info("✅ 파일 변경 감지 완전 차단됨")
    
    yield
    
    # 종료 시
    logger.info("🛑 Railway 안정 서버 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="EORA AI System - Railway 안정 서버",
    description="파일 변경 감지 완전 차단된 안정 서버",
    version="2.0.0",
    lifespan=lifespan
)

# 정적 파일 설정 (선택적)
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    try:
        app.mount("/static", StaticFiles(directory=static_path), name="static")
        logger.info("✅ 정적 파일 마운트 성공")
    except Exception as e:
        logger.warning(f"정적 파일 마운트 실패: {e}")
else:
    logger.info("ℹ️ 정적 파일 디렉토리가 없습니다. 건너뜁니다.")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """홈페이지"""
    try:
        return templates.TemplateResponse("home.html", {"request": request})
    except Exception as e:
        logger.error(f"홈페이지 렌더링 실패: {e}")
        return HTMLResponse(content="<h1>EORA AI System</h1><p>서버가 정상 작동 중입니다.</p>")

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """채팅 페이지"""
    try:
        return templates.TemplateResponse("chat.html", {"request": request})
    except Exception as e:
        logger.error(f"채팅 페이지 렌더링 실패: {e}")
        return HTMLResponse(content="<h1>채팅</h1><p>채팅 기능을 사용할 수 없습니다.</p>")

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "railway_stable",
        "version": "2.0.0",
        "port": 8005
    }

@app.get("/api/sessions")
async def get_sessions():
    """세션 목록 조회"""
    try:
        session_list = []
        for session_id, data in sessions.items():
            session_list.append({
                "id": session_id,
                "name": data.get("name", "무제"),
                "message_count": len(data.get("messages", [])),
                "created_at": data.get("created_at", datetime.now().isoformat())
            })
        return {"sessions": session_list}
    except Exception as e:
        logger.error(f"세션 목록 조회 실패: {e}")
        return {"sessions": []}

@app.post("/api/sessions")
async def create_session(session_data: SessionData):
    """새 세션 생성"""
    try:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        sessions[session_id] = {
            "name": session_data.name,
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
        return {"session_id": session_id, "name": session_data.name}
    except Exception as e:
        logger.error(f"세션 생성 실패: {e}")
        raise HTTPException(status_code=500, detail="세션 생성 실패")

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    try:
        if session_id in sessions:
            del sessions[session_id]
            if session_id in chat_history:
                del chat_history[session_id]
        return {"message": "세션 삭제 완료"}
    except Exception as e:
        logger.error(f"세션 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail="세션 삭제 실패")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """웹소켓 엔드포인트"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 메시지 저장
            if session_id not in chat_history:
                chat_history[session_id] = []
            
            user_message = {
                "role": "user",
                "content": message_data.get("message", ""),
                "timestamp": datetime.now().isoformat()
            }
            chat_history[session_id].append(user_message)
            
            # AI 응답 생성
            ai_response = {
                "role": "assistant",
                "content": f"안정 서버에서 응답: {message_data.get('message', '')}",
                "timestamp": datetime.now().isoformat()
            }
            chat_history[session_id].append(ai_response)
            
            # 응답 전송
            response_data = {
                "type": "message",
                "content": ai_response["content"],
                "timestamp": ai_response["timestamp"]
            }
            await manager.send_personal_message(json.dumps(response_data), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"웹소켓 오류: {e}")
        manager.disconnect(websocket)

@app.get("/api/chat/{session_id}")
async def get_chat_history(session_id: str):
    """채팅 기록 조회"""
    try:
        return {"messages": chat_history.get(session_id, [])}
    except Exception as e:
        logger.error(f"채팅 기록 조회 실패: {e}")
        return {"messages": []}

@app.post("/api/chat/{session_id}")
async def send_message(session_id: str, message: ChatMessage):
    """메시지 전송"""
    try:
        if session_id not in chat_history:
            chat_history[session_id] = []
        
        user_message = {
            "role": "user",
            "content": message.message,
            "timestamp": datetime.now().isoformat()
        }
        chat_history[session_id].append(user_message)
        
        # AI 응답 생성
        ai_response = {
            "role": "assistant",
            "content": f"안정 서버 응답: {message.message}",
            "timestamp": datetime.now().isoformat()
        }
        chat_history[session_id].append(ai_response)
        
        return ai_response
    except Exception as e:
        logger.error(f"메시지 전송 실패: {e}")
        raise HTTPException(status_code=500, detail="메시지 전송 실패")

@app.get("/test")
async def test_endpoint():
    """테스트 엔드포인트"""
    return {
        "message": "Railway 안정 서버가 정상 작동 중입니다!",
        "timestamp": datetime.now().isoformat(),
        "status": "stable",
        "port": 8005
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "railway_server:app",
        host="0.0.0.0",
        port=8005,  # 포트를 8005로 변경
        reload=False,  # 재시작 완전 차단
        log_level="info"
    ) 