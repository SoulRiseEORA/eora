from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from datetime import datetime
import logging
import json
import openai
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AURA System with GPT", version="1.0.0")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"

# OpenAI 클라이언트 초기화
openai_client = None
if OPENAI_API_KEY:
    try:
        openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI 클라이언트 초기화 성공")
    except Exception as e:
        logger.error(f"OpenAI 클라이언트 초기화 실패: {e}")
else:
    logger.warning("OPENAI_API_KEY가 설정되지 않았습니다.")

# WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

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
            logger.error(f"웹소켓 메시지 전송 실패: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"브로드캐스트 실패: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """홈페이지"""
    logger.info("홈페이지 요청됨")
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/aura_system", response_class=HTMLResponse)
async def aura_system_page(request: Request):
    """AURA 시스템 소개 페이지"""
    logger.info("AURA 시스템 페이지 요청됨")
    try:
        return templates.TemplateResponse("aura_system.html", {"request": request})
    except Exception as e:
        logger.error(f"AURA 페이지 오류: {e}")
        return HTMLResponse(content=f"<h1>AURA 시스템 페이지</h1><p>오류: {e}</p>", status_code=500)

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """채팅 페이지"""
    logger.info("채팅 페이지 요청됨")
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/health")
async def health_check():
    """헬스 체크"""
    logger.info("헬스 체크 요청됨")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "aura_system": "active",
        "openai_available": openai_client is not None
    }

@app.get("/api/aura/system/info")
async def get_aura_system_info():
    """AURA 시스템 정보 조회"""
    logger.info("AURA 시스템 정보 요청됨")
    system_info = {
        "name": "AURA System with GPT",
        "version": "1.0.0",
        "description": "인간의 직감과 기억 회상 메커니즘을 결합한 6단계 계층 구조 AI 기억 시스템",
        "hierarchy_levels": [
            {
                "level": 1,
                "name": "기억 (Memory)",
                "description": "MongoDB 기반 구조화된 기억 저장 시스템"
            },
            {
                "level": 2,
                "name": "회상 (Recall)",
                "description": "다단계 회상 시스템과 7가지 회상 전략"
            },
            {
                "level": 3,
                "name": "통찰 (Insight)",
                "description": "패턴 인식과 연결 분석을 통한 통찰 생성"
            },
            {
                "level": 4,
                "name": "지혜 (Wisdom)",
                "description": "통찰을 바탕으로 한 지혜로운 판단"
            },
            {
                "level": 5,
                "name": "진리 (Truth)",
                "description": "지혜를 통한 진리 인식과 본질적 이해"
            },
            {
                "level": 6,
                "name": "존재 감각 (Existence)",
                "description": "진리를 통한 존재의 의미와 목적 이해"
            }
        ],
        "performance_metrics": {
            "token_efficiency_improvement": "82.5%",
            "memory_recall_speed": "92% 향상",
            "intuition_accuracy": "2배 향상",
            "search_response_connection": "1.7배 향상"
        },
        "features": [
            "직감 기반 회상",
            "다차원 연결망",
            "실시간 통찰",
            "맥락 인식",
            "성능 최적화",
            "자기 진화",
            "GPT 통합"
        ],
        "status": "active",
        "openai_available": openai_client is not None,
        "last_updated": datetime.now().isoformat()
    }
    
    return system_info

# GPT 채팅 API 엔드포인트 추가
@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """GPT 채팅 API"""
    try:
        data = await request.json()
        user_message = data.get("message", "")
        user_id = data.get("user_id", "anonymous")
        
        logger.info(f"채팅 요청: {user_id} - {user_message[:50]}...")
        
        if not user_message.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "메시지가 비어있습니다."}
            )
        
        # GPT API 호출
        if openai_client:
            try:
                response = await openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "당신은 AURA 시스템의 AI 어시스턴트입니다. 인간의 직감과 기억 회상 메커니즘을 결합한 지혜로운 AI입니다."},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                ai_response = response.choices[0].message.content
                logger.info("GPT API 응답 생성 완료")
            except Exception as e:
                logger.error(f"GPT API 호출 실패: {e}")
                ai_response = "죄송합니다. 현재 응답을 생성할 수 없습니다. 잠시 후 다시 시도해주세요."
        else:
            ai_response = "죄송합니다. AI 시스템이 초기화되지 않았습니다. 관리자에게 문의해주세요."
        
        # 응답 데이터 구성
        response_data = {
            "response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "model": OPENAI_MODEL if openai_client else "none"
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"채팅 API 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "채팅 처리 중 오류가 발생했습니다.", "details": str(e)}
        )

# WebSocket 엔드포인트 추가
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 엔드포인트 - 실시간 채팅 처리"""
    logger.info(f"WebSocket 연결 시도: {client_id}")
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type", "message")
            
            if message_type == "message":
                user_message = message_data.get("content", "")
                session_id = message_data.get("session_id", client_id)
                
                # GPT API 호출
                if openai_client:
                    try:
                        response = await openai_client.chat.completions.create(
                            model=OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": "당신은 AURA 시스템의 AI 어시스턴트입니다. 인간의 직감과 기억 회상 메커니즘을 결합한 지혜로운 AI입니다."},
                                {"role": "user", "content": user_message}
                            ],
                            max_tokens=1000,
                            temperature=0.7
                        )
                        ai_response = response.choices[0].message.content
                        logger.info("WebSocket GPT API 응답 생성 완료")
                    except Exception as e:
                        logger.error(f"WebSocket GPT API 호출 실패: {e}")
                        ai_response = "죄송합니다. 현재 응답을 생성할 수 없습니다."
                else:
                    ai_response = f"AURA 시스템 응답: {user_message}에 대한 답변입니다."
                
                # 응답 전송
                await manager.send_personal_message(json.dumps({
                    "type": "response",
                    "content": ai_response,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }), websocket)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket 연결 해제: {client_id}")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
        manager.disconnect(websocket)

# 디버깅용 라우트 추가
@app.get("/debug/routes")
async def debug_routes():
    """등록된 라우트 확인"""
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, 'methods') else []
        })
    return {"routes": routes}

if __name__ == "__main__":
    import uvicorn
    logger.info("서버 시작 중...")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True) 