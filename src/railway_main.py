import os
import json
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, EmailStr
import uvicorn
from fastapi.websockets import WebSocket, WebSocketDisconnect

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="EORA AI System", version="2.0.0")

# 세션 미들웨어 추가
app.add_middleware(
    SessionMiddleware,
    secret_key="eora_super_secret_key_2024_07_11_!@#",
    session_cookie="eora_session",
    max_age=60*60*24*7,  # 7일
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 데이터 모델
class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

# 메모리 기반 데이터 저장소
users_db: Dict[str, Dict] = {}
sessions_db: Dict[str, Dict] = {}
chat_history: Dict[str, List] = {}

# EORA Core 클래스
class EORACore:
    def __init__(self):
        self.name = "EORA Core"
        self.version = "2.0.0"
        self.openai_client = None
        self._initialize_openai()
    
    def _initialize_openai(self):
        """OpenAI 클라이언트 초기화"""
        try:
            from openai import OpenAI
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("✅ OpenAI 클라이언트 초기화 완료")
            else:
                logger.warning("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        except Exception as e:
            logger.error(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
    
    def process_input(self, message: str, user_id: str = None) -> str:
        """사용자 입력 처리 - GPT API 사용"""
        try:
            if not self.openai_client:
                return self._fallback_response(message)
            
            # 🎯 과거 대화 회상 및 메모리 활용 지시사항 (최우선)
            memory_instruction = (
                "아래 [과거 대화 요약] 메시지는 참고하여, 필요하다고 판단되는 경우에만 답변에 반영하라. "
                "특히, 날씨/시간/장소/감정 등 맥락이 중요한 경우에는 과거 대화를 적극적으로 활용하라.\n"
                "아래 [과거 대화 요약] 사용자 질문이 1개 이상의 회상 답변을 요구 하는지 판단하여 대화에 필요하다고 판단되는 경우 1개 이상 3개까지 답변에 반영하라.\n\n"
            )
            
            base_system_content = "당신은 EORA AI입니다. 사용자와 따뜻하고 공감적인 대화를 나누며, 그들의 성장과 자기 이해를 돕는 AI 상담사입니다. 한국어로 응답해주세요."
            full_system_content = memory_instruction + base_system_content
            
            # GPT API 호출
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": full_system_content
                    },
                    {
                        "role": "user", 
                        "content": message
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"✅ GPT API 응답 생성 완료 - 사용자: {user_id}")
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ GPT API 호출 실패: {e}")
            return self._fallback_response(message)
    
    def _fallback_response(self, message: str) -> str:
        """GPT API 실패 시 대체 응답"""
        fallback_responses = [
            "안녕하세요! EORA AI입니다. 무엇을 도와드릴까요?",
            "흥미로운 질문이네요. 더 자세히 설명해주시겠어요?",
            "좋은 질문입니다. 제가 도움을 드릴 수 있는 부분이 있나요?",
            "EORA AI가 당신의 질문에 답변하고 있습니다. 잠시만 기다려주세요.",
            "의식적 AI 시스템과의 대화를 즐기고 계시는군요!",
            "당신의 생각이 흥미롭습니다. 더 자세히 들어보고 싶어요.",
            "EORA AI는 학습과 성장을 통해 더 나은 답변을 제공하려고 합니다.",
            "의식과 지능의 경계에서 당신과 대화하는 것이 즐겁습니다.",
            "현재 AI 서비스에 일시적인 문제가 있어 기본 응답을 드립니다. 곧 정상화될 예정입니다.",
            "죄송합니다. 현재 응답을 생성할 수 없습니다. 잠시 후 다시 시도해주세요."
        ]
        
        import random
        return random.choice(fallback_responses)

# EORA Core 인스턴스 생성
eora_core = EORACore()

# 유틸리티 함수들
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def generate_session_id() -> str:
    return f"session_{datetime.now().timestamp()}_{hash(datetime.now())}"

def get_user_by_email(email: str) -> Optional[Dict]:
    for user in users_db.values():
        if user.get("email") == email:
            return user
    return None

def get_current_user(request: Request) -> Optional[Dict]:
    user_id = request.session.get("user_id")
    if user_id and user_id in users_db:
        return users_db[user_id]
    return None

def require_auth(request: Request) -> Dict:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")
    return user

def require_admin(request: Request) -> Dict:
    user = require_auth(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return user

def initialize_system():
    """시스템 초기화 - 기본 관리자 및 사용자 계정 생성"""
    # 기본 관리자 계정
    admin_id = "admin_001"
    if admin_id not in users_db:
        users_db[admin_id] = {
            "id": admin_id,
            "name": "관리자",
            "email": "admin@eora.ai",
            "password": hash_password("admin123"),
            "role": "admin",
            "created_at": datetime.now().isoformat(),
            "points": 1000,
            "storage_used": 0,
            "storage_limit": 1000000
        }
        logger.info("✅ 기본 관리자 계정 생성 완료")
    
    # 기본 사용자 계정
    user_id = "user_001"
    if user_id not in users_db:
        users_db[user_id] = {
            "id": user_id,
            "name": "테스트 사용자",
            "email": "user@eora.ai",
            "password": hash_password("user123"),
            "role": "user",
            "created_at": datetime.now().isoformat(),
            "points": 100,
            "storage_used": 0,
            "storage_limit": 100000
        }
        logger.info("✅ 기본 사용자 계정 생성 완료")

# 환경변수 설정
def setup_environment():
    """환경변수 설정"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        logger.info("✅ OpenAI API 키가 Railway 환경변수에서 설정되었습니다.")
    else:
        logger.warning("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
    
    port = int(os.getenv("PORT", 8080))
    return port

# 라우트 정의
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

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """로그인 페이지"""
    try:
        return templates.TemplateResponse("login.html", {"request": request})
    except Exception as e:
        logger.error(f"로그인 페이지 로드 오류: {e}")
        return HTMLResponse(content=f"""
        <html>
        <head><title>로그인 - EORA AI System</title></head>
        <body>
            <h1>로그인</h1>
            <p>로그인 페이지를 로드할 수 없습니다: {e}</p>
            <p><a href="/home">홈으로 돌아가기</a></p>
        </body>
        </html>
        """)

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """관리자 페이지"""
    try:
        return templates.TemplateResponse("admin.html", {"request": request})
    except Exception as e:
        logger.error(f"관리자 페이지 로드 오류: {e}")
        return HTMLResponse(content=f"""
        <html>
        <head><title>관리자 - EORA AI System</title></head>
        <body>
            <h1>관리자 페이지</h1>
            <p>관리자 페이지를 로드할 수 없습니다: {e}</p>
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

@app.post("/api/auth/login")
async def login_user(request: Request, login_data: UserLogin):
    """사용자 로그인"""
    try:
        user = get_user_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다")
        
        # 세션에 사용자 정보 저장
        request.session["user_id"] = user["id"]
        request.session["user_role"] = user["role"]
        
        logger.info(f"✅ 사용자 로그인 성공: {user['email']}")
        return {
            "success": True,
            "message": "로그인 성공",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        raise HTTPException(status_code=500, detail="로그인 처리 중 오류가 발생했습니다")

@app.post("/api/login")
async def login_user_legacy(request: Request, login_data: UserLogin):
    """레거시 로그인 API (호환성)"""
    return await login_user(request, login_data)

@app.post("/api/auth/logout")
async def logout_user(request: Request):
    """사용자 로그아웃"""
    request.session.clear()
    return {"success": True, "message": "로그아웃 성공"}

@app.get("/api/sessions")
async def get_sessions(request: Request):
    """세션 목록 조회"""
    try:
        user = get_current_user(request)
        user_id = user["id"] if user else "anonymous"
        
        user_sessions = []
        for session_id, session in sessions_db.items():
            if session.get("user_id") == user_id:
                user_sessions.append({
                    "id": session_id,
                    "name": session.get("name", "새 대화"),
                    "created_at": session.get("created_at"),
                    "message_count": len(session.get("messages", []))
                })
        
        return {"sessions": user_sessions}
    except Exception as e:
        logger.error(f"세션 목록 조회 오류: {e}")
        return {"sessions": []}

@app.post("/api/sessions")
async def create_session(request: Request):
    """새 세션 생성"""
    try:
        user = get_current_user(request)
        user_id = user["id"] if user else "anonymous"
        
        session_id = generate_session_id()
        sessions_db[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "name": "새 대화",
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        
        logger.info(f"✅ 새 채팅 세션 생성: {session_id}")
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"세션 생성 오류: {e}")
        raise HTTPException(status_code=500, detail="세션 생성에 실패했습니다")

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(request: Request, session_id: str):
    """세션 메시지 조회"""
    try:
        user = get_current_user(request)
        user_id = user["id"] if user else "anonymous"
        
        if session_id in sessions_db:
            session = sessions_db[session_id]
            # 사용자 권한 확인
            if session.get("user_id") == user_id or user_id == "anonymous":
                return {"messages": session.get("messages", [])}
        
        return {"messages": []}
    except Exception as e:
        logger.error(f"메시지 조회 오류: {e}")
        return {"messages": []}

@app.post("/api/messages")
async def save_message(request: Request):
    """메시지 저장"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        role = data.get("role", "user")
        content = data.get("content", "")
        
        if session_id and content:
            if session_id not in sessions_db:
                user = get_current_user(request)
                user_id = user["id"] if user else "anonymous"
                sessions_db[session_id] = {
                    "id": session_id,
                    "user_id": user_id,
                    "name": "새 대화",
                    "created_at": datetime.now().isoformat(),
                    "messages": []
                }
            
            message_data = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            sessions_db[session_id]["messages"].append(message_data)
            
            return {"success": True, "message": "메시지가 저장되었습니다."}
        
        return {"success": False, "message": "메시지 저장에 실패했습니다."}
    except Exception as e:
        logger.error(f"메시지 저장 오류: {e}")
        return {"success": False, "message": "메시지 저장에 실패했습니다."}

@app.post("/api/chat")
async def chat_endpoint(request: Request, chat_data: ChatMessage):
    """채팅 API"""
    try:
        user = get_current_user(request)
        user_id = user["id"] if user else "anonymous"
        
        logger.info(f"💬 채팅 요청 - 사용자: {user_id}, 메시지: {chat_data.message[:50]}...")
        
        # EORA Core를 통한 AI 응답 생성
        ai_response = eora_core.process_input(chat_data.message, user_id)
        
        # 응답 저장
        if chat_data.session_id and chat_data.session_id in sessions_db:
            sessions_db[chat_data.session_id]["messages"].append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })
        
        return {"response": ai_response}
        
    except Exception as e:
        logger.error(f"채팅 API 오류: {e}")
        return {"response": f"오류가 발생했습니다: {str(e)}"}

@app.post("/api/set-language")
async def set_language(request: Request):
    """언어 설정"""
    try:
        data = await request.json()
        language = data.get("language", "ko")
        
        # 세션에 언어 설정 저장
        request.session["language"] = language
        
        return {"success": True, "message": f"언어가 {language}로 설정되었습니다."}
    except Exception as e:
        logger.error(f"언어 설정 오류: {e}")
        return {"success": False, "message": "언어 설정에 실패했습니다."}

@app.delete("/api/sessions/{session_id}")
async def delete_session(request: Request, session_id: str):
    """세션 삭제"""
    try:
        user = get_current_user(request)
        user_id = user["id"] if user else "anonymous"
        
        if session_id in sessions_db:
            session = sessions_db[session_id]
            # 사용자 권한 확인
            if session.get("user_id") == user_id or user_id == "anonymous":
                del sessions_db[session_id]
                return {"success": True, "message": "세션이 삭제되었습니다."}
        
        return {"success": False, "message": "세션을 찾을 수 없습니다."}
    except Exception as e:
        logger.error(f"세션 삭제 오류: {e}")
        return {"success": False, "message": "세션 삭제에 실패했습니다."}

# WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"WebSocket 메시지 전송 오류: {e}")
            self.disconnect(websocket)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 엔드포인트"""
    try:
        await manager.connect(websocket)
        logger.info(f"✅ WebSocket 연결 성공: {session_id}")
        
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # 메시지 처리 및 AI 응답 생성
                user_message = message_data.get("message", "")
                ai_response = eora_core.process_input(user_message)
                
                # 응답 전송
                response_data = {
                    "type": "ai_response",
                    "content": ai_response,
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(response_data), websocket)
                
            except WebSocketDisconnect:
                manager.disconnect(websocket)
                logger.info(f"WebSocket 연결 종료: {session_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket 처리 오류: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket 연결 오류: {e}")
        manager.disconnect(websocket)

# 서버 이벤트 핸들러
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    logger.info("🚀 EORA AI 시스템 시작 중...")
    port = setup_environment()
    initialize_system()
    logger.info(f"✅ 서버가 포트 {port}에서 시작되었습니다.")
    logger.info("🚀 EORA AI 시스템이 성공적으로 시작되었습니다!")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행"""
    logger.info("✅ 시스템 종료 중...")

# Railway 배포용 실행
if __name__ == "__main__":
    port = setup_environment()
    uvicorn.run(app, host="0.0.0.0", port=port) 