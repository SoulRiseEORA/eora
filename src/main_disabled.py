from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from datetime import datetime
import logging
import json
import openai
from typing import Dict, Any, List
import uuid
from pathlib import Path

# 로깅 설정 (먼저 설정)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일 로드
def load_env_file():
    """환경 변수 파일 로드"""
    # 현재 폴더와 상위 폴더에서 .env 파일 찾기
    env_files = [
        Path(".env"),  # 현재 폴더
        Path("..").resolve() / ".env",  # 상위 폴더
        Path("../.env"),  # 상위 폴더 (상대 경로)
    ]
    
    for env_file in env_files:
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                try:
                    logger.info(f".env 파일 로드 완료: {env_file}")
                except NameError:
                    print(f".env 파일 로드 완료: {env_file}")
                return
            except Exception as e:
                try:
                    logger.error(f".env 파일 로드 실패 ({env_file}): {e}")
                except NameError:
                    print(f".env 파일 로드 실패 ({env_file}): {e}")
    
    try:
        logger.info("ℹ️ .env 파일을 찾을 수 없습니다. Railway 환경변수를 사용합니다.")
    except NameError:
        print("ℹ️ .env 파일을 찾을 수 없습니다. Railway 환경변수를 사용합니다.")

# 환경 변수 로드 (logger 정의 후에 호출)
load_env_file()

app = FastAPI(title="AURA System with GPT", version="1.0.0")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 데이터 저장소 설정
DATA_DIR = "chat_data"
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")

# 데이터 디렉토리 생성
os.makedirs(DATA_DIR, exist_ok=True)

# 데이터 로드 함수
def load_sessions() -> List[Dict]:
    """세션 데이터 로드"""
    try:
        if os.path.exists(SESSIONS_FILE):
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"세션 로드 오류: {e}")
    return []

def save_sessions(sessions: List[Dict]):
    """세션 데이터 저장"""
    try:
        with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"세션 저장 오류: {e}")

def load_messages() -> List[Dict]:
    """메시지 데이터 로드"""
    try:
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"메시지 로드 오류: {e}")
    return []

def save_messages(messages: List[Dict]):
    """메시지 데이터 저장"""
    try:
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"메시지 저장 오류: {e}")

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"

# 프롬프트 데이터 전역 변수
prompts_data = {}

def load_prompts_data():
    """ai_prompts.json 파일에서 프롬프트 데이터를 로드합니다."""
    global prompts_data
    try:
        prompts_file = "ai_brain/ai_prompts.json"
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
            logger.info(f"✅ ai_prompts.json 파일 로드 완료: {len(prompts_data)}개 AI")
            return True
        else:
            logger.warning("⚠️ ai_prompts.json 파일을 찾을 수 없습니다.")
            return False
    except Exception as e:
        logger.error(f"❌ 프롬프트 데이터 로드 오류: {e}")
        return False

# OpenAI 클라이언트 초기화 - Railway 호환
openai_client = None
if OPENAI_API_KEY:
    try:
        logger.info("OpenAI 클라이언트 초기화 시도...")
        # Railway 호환 - OpenAI 클라이언트 사용
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI 클라이언트 초기화 성공")
    except Exception as e:
        logger.error(f"OpenAI 클라이언트 초기화 실패: {e}")
        logger.error(f"오류 타입: {type(e)}")
        import traceback
        logger.error(f"스택 트레이스: {traceback.format_exc()}")
        # 오류 발생 시에도 None으로 설정하여 서버가 계속 실행되도록 함
        openai_client = None
else:
    logger.info("OPENAI_API_KEY가 설정되지 않았습니다. Railway 환경변수를 확인해주세요.")

# 서버 시작 시 프롬프트 데이터 로드
logger.info("📚 프롬프트 데이터 로드 중...")
if load_prompts_data():
    logger.info("✅ 프롬프트 데이터 로드 완료")
else:
    logger.warning("⚠️ 프롬프트 데이터 로드 실패 - 기본 설정으로 진행")

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
        
        # AI 프롬프트 로드
        system_prompt = "당신은 AURA 시스템의 AI 어시스턴트입니다. 인간의 직감과 기억 회상 메커니즘을 결합한 지혜로운 AI입니다."
        
        # ai_prompts.json에서 ai1의 system 프롬프트 사용
        if prompts_data and "ai1" in prompts_data and "system" in prompts_data["ai1"]:
            ai1_system_prompts = prompts_data["ai1"]["system"]
            if isinstance(ai1_system_prompts, list) and len(ai1_system_prompts) > 0:
                system_prompt = "\n".join(ai1_system_prompts)
            elif isinstance(ai1_system_prompts, str):
                system_prompt = ai1_system_prompts
        
        # GPT API 호출 - Railway 호환
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
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
                
                # AI 프롬프트 로드
                system_prompt = "당신은 AURA 시스템의 AI 어시스턴트입니다. 인간의 직감과 기억 회상 메커니즘을 결합한 지혜로운 AI입니다."
                
                # ai_prompts.json에서 ai1의 system 프롬프트 사용
                if prompts_data and "ai1" in prompts_data and "system" in prompts_data["ai1"]:
                    ai1_system_prompts = prompts_data["ai1"]["system"]
                    if isinstance(ai1_system_prompts, list) and len(ai1_system_prompts) > 0:
                        system_prompt = "\n".join(ai1_system_prompts)
                    elif isinstance(ai1_system_prompts, str):
                        system_prompt = ai1_system_prompts
                
                # GPT API 호출 - Railway 호환
                if openai_client:
                    try:
                        response = openai_client.chat.completions.create(
                            model=OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": system_prompt},
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

# 언어 설정 API
@app.post("/api/set-language")
async def set_language(request: Request):
    """언어 설정"""
    try:
        data = await request.json()
        language = data.get("language", "ko")
        logger.info(f"언어 설정: {language}")
        return JSONResponse(content={"status": "success", "language": language})
    except Exception as e:
        logger.error(f"언어 설정 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "언어 설정 실패"})

# 세션 관리 API
@app.get("/api/sessions")
async def get_sessions():
    """세션 목록 조회"""
    try:
        sessions = load_sessions()
        logger.info("세션 목록 조회")
        return JSONResponse(content={"sessions": sessions})
    except Exception as e:
        logger.error(f"세션 조회 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "세션 조회 실패"})

@app.post("/api/sessions")
async def create_session(request: Request):
    """새 세션 생성"""
    try:
        data = await request.json()
        session_name = data.get("name", f"새 세션 {datetime.now().strftime('%Y. %m. %d.')}")
        user_id = data.get("user_id", "anonymous")
        
        # 고유한 세션 ID 생성
        session_id = f"session_{int(datetime.now().timestamp() * 1000)}"
        
        session_data = {
            "id": session_id,
            "name": session_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_id": user_id,
            "message_count": 0,
            "status": "active"
        }
        
        sessions = load_sessions()
        sessions.append(session_data)
        save_sessions(sessions)
        
        logger.info(f"새 세션 생성: {session_name}")
        return JSONResponse(content={
            "success": True,
            "session_id": session_id,
            "session": session_data,
            "message": "세션이 성공적으로 생성되었습니다."
        })
    except Exception as e:
        logger.error(f"세션 생성 오류: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": "세션 생성 실패",
            "message": str(e)
        })

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """세션 삭제"""
    try:
        sessions = load_sessions()
        session_exists = any(s["id"] == session_id for s in sessions)
        if not session_exists:
            return JSONResponse(status_code=404, content={"error": "세션을 찾을 수 없습니다."})
        # 세션 삭제
        sessions = [s for s in sessions if s["id"] != session_id]
        save_sessions(sessions)
        # 해당 세션의 메시지도 삭제
        messages = load_messages()
        messages = [m for m in messages if m["session_id"] != session_id]
        save_messages(messages)
        logger.info(f"세션 삭제: {session_id}")
        return {"result": "ok"}
    except Exception as e:
        logger.error(f"세션 삭제 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "세션 삭제 실패"})

# 메시지 API
@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """세션별 메시지 조회"""
    try:
        messages = load_messages()
        session_messages = [msg for msg in messages if msg.get("session_id") == session_id]
        logger.info(f"세션 {session_id} 메시지 조회: {len(session_messages)}개")
        return JSONResponse(content={"messages": session_messages})
    except Exception as e:
        logger.error(f"세션 메시지 조회 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "메시지 조회 실패"})

@app.post("/api/messages")
async def create_message(request: Request):
    """새 메시지 생성"""
    try:
        data = await request.json()
        content = data.get("content", "")
        session_id = data.get("session_id", "")
        role = data.get("role", "user")
        
        message_data = {
            "id": f"msg_{datetime.now().timestamp()}",
            "content": content,
            "role": role,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"새 메시지 생성: {role} - {content[:50]}...")
        
        messages = load_messages()
        messages.append(message_data)
        save_messages(messages)
        
        return JSONResponse(content={"message": message_data})
    except Exception as e:
        logger.error(f"메시지 생성 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "메시지 생성 실패"})

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

# 사용자 관리 API
@app.post("/api/login")
async def login(request: Request):
    """사용자 로그인"""
    try:
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        
        logger.info(f"로그인 시도: {email}")
        
        # 관리자 계정 체크 (여러 관리자 계정 지원)
        admin_accounts = {
            "admin@eora.com": {"password": "admin123", "username": "관리자"},
            "admin": {"password": "admin123", "username": "관리자"},
            "eora@admin.com": {"password": "admin123", "username": "EORA 관리자"}
        }
        
        # 일반 사용자 계정
        user_accounts = {
            "user@eora.com": {"password": "user123", "username": "사용자"},
            "guest@eora.com": {"password": "guest123", "username": "게스트"}
        }
        
        # 관리자 계정 확인
        if email in admin_accounts and admin_accounts[email]["password"] == password:
            logger.info(f"관리자 로그인 성공: {email}")
            return JSONResponse(content={
                "success": True,
                "user": {
                    "email": email,
                    "username": admin_accounts[email]["username"],
                    "is_admin": True,
                    "role": "admin"
                },
                "message": "관리자 로그인 성공"
            })
        
        # 일반 사용자 계정 확인
        elif email in user_accounts and user_accounts[email]["password"] == password:
            logger.info(f"일반 사용자 로그인 성공: {email}")
            return JSONResponse(content={
                "success": True,
                "user": {
                    "email": email,
                    "username": user_accounts[email]["username"],
                    "is_admin": False,
                    "role": "user"
                },
                "message": "로그인 성공"
            })
        
        # 게스트 로그인 (비밀번호 없이)
        elif email == "guest" or email == "guest@eora.com":
            logger.info(f"게스트 로그인: {email}")
            return JSONResponse(content={
                "success": True,
                "user": {
                    "email": "guest@eora.com",
                    "username": "게스트",
                    "is_admin": False,
                    "role": "guest"
                },
                "message": "게스트 로그인 성공"
            })
        
        else:
            logger.warning(f"로그인 실패: {email}")
            return JSONResponse(content={
                "success": False,
                "message": "이메일 또는 비밀번호가 올바르지 않습니다."
            })
    except Exception as e:
        logger.error(f"로그인 API 오류: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "로그인 처리 중 오류가 발생했습니다."
        })

@app.post("/api/register")
async def register(request: Request):
    """사용자 회원가입"""
    try:
        data = await request.json()
        email = data.get("email", "")
        password = data.get("password", "")
        name = data.get("name", email.split("@")[0])
        
        # 간단한 검증
        if not email or not password:
            return JSONResponse(content={
                "success": False,
                "message": "이메일과 비밀번호를 입력해주세요."
            })
        
        if len(password) < 6:
            return JSONResponse(content={
                "success": False,
                "message": "비밀번호는 6자 이상이어야 합니다."
            })
        
        # 이미 존재하는 계정 체크 (간단한 예시)
        existing_accounts = ["admin@eora.com", "user@eora.com"]
        if email in existing_accounts:
            return JSONResponse(content={
                "success": False,
                "message": "이미 존재하는 계정입니다."
            })
        
        logger.info(f"새 사용자 등록: {email}")
        return JSONResponse(content={
            "success": True,
            "user": {
                "email": email,
                "name": name,
                "is_admin": False
            },
            "message": "회원가입이 완료되었습니다."
        })
    except Exception as e:
        logger.error(f"회원가입 API 오류: {e}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "회원가입 처리 중 오류가 발생했습니다."
        })

# 관리자 페이지 라우트
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """관리자 대시보드 페이지"""
    logger.info("관리자 대시보드 페이지 요청됨")
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>관리자 대시보드 - EORA</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            .header h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                color: #666;
                font-size: 1.1em;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .stat-card h3 {
                color: #667eea;
                font-size: 2em;
                margin-bottom: 10px;
            }
            .stat-card p {
                color: #666;
                font-size: 1.1em;
            }
            .nav-buttons {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }
            .nav-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 1.1em;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .nav-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌟 관리자 대시보드</h1>
                <p>EORA AI 시스템 관리 및 모니터링</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>12</h3>
                    <p>활성 세션</p>
                </div>
                <div class="stat-card">
                    <h3>1,247</h3>
                    <p>총 메시지</p>
                </div>
                <div class="stat-card">
                    <h3>98.5%</h3>
                    <p>시스템 가동률</p>
                </div>
                <div class="stat-card">
                    <h3>24</h3>
                    <p>등록된 사용자</p>
                </div>
            </div>
            
            <div class="nav-buttons">
                <a href="/memory" class="nav-btn">🧠 기억 관리</a>
                <a href="/admin" class="nav-btn">⚙️ 관리자 설정</a>
                <a href="/chat" class="nav-btn">💬 채팅 시스템</a>
                <a href="/" class="nav-btn">🏠 홈으로</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/memory", response_class=HTMLResponse)
async def memory_page(request: Request):
    """기억 관리 페이지"""
    logger.info("기억 관리 페이지 요청됨")
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>기억 관리 - EORA</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            .header h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                color: #666;
                font-size: 1.1em;
            }
            .memory-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .memory-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            .memory-card h3 {
                color: #667eea;
                font-size: 1.5em;
                margin-bottom: 15px;
            }
            .memory-card p {
                color: #666;
                margin-bottom: 15px;
                line-height: 1.6;
            }
            .memory-stats {
                display: flex;
                justify-content: space-between;
                margin-top: 20px;
            }
            .stat {
                text-align: center;
            }
            .stat .number {
                font-size: 1.5em;
                font-weight: bold;
                color: #667eea;
            }
            .stat .label {
                font-size: 0.9em;
                color: #666;
            }
            .nav-buttons {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }
            .nav-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 1.1em;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .nav-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 기억 관리 시스템</h1>
                <p>AI 기억 및 학습 데이터 관리</p>
            </div>
            
            <div class="memory-grid">
                <div class="memory-card">
                    <h3>단기 기억</h3>
                    <p>현재 세션에서 생성된 임시 기억 데이터</p>
                    <div class="memory-stats">
                        <div class="stat">
                            <div class="number">156</div>
                            <div class="label">기억 단위</div>
                        </div>
                        <div class="stat">
                            <div class="number">2.3MB</div>
                            <div class="label">용량</div>
                        </div>
                    </div>
                </div>
                
                <div class="memory-card">
                    <h3>장기 기억</h3>
                    <p>영구적으로 저장된 학습된 패턴과 지식</p>
                    <div class="memory-stats">
                        <div class="stat">
                            <div class="number">1,247</div>
                            <div class="label">기억 단위</div>
                        </div>
                        <div class="stat">
                            <div class="number">45.7MB</div>
                            <div class="label">용량</div>
                        </div>
                    </div>
                </div>
                
                <div class="memory-card">
                    <h3>감정 기억</h3>
                    <p>사용자 상호작용에서 학습된 감정 패턴</p>
                    <div class="memory-stats">
                        <div class="stat">
                            <div class="number">89</div>
                            <div class="label">감정 패턴</div>
                        </div>
                        <div class="stat">
                            <div class="number">12.1MB</div>
                            <div class="label">용량</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="nav-buttons">
                <a href="/dashboard" class="nav-btn">📊 대시보드</a>
                <a href="/admin" class="nav-btn">⚙️ 관리자 설정</a>
                <a href="/chat" class="nav-btn">💬 채팅 시스템</a>
                <a href="/" class="nav-btn">🏠 홈으로</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """관리자 페이지"""
    logger.info("관리자 페이지 요청됨")
    with open("templates/admin.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

# 관리자 API 엔드포인트들
@app.get("/api/admin/stats")
async def admin_stats():
    """관리자 통계 API"""
    try:
        sessions = load_sessions()
        messages = load_messages()
        
        stats = {
            "total_sessions": len(sessions),
            "total_messages": len(messages),
            "active_users": len(set([msg.get("user_id", "anonymous") for msg in messages])),
            "system_uptime": "98.5%",
            "memory_usage": "45.7MB",
            "cpu_usage": "23%",
            "disk_usage": "1.2GB"
        }
        
        logger.info("관리자 통계 조회")
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"관리자 통계 조회 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "통계 조회 실패"})

@app.get("/api/admin/users")
async def admin_users():
    """관리자 사용자 목록 API"""
    try:
        # 샘플 사용자 데이터
        users = [
            {
                "id": 1,
                "email": "admin@eora.com",
                "username": "관리자",
                "role": "admin",
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "last_login": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "email": "user@eora.com",
                "username": "사용자",
                "role": "user",
                "status": "active",
                "created_at": "2024-01-02T00:00:00Z",
                "last_login": "2024-01-14T15:20:00Z"
            },
            {
                "id": 3,
                "email": "guest@eora.com",
                "username": "게스트",
                "role": "guest",
                "status": "active",
                "created_at": "2024-01-03T00:00:00Z",
                "last_login": "2024-01-15T09:15:00Z"
            }
        ]
        
        logger.info("관리자 사용자 목록 조회")
        return JSONResponse(content={"users": users})
    except Exception as e:
        logger.error(f"관리자 사용자 목록 조회 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "사용자 목록 조회 실패"})

@app.get("/api/admin/sessions")
async def admin_sessions():
    """관리자 세션 목록 API"""
    try:
        sessions = load_sessions()
        messages = load_messages()
        
        # 세션별 메시지 수 계산
        session_stats = []
        for session in sessions:
            session_messages = [msg for msg in messages if msg.get("session_id") == session["id"]]
            session_stats.append({
                "id": session["id"],
                "name": session["name"],
                "created_at": session["created_at"],
                "message_count": len(session_messages),
                "last_activity": session_messages[-1]["timestamp"] if session_messages else session["created_at"],
                "status": "active"
            })
        
        logger.info("관리자 세션 목록 조회")
        return JSONResponse(content={"sessions": session_stats})
    except Exception as e:
        logger.error(f"관리자 세션 목록 조회 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "세션 목록 조회 실패"})

@app.get("/api/admin/logs")
async def admin_logs():
    """관리자 로그 API"""
    try:
        # 샘플 로그 데이터
        logs = [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "level": "INFO",
                "message": "관리자 로그인 성공: admin@eora.com",
                "user": "admin@eora.com"
            },
            {
                "timestamp": "2024-01-15T10:25:00Z",
                "level": "INFO",
                "message": "새 세션 생성: 테스트 세션",
                "user": "user@eora.com"
            },
            {
                "timestamp": "2024-01-15T10:20:00Z",
                "level": "WARNING",
                "message": "OpenAI API 키가 설정되지 않았습니다.",
                "user": "system"
            },
            {
                "timestamp": "2024-01-15T10:15:00Z",
                "level": "INFO",
                "message": "서버 시작 완료",
                "user": "system"
            }
        ]
        
        logger.info("관리자 로그 조회")
        return JSONResponse(content={"logs": logs})
    except Exception as e:
        logger.error(f"관리자 로그 조회 오류: {e}")
        return JSONResponse(status_code=500, content={"error": "로그 조회 실패"})

# 관리자 페이지들
@app.get("/prompt-management", response_class=HTMLResponse)
async def prompt_management_page(request: Request):
    """프롬프트 관리 페이지"""
    logger.info("프롬프트 관리 페이지 요청됨")
    with open("templates/prompt_management.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get("/storage-management", response_class=HTMLResponse)
async def storage_management_page(request: Request):
    """저장소 관리 페이지"""
    logger.info("저장소 관리 페이지 요청됨")
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>저장소 관리 - EORA</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            .header h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                color: #666;
                font-size: 1.1em;
            }
            .storage-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .storage-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            .storage-card h3 {
                color: #667eea;
                font-size: 1.5em;
                margin-bottom: 15px;
            }
            .storage-stats {
                display: flex;
                justify-content: space-between;
                margin-bottom: 15px;
            }
            .stat {
                text-align: center;
            }
            .stat .number {
                font-size: 1.5em;
                font-weight: bold;
                color: #667eea;
            }
            .stat .label {
                font-size: 0.9em;
                color: #666;
            }
            .progress-bar {
                width: 100%;
                height: 10px;
                background: #e9ecef;
                border-radius: 5px;
                overflow: hidden;
                margin-bottom: 15px;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                transition: width 0.3s ease;
            }
            .nav-buttons {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }
            .nav-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 1.1em;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .nav-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💾 저장소 관리</h1>
                <p>데이터 저장소 및 파일 시스템 관리</p>
            </div>
            
            <div class="storage-grid">
                <div class="storage-card">
                    <h3>세션 데이터</h3>
                    <div class="storage-stats">
                        <div class="stat">
                            <div class="number">12</div>
                            <div class="label">활성 세션</div>
                        </div>
                        <div class="stat">
                            <div class="number">2.3MB</div>
                            <div class="label">용량</div>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 45%;"></div>
                    </div>
                    <p style="color: #666; font-size: 0.9em;">총 5.1MB 중 2.3MB 사용</p>
                </div>
                
                <div class="storage-card">
                    <h3>메시지 데이터</h3>
                    <div class="storage-stats">
                        <div class="stat">
                            <div class="number">1,247</div>
                            <div class="label">메시지</div>
                        </div>
                        <div class="stat">
                            <div class="number">45.7MB</div>
                            <div class="label">용량</div>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 78%;"></div>
                    </div>
                    <p style="color: #666; font-size: 0.9em;">총 58.5MB 중 45.7MB 사용</p>
                </div>
                
                <div class="storage-card">
                    <h3>기억 데이터</h3>
                    <div class="storage-stats">
                        <div class="stat">
                            <div class="number">89</div>
                            <div class="label">기억 단위</div>
                        </div>
                        <div class="stat">
                            <div class="number">12.1MB</div>
                            <div class="label">용량</div>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 32%;"></div>
                    </div>
                    <p style="color: #666; font-size: 0.9em;">총 37.8MB 중 12.1MB 사용</p>
                </div>
                
                <div class="storage-card">
                    <h3>시스템 로그</h3>
                    <div class="storage-stats">
                        <div class="stat">
                            <div class="number">156</div>
                            <div class="label">로그 파일</div>
                        </div>
                        <div class="stat">
                            <div class="number">8.9MB</div>
                            <div class="label">용량</div>
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 67%;"></div>
                    </div>
                    <p style="color: #666; font-size: 0.9em;">총 13.3MB 중 8.9MB 사용</p>
                </div>
            </div>
            
            <div class="nav-buttons">
                <a href="/admin" class="nav-btn">🔙 관리자 페이지</a>
                <a href="/prompt-management" class="nav-btn">📝 프롬프트 관리</a>
                <a href="/point-management" class="nav-btn">⭐ 포인트 관리</a>
                <a href="/" class="nav-btn">🏠 홈으로</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """프로필 페이지"""
    logger.info("프로필 페이지 요청됨")
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/point-management", response_class=HTMLResponse)
async def point_management_page(request: Request):
    """포인트 관리 페이지"""
    logger.info("포인트 관리 페이지 요청됨")
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>포인트 관리 - EORA</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            .header h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                color: #666;
                font-size: 1.1em;
            }
            .point-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .point-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            .point-card h3 {
                color: #667eea;
                font-size: 1.5em;
                margin-bottom: 15px;
            }
            .point-item {
                margin-bottom: 20px;
                padding: 15px;
                background: rgba(102, 126, 234, 0.1);
                border-radius: 10px;
            }
            .point-item label {
                display: block;
                font-weight: bold;
                margin-bottom: 5px;
                color: #333;
            }
            .point-item input, .point-item select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 1em;
            }
            .nav-buttons {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
            }
            .nav-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 1.1em;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .nav-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⭐ 포인트 관리</h1>
                <p>사용자 포인트 및 보상 시스템 관리</p>
            </div>
            
            <div class="point-grid">
                <div class="point-card">
                    <h3>포인트 적립 규칙</h3>
                    <div class="point-item">
                        <label>메시지 전송</label>
                        <input type="number" value="1" min="0">
                    </div>
                    <div class="point-item">
                        <label>세션 생성</label>
                        <input type="number" value="5" min="0">
                    </div>
                    <div class="point-item">
                        <label>일일 로그인</label>
                        <input type="number" value="10" min="0">
                    </div>
                </div>
                
                <div class="point-card">
                    <h3>포인트 사용 규칙</h3>
                    <div class="point-item">
                        <label>고급 기능 사용</label>
                        <input type="number" value="50" min="0">
                    </div>
                    <div class="point-item">
                        <label>프리미엄 모델</label>
                        <input type="number" value="100" min="0">
                    </div>
                    <div class="point-item">
                        <label>기억 확장</label>
                        <input type="number" value="25" min="0">
                    </div>
                </div>
                
                <div class="point-card">
                    <h3>포인트 통계</h3>
                    <div class="point-item">
                        <label>총 적립 포인트</label>
                        <input type="text" value="12,450" readonly>
                    </div>
                    <div class="point-item">
                        <label>총 사용 포인트</label>
                        <input type="text" value="8,230" readonly>
                    </div>
                    <div class="point-item">
                        <label>현재 보유 포인트</label>
                        <input type="text" value="4,220" readonly>
                    </div>
                </div>
            </div>
            
            <div class="nav-buttons">
                <a href="/admin" class="nav-btn">🔙 관리자 페이지</a>
                <a href="/prompt-management" class="nav-btn">📝 프롬프트 관리</a>
                <a href="/storage-management" class="nav-btn">💾 저장소 관리</a>
                <a href="/" class="nav-btn">🏠 홈으로</a>
            </div>
        </div>
    </body>
    </html>
    """)

# 프롬프트 관리 API
@app.get("/api/prompts")
async def get_prompts():
    """AI별 프롬프트 데이터 조회"""
    try:
        if not prompts_data:
            load_prompts_data()
        
        # 데이터를 리스트 형태로 변환
        prompts_list = []
        for ai_name, ai_data in prompts_data.items():
            for category, category_prompts in ai_data.items():
                if isinstance(category_prompts, list):
                    for index, content in enumerate(category_prompts):
                        prompts_list.append({
                            "id": f"{ai_name}_{category}_{index}",
                            "ai_name": ai_name,
                            "category": category,
                            "content": content,
                            "content_index": index
                        })
                else:
                    # 단일 문자열인 경우
                    prompts_list.append({
                        "id": f"{ai_name}_{category}_0",
                        "ai_name": ai_name,
                        "category": category,
                        "content": str(category_prompts),
                        "content_index": 0
                    })
        
        logger.info(f"프롬프트 데이터 조회 완료: {len(prompts_list)}개")
        return prompts_list
    except Exception as e:
        logger.error(f"프롬프트 데이터 조회 오류: {e}")
        return []

@app.post("/api/prompts/category")
async def save_prompt_category(request: Request):
    """카테고리별 프롬프트 저장"""
    try:
        data = await request.json()
        ai_name = data.get("ai_name")
        category = data.get("category")
        prompts = data.get("prompts", [])
        
        prompts_file = "ai_brain/ai_prompts.json"
        
        # 기존 데이터 로드
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        else:
            all_data = {}
        
        # AI별 데이터 초기화
        if ai_name not in all_data:
            all_data[ai_name] = {}
        
        # 카테고리별 데이터 초기화
        if category not in all_data[ai_name]:
            all_data[ai_name][category] = []
        
        # ai1의 system 프롬프트는 문자열 배열로 저장
        if ai_name == "ai1" and category == "system":
            # textarea의 내용을 빈 줄로 분할하여 각각을 배열 요소로 저장
            if prompts and len(prompts) > 0:
                content = prompts[0].get("content", "")
                # 빈 줄을 기준으로 분할하고 각 줄을 개별 프롬프트로 저장
                lines = [line.strip() for line in content.split('\n\n') if line.strip()]
                all_data[ai_name][category] = lines
            else:
                all_data[ai_name][category] = []
        else:
            # 다른 AI나 카테고리는 기존 방식대로 저장
            all_data[ai_name][category] = [prompt.get("content", "") for prompt in prompts]
        
        # 파일에 저장
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        # 전역 데이터 업데이트
        global prompts_data
        prompts_data = all_data
        
        logger.info(f"✅ 프롬프트 저장 완료: {ai_name} - {category}")
        return {"status": "success", "message": "프롬프트가 저장되었습니다."}
        
    except Exception as e:
        logger.error(f"❌ 프롬프트 저장 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"저장 중 오류가 발생했습니다: {str(e)}"}
        )

# 프로필 관련 API
@app.get("/api/profile")
async def get_profile():
    """사용자 프로필 정보 조회"""
    try:
        # 현재는 기본 프로필 정보를 반환
        # 실제로는 로그인된 사용자 정보를 데이터베이스에서 조회해야 함
        profile_data = {
            "username": "admin",
            "email": "admin@eora.com",
            "role": "관리자",
            "join_date": "2024-01-01",
            "last_login": "2024-07-14",
            "stats": {
                "total_sessions": 25,
                "total_messages": 156,
                "total_points": 1250,
                "login_streak": 7
            },
            "preferences": {
                "language": "ko",
                "theme": "dark",
                "notifications": True
            }
        }
        
        logger.info("프로필 정보 조회 완료")
        return profile_data
        
    except Exception as e:
        logger.error(f"프로필 정보 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "프로필 정보를 가져올 수 없습니다."}
        )

@app.post("/api/profile/update")
async def update_profile(request: Request):
    """프로필 정보 업데이트"""
    try:
        data = await request.json()
        
        # 실제로는 데이터베이스에 업데이트해야 함
        logger.info(f"프로필 업데이트 요청: {data}")
        
        return {"status": "success", "message": "프로필이 업데이트되었습니다."}
        
    except Exception as e:
        logger.error(f"프로필 업데이트 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "프로필 업데이트에 실패했습니다."}
        )

# 프롬프트 데이터 재로드 API
@app.post("/api/prompts/reload")
async def reload_prompts():
    """프롬프트 데이터를 다시 로드합니다."""
    try:
        if load_prompts_data():
            logger.info("✅ 프롬프트 데이터 재로드 완료")
            return {"status": "success", "message": "프롬프트 데이터가 재로드되었습니다."}
        else:
            logger.warning("⚠️ 프롬프트 데이터 재로드 실패")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "프롬프트 데이터 재로드에 실패했습니다."}
            )
    except Exception as e:
        logger.error(f"❌ 프롬프트 데이터 재로드 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"프롬프트 데이터 재로드 중 오류가 발생했습니다: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True) 