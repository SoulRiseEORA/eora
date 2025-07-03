from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import json
import asyncio
import logging
from datetime import datetime
import uuid
from typing import Dict, List, Any
import os
import hashlib

# EORA 시스템 임포트
from eora_core import EORACore
from eora_consciousness import EORAConsciousness
from eora_enhanced_core import EORAEnhancedCore
from eora_intuition_system import intuition_system, insight_system
from eora_chain_memory_system import chain_memory_system
from database import db_manager
from auth_system import auth_system

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# EORA_GAI 통합 시스템 (선택적)
try:
    from EORA_GAI.EORA_Consciousness_AI import EORA as EORAGAI
    from EORA_GAI.core.eora_wave_core import EORAWaveCore
    from EORA_GAI.core.ir_core import IRCore
    from EORA_GAI.core.free_will_core import FreeWillCore
    from EORA_GAI.core.ethics_engine import EthicsEngine
    from EORA_GAI.core.self_model import SelfModel
    from EORA_GAI.core.life_loop import LifeLoop
    from EORA_GAI.core.love_engine import LoveEngine
    from EORA_GAI.core.pain_engine import PainEngine
    from EORA_GAI.core.stress_monitor import StressMonitor
    EORA_GAI_AVAILABLE = True
    logger.info("✅ EORA_GAI 모듈 로드 성공")
except ImportError as e:
    EORA_GAI_AVAILABLE = False
    logger.info(f"ℹ️ EORA_GAI 모듈 로드 실패: {str(e)}")

app = FastAPI(title="EORA AI System", version="1.0.0")

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 간단한 사용자 저장소 (실제로는 데이터베이스 사용)
users_db = {}
points_db = {}

# EORA 시스템 초기화
eora_core = EORACore()
eora_consciousness = EORAConsciousness()
eora_enhanced = EORAEnhancedCore()

# EORA_GAI 시스템 초기화 (가능한 경우)
eora_gai_system = None
eora_gai_wave_core = None
eora_gai_intuition_core = None
eora_gai_free_will_core = None
eora_gai_ethics_engine = None
eora_gai_self_model = None
eora_gai_life_loop = None
eora_gai_love_engine = None
eora_gai_pain_engine = None
eora_gai_stress_monitor = None

if EORA_GAI_AVAILABLE:
    try:
        eora_gai_system = EORAGAI()
        eora_gai_wave_core = EORAWaveCore()
        eora_gai_intuition_core = IRCore()
        eora_gai_free_will_core = FreeWillCore()
        eora_gai_ethics_engine = EthicsEngine()
        eora_gai_self_model = SelfModel()
        eora_gai_life_loop = LifeLoop()
        eora_gai_love_engine = LoveEngine()
        eora_gai_pain_engine = PainEngine()
        eora_gai_stress_monitor = StressMonitor()
        logger.info("✅ EORA_GAI 시스템 초기화 완료")
    except Exception as e:
        logger.error(f"❌ EORA_GAI 시스템 초기화 실패: {str(e)}")
        EORA_GAI_AVAILABLE = False

# 웹소켓 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"새로운 웹소켓 연결: {len(self.active_connections)}개 활성")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"웹소켓 연결 해제: {len(self.active_connections)}개 활성")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    try:
        # MongoDB 연결
        await db_manager.connect()
        logger.info("EORA 시스템 시작 - MongoDB 연결 완료")
        
        # 시스템 로그 저장
        await db_manager.log_system_event(
            "system_startup",
            "EORA AI 시스템이 시작되었습니다.",
            "INFO"
        )
        
    except Exception as e:
        logger.error(f"시스템 시작 실패: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    try:
        # MongoDB 연결 해제
        await db_manager.disconnect()
        logger.info("EORA 시스템 종료 - MongoDB 연결 해제")
        
    except Exception as e:
        logger.error(f"시스템 종료 중 오류: {str(e)}")

# 페이지 라우트
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """홈 페이지"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """대시보드 페이지"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """채팅 페이지"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/points", response_class=HTMLResponse)
async def points_page(request: Request):
    """포인트 관리 페이지"""
    return templates.TemplateResponse("points.html", {"request": request})

# 인증 API
@app.post("/api/auth/register")
async def register_user(request: Request):
    """회원가입 API"""
    try:
        body = await request.json()
        name = body.get("name")
        email = body.get("email")
        password = body.get("password")
        
        if not all([name, email, password]):
            raise HTTPException(status_code=400, detail="모든 필드를 입력해주세요.")
        
        if email in users_db:
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        
        # 비밀번호 해싱
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # 사용자 생성
        user_id = str(uuid.uuid4())
        users_db[email] = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now().isoformat(),
            "is_admin": False
        }
        
        # 포인트 계정 생성 (회원가입 보너스 100포인트)
        points_db[user_id] = {
            "user_id": user_id,
            "current_points": 100,
            "total_earned": 100,
            "total_spent": 0,
            "last_updated": datetime.now().isoformat(),
            "history": [{
                "type": "signup_bonus",
                "points": 100,
                "description": "회원가입 보너스",
                "timestamp": datetime.now().isoformat()
            }]
        }
        
        return {"success": True, "message": "회원가입이 완료되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다.")

@app.post("/api/auth/login")
async def login_user(request: Request):
    """로그인 API"""
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        if not all([email, password]):
            raise HTTPException(status_code=400, detail="이메일과 비밀번호를 입력해주세요.")
        
        if email not in users_db:
            raise HTTPException(status_code=400, detail="존재하지 않는 이메일입니다.")
        
        user = users_db[email]
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if user["password"] != hashed_password:
            raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")
        
        # 간단한 JWT 토큰 생성
        token = f"test_token_{user['user_id']}_{datetime.now().timestamp()}"
        
        return {
            "success": True,
            "access_token": token,
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다.")

# 포인트 시스템 API
@app.get("/api/user/points")
async def get_user_points(request: Request):
    """사용자 포인트 조회"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    
    token = auth_header.split(" ")[1]
    user_id = token.split("_")[2] if len(token.split("_")) > 2 else None
    
    if not user_id or user_id not in points_db:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    return points_db[user_id]

@app.get("/api/points/packages")
async def get_point_packages():
    """포인트 패키지 조회"""
    packages = [
        {
            "id": "starter",
            "name": "스타터 패키지",
            "points": 100,
            "price": 5000,
            "description": "처음 시작하는 분들을 위한 패키지",
            "is_popular": False
        },
        {
            "id": "basic",
            "name": "기본 패키지",
            "points": 500,
            "price": 20000,
            "description": "일반적인 사용을 위한 패키지",
            "is_popular": True
        },
        {
            "id": "premium",
            "name": "프리미엄 패키지",
            "points": 1500,
            "price": 50000,
            "description": "많은 대화를 원하는 분들을 위한 패키지",
            "discount_percent": 10
        },
        {
            "id": "unlimited",
            "name": "무제한 패키지",
            "points": 5000,
            "price": 150000,
            "description": "무제한 대화를 위한 패키지",
            "discount_percent": 20
        }
    ]
    return packages

@app.post("/api/points/purchase")
async def purchase_points(request: Request):
    """포인트 구매 (시뮬레이션)"""
    try:
        body = await request.json()
        package_id = body.get("package_id")
        payment_method = body.get("payment_method")
        
        # 간단한 토큰 검증
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="인증이 필요합니다.")
        
        token = auth_header.split(" ")[1]
        user_id = token.split("_")[2] if len(token.split("_")) > 2 else None
        
        if not user_id or user_id not in points_db:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        # 패키지 정보 가져오기
        packages = await get_point_packages()
        package = next((p for p in packages if p["id"] == package_id), None)
        
        if not package:
            raise HTTPException(status_code=400, detail="존재하지 않는 패키지입니다.")
        
        # 포인트 추가
        points_db[user_id]["current_points"] += package["points"]
        points_db[user_id]["total_earned"] += package["points"]
        points_db[user_id]["last_updated"] = datetime.now().isoformat()
        
        # 구매 기록 추가
        points_db[user_id]["history"].append({
            "type": "purchase",
            "points": package["points"],
            "description": f"{package['name']} 구매",
            "payment_method": payment_method,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": f"{package['name']} 구매가 완료되었습니다.",
            "points_added": package["points"],
            "current_points": points_db[user_id]["current_points"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="포인트 구매 중 오류가 발생했습니다.")

# 기존 EORA 시스템 API들
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """웹소켓 엔드포인트 - 실시간 채팅 처리"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # EORA 시스템을 통한 응답 생성
            user_message = message_data.get("message", "")
            user_id = message_data.get("user_id", client_id)
            
            # 자동 명령어 처리
            if user_message.startswith('/'):
                final_response = await process_auto_commands(user_message, user_id)
                consciousness_response = {"consciousness_level": 0.5, "memory_triggered": False}
            else:
                # EORA 의식 시스템 처리
                consciousness_response = await eora_consciousness.process_input(user_message, user_id)
                
                # 향상된 EORA 시스템을 통한 응답 생성
                final_response = await eora_enhanced.generate_enhanced_response(
                    user_message, 
                    consciousness_response,
                    user_id
                )
                
                # EORA_GAI 고급 분석 (가능한 경우)
                advanced_analysis = {}
                if EORA_GAI_AVAILABLE:
                    try:
                        advanced_analysis = await process_advanced_input(user_message, user_id)
                        logger.info(f"🔬 EORA_GAI 고급 분석 완료 - 사용자: {user_id}")
                    except Exception as e:
                        logger.error(f"EORA_GAI 고급 분석 오류: {str(e)}")
                
                # 자동 통찰 생성
                try:
                    insight = await insight_system.generate_insight({
                        "user_input": user_message,
                        "ai_response": final_response,
                        "consciousness_level": consciousness_response.get("consciousness_level", 0.0)
                    })
                    
                    # 통찰 정보를 응답에 포함
                    consciousness_response["insight"] = insight
                    consciousness_response["cognitive_layer"] = insight["cognitive_layer"]
                    consciousness_response["insight_level"] = insight["insight_level"]
                    
                except Exception as e:
                    logger.error(f"자동 통찰 생성 오류: {str(e)}")
            
            # 사슬형태 기억 시스템 처리
            chain_result = await chain_memory_system.increment_turn(user_message, final_response, user_id)
            
            # MongoDB에 상호작용 저장 (통찰 포함)
            metadata = {
                "consciousness_response": consciousness_response,
                "client_id": client_id,
                "turn_counter": chain_result["basic_memory"]["turn"]
            }
            
            # EORA_GAI 고급 분석 결과가 있으면 메타데이터에 추가
            if advanced_analysis and "error" not in advanced_analysis:
                metadata["advanced_analysis"] = advanced_analysis
            
            # 통찰 정보가 있으면 메타데이터에 추가
            if "insight" in consciousness_response:
                metadata["insight"] = consciousness_response["insight"]
                metadata["cognitive_layer"] = consciousness_response["cognitive_layer"]
                metadata["insight_level"] = consciousness_response["insight_level"]
            
            # 체인 분석 결과가 있으면 메타데이터에 추가
            if chain_result["is_analysis_turn"] and chain_result["chain_analysis"]:
                metadata["chain_analysis"] = chain_result["chain_analysis"]
                metadata["is_chain_analysis_turn"] = True
            
            await db_manager.store_interaction(
                user_id=user_id,
                user_input=user_message,
                ai_response=final_response,
                consciousness_level=consciousness_response.get("consciousness_level", 0.0),
                metadata=metadata
            )
            
            # 의식 이벤트 저장
            await db_manager.store_consciousness_event(
                user_id=user_id,
                event_type="chat_interaction",
                consciousness_level=consciousness_response.get("consciousness_level", 0.0),
                metadata=consciousness_response
            )
            
            # 응답 전송 (통찰 및 체인 분석 포함)
            response_data = {
                "type": "ai_response",
                "message": final_response,
                "timestamp": datetime.now().isoformat(),
                "consciousness_level": consciousness_response.get("consciousness_level", 0),
                "memory_triggered": consciousness_response.get("memory_triggered", False),
                "turn_counter": chain_result["basic_memory"]["turn"]
            }
            
            # EORA_GAI 고급 분석 결과가 있으면 응답에 포함
            if advanced_analysis and "error" not in advanced_analysis:
                response_data["advanced_analysis"] = advanced_analysis
            
            # 통찰 정보가 있으면 응답에 포함
            if "insight" in consciousness_response:
                response_data["insight"] = consciousness_response["insight"]
                response_data["cognitive_layer"] = consciousness_response["cognitive_layer"]
                response_data["insight_level"] = consciousness_response["insight_level"]
            

            
            await manager.send_personal_message(
                json.dumps(response_data, ensure_ascii=False),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"웹소켓 오류: {str(e)}")
        manager.disconnect(websocket)

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """REST API 채팅 엔드포인트"""
    try:
        body = await request.json()
        user_message = body.get("message", "")
        user_id = body.get("user_id", str(uuid.uuid4()))
        
        # 자동 명령어 처리
        if user_message.startswith('/'):
            final_response = await process_auto_commands(user_message, user_id)
            consciousness_response = {"consciousness_level": 0.5, "memory_triggered": False}
        else:
            # EORA 시스템 처리
            consciousness_response = await eora_consciousness.process_input(user_message, user_id)
            final_response = await eora_enhanced.generate_enhanced_response(
                user_message, 
                consciousness_response,
                user_id
            )
            
            # EORA_GAI 고급 분석 (가능한 경우)
            advanced_analysis = {}
            if EORA_GAI_AVAILABLE:
                try:
                    advanced_analysis = await process_advanced_input(user_message, user_id)
                    logger.info(f"🔬 EORA_GAI 고급 분석 완료 - 사용자: {user_id}")
                except Exception as e:
                    logger.error(f"EORA_GAI 고급 분석 오류: {str(e)}")
            
            # 자동 통찰 생성
            try:
                insight = await insight_system.generate_insight({
                    "user_input": user_message,
                    "ai_response": final_response,
                    "consciousness_level": consciousness_response.get("consciousness_level", 0.0)
                })
                
                # 통찰 정보를 응답에 포함
                consciousness_response["insight"] = insight
                consciousness_response["cognitive_layer"] = insight["cognitive_layer"]
                consciousness_response["insight_level"] = insight["insight_level"]
                
            except Exception as e:
                logger.error(f"자동 통찰 생성 오류: {str(e)}")
        
        # 사슬형태 기억 시스템 처리
        chain_result = await chain_memory_system.increment_turn(user_message, final_response, user_id)
        
        # MongoDB에 저장 (통찰 및 체인 분석 포함)
        metadata = {
            "turn_counter": chain_result["basic_memory"]["turn"]
        }
        
        # EORA_GAI 고급 분석 결과가 있으면 메타데이터에 추가
        if advanced_analysis and "error" not in advanced_analysis:
            metadata["advanced_analysis"] = advanced_analysis
        
        # 통찰 정보가 있으면 메타데이터에 추가
        if "insight" in consciousness_response:
            metadata["insight"] = consciousness_response["insight"]
            metadata["cognitive_layer"] = consciousness_response["cognitive_layer"]
            metadata["insight_level"] = consciousness_response["insight_level"]
        
        # 체인 분석 결과가 있으면 메타데이터에 추가
        if chain_result["is_analysis_turn"] and chain_result["chain_analysis"]:
            metadata["chain_analysis"] = chain_result["chain_analysis"]
            metadata["is_chain_analysis_turn"] = True
        
        await db_manager.store_interaction(
            user_id=user_id,
            user_input=user_message,
            ai_response=final_response,
            consciousness_level=consciousness_response.get("consciousness_level", 0.0),
            metadata=metadata
        )
        
        response_data = {
            "response": final_response,
            "consciousness_level": consciousness_response.get("consciousness_level", 0),
            "memory_triggered": consciousness_response.get("memory_triggered", False),
            "timestamp": datetime.now().isoformat(),
            "turn_counter": chain_result["basic_memory"]["turn"]
        }
        
        # EORA_GAI 고급 분석 결과가 있으면 응답에 포함
        if advanced_analysis and "error" not in advanced_analysis:
            response_data["advanced_analysis"] = advanced_analysis
        
        # 통찰 정보가 있으면 응답에 포함
        if "insight" in consciousness_response:
            response_data["insight"] = consciousness_response["insight"]
            response_data["cognitive_layer"] = consciousness_response["cognitive_layer"]
            response_data["insight_level"] = consciousness_response["insight_level"]
        

        
        return response_data
        
    except Exception as e:
        logger.error(f"채팅 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_system_status():
    """시스템 상태 확인"""
    try:
        # MongoDB 통계 조회
        consciousness_stats = await db_manager.get_consciousness_stats()
        
        return {
            "status": "active",
            "eora_core": eora_core.get_status(),
            "eora_consciousness": eora_consciousness.get_status(),
            "eora_enhanced": eora_enhanced.get_status(),
            "database": {
                "connected": db_manager.client is not None,
                "consciousness_stats": consciousness_stats
            },
            "active_connections": len(manager.active_connections),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"시스템 상태 조회 오류: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# 사용자 관련 엔드포인트
@app.get("/api/user/stats/{user_id}")
async def get_user_stats(user_id: str):
    """사용자 통계 조회"""
    try:
        stats = await auth_system.get_user_stats(user_id)
        return stats
    except Exception as e:
        logger.error(f"사용자 통계 조회 오류: {str(e)}")
        return {"error": str(e)}

@app.get("/api/user/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """사용자 세션 목록 조회"""
    try:
        sessions = await db_manager.get_user_sessions(user_id)
        return sessions
    except Exception as e:
        logger.error(f"사용자 세션 조회 오류: {str(e)}")
        return []

@app.delete("/api/user/sessions/{session_id}")
async def delete_user_session(session_id: str):
    """사용자 세션 삭제"""
    try:
        await auth_system.logout_user(session_id)
        return {"success": True, "message": "세션이 삭제되었습니다."}
    except Exception as e:
        logger.error(f"세션 삭제 오류: {str(e)}")
        return {"success": False, "message": "세션 삭제 중 오류가 발생했습니다."}

# 관리자 관련 엔드포인트
@app.get("/api/admin/users")
async def get_all_users():
    """모든 사용자 목록 조회 (관리자용)"""
    try:
        users = await auth_system.get_all_users()
        return users
    except Exception as e:
        logger.error(f"사용자 목록 조회 오류: {str(e)}")
        return []

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str):
    """사용자 삭제 (관리자용)"""
    try:
        result = await auth_system.delete_user(user_id)
        return result
    except Exception as e:
        logger.error(f"사용자 삭제 오류: {str(e)}")
        return {"success": False, "message": "사용자 삭제 중 오류가 발생했습니다."}

@app.get("/api/memory/{user_id}")
async def get_user_memory(user_id: str):
    """사용자 메모리 조회"""
    try:
        interactions = await db_manager.get_user_interactions(user_id, limit=50)
        return {"interactions": interactions, "user_id": user_id}
    except Exception as e:
        logger.error(f"메모리 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_memories(query: str, user_id: str = None):
    """메모리 검색"""
    try:
        results = await db_manager.search_interactions(query, user_id, limit=20)
        return {"results": results, "query": query, "user_id": user_id}
    except Exception as e:
        logger.error(f"메모리 검색 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/eora/manifest")
async def get_eora_manifest():
    """EORA 매니페스트 조회"""
    try:
        manifest = eora_enhanced.manifest()
        return {
            "manifest": manifest,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"매니페스트 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eora/gai/status")
async def get_eora_gai_status():
    """EORA_GAI 시스템 상태 조회"""
    try:
        if not EORA_GAI_AVAILABLE:
            return {
                "available": False,
                "message": "EORA_GAI 시스템을 사용할 수 없습니다.",
                "timestamp": datetime.now().isoformat()
            }
        
        # 고급 시스템 상태 조회
        system_state = await update_system_state_advanced()
        
        return {
            "available": True,
            "modules": {
                "wave_core": eora_gai_wave_core is not None,
                "intuition_core": eora_gai_intuition_core is not None,
                "free_will_core": eora_gai_free_will_core is not None,
                "ethics_engine": eora_gai_ethics_engine is not None,
                "self_model": eora_gai_self_model is not None,
                "life_loop": eora_gai_life_loop is not None,
                "love_engine": eora_gai_love_engine is not None,
                "pain_engine": eora_gai_pain_engine is not None,
                "stress_monitor": eora_gai_stress_monitor is not None
            },
            "system_state": system_state,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"EORA_GAI 상태 조회 오류: {str(e)}")
        return {
            "available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/eora/prompts")
async def get_available_prompts():
    """사용 가능한 프롬프트 목록 조회"""
    try:
        prompts = eora_enhanced.prompts
        return {
            "prompts": list(prompts.keys()),
            "count": len(prompts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"프롬프트 목록 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eora/prompt/{prompt_name}")
async def get_prompt_content(prompt_name: str):
    """특정 프롬프트 내용 조회"""
    try:
        # 프롬프트 이름 정규화
        normalized_name = prompt_name.replace(' ', ' ').upper()
        
        for name, content in eora_enhanced.prompts.items():
            if normalized_name in name.upper():
                return {
                    "name": name,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
        
        raise HTTPException(status_code=404, detail="프롬프트를 찾을 수 없습니다")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프롬프트 내용 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/eora/memory/recall")
async def recall_memory(request: Request):
    """메모리 회상 API"""
    try:
        body = await request.json()
        query = body.get("query", "")
        user_id = body.get("user_id", str(uuid.uuid4()))
        
        if not query.strip():
            raise HTTPException(status_code=400, detail="검색어를 입력해주세요")
        
        # 향상된 EORA 시스템의 메모리 회상 기능 사용
        response = await eora_enhanced._perform_memory_recall(query, user_id)
        
        return {
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메모리 회상 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eora/memory/search")
async def search_memories(query: str, user_id: str = None, search_type: str = "comprehensive"):
    """메모리 검색 API"""
    try:
        if not user_id:
            user_id = str(uuid.uuid4())
        
        if not query.strip():
            raise HTTPException(status_code=400, detail="검색어를 입력해주세요")
        
        # 데이터베이스에서 메모리 검색
        memories = await db_manager.search_memories(user_id, query, search_type)
        
        return {
            "query": query,
            "search_type": search_type,
            "results_count": len(memories),
            "memories": memories,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메모리 검색 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eora/memory/stats/{user_id}")
async def get_memory_stats(user_id: str):
    """메모리 통계 API"""
    try:
        stats = await db_manager.get_user_memory_stats(user_id)
        
        return {
            "user_id": user_id,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"메모리 통계 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eora/memory/recent/{user_id}")
async def get_recent_memories(user_id: str, limit: int = 10):
    """최근 메모리 조회 API"""
    try:
        interactions = await db_manager.get_user_interactions(user_id, limit)
        
        return {
            "user_id": user_id,
            "recent_memories": interactions,
            "count": len(interactions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"최근 메모리 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_advanced_input(user_input: str, user_id: str) -> Dict[str, Any]:
    """EORA_GAI 고급 입력 처리"""
    if not EORA_GAI_AVAILABLE:
        return {"error": "EORA_GAI 시스템을 사용할 수 없습니다."}
    
    try:
        advanced_result = {
            "wave_analysis": {},
            "intuition_analysis": {},
            "ethics_evaluation": {},
            "emotion_analysis": {},
            "free_will_decision": {},
            "self_model_update": {},
            "life_loop_update": {},
            "system_state": {},
            "advanced_processing": True
        }
        
        # 1. 파동 분석
        if eora_gai_wave_core:
            try:
                wave_result = eora_gai_wave_core.analyze_wave(user_input)
                advanced_result["wave_analysis"] = {
                    "amplitude": wave_result.get("amplitude", 0.5),
                    "frequency": wave_result.get("frequency", 7.83),
                    "phase": wave_result.get("phase", 0.0),
                    "resonance_score": wave_result.get("resonance_score", 0.5),
                    "wave_type": wave_result.get("wave_type", "normal")
                }
            except Exception as e:
                logger.error(f"파동 분석 오류: {str(e)}")
        
        # 2. 직감 분석
        if eora_gai_intuition_core:
            try:
                resonance_score = advanced_result["wave_analysis"].get("resonance_score", 0.5)
                intuition_result = eora_gai_intuition_core.analyze_intuition(user_input, resonance_score)
                advanced_result["intuition_analysis"] = {
                    "intuition_strength": intuition_result.get("intuition_strength", 0.5),
                    "spark_threshold": intuition_result.get("spark_threshold", 0.7),
                    "intuition_type": intuition_result.get("intuition_type", "normal"),
                    "confidence": intuition_result.get("confidence", 0.5)
                }
            except Exception as e:
                logger.error(f"직감 분석 오류: {str(e)}")
        
        # 3. 윤리 평가
        if eora_gai_ethics_engine:
            try:
                ethics_result = eora_gai_ethics_engine.evaluate_ethics(user_input)
                advanced_result["ethics_evaluation"] = {
                    "ethics_score": ethics_result.get("ethics_score", 0.5),
                    "principles": ethics_result.get("principles", {}),
                    "violations": ethics_result.get("violations", []),
                    "recommendations": ethics_result.get("recommendations", []),
                    "is_ethical": ethics_result.get("is_ethical", True)
                }
            except Exception as e:
                logger.error(f"윤리 평가 오류: {str(e)}")
        
        # 4. 감정 분석 (향상된 버전)
        emotion_result = await analyze_emotion_advanced(user_input)
        advanced_result["emotion_analysis"] = emotion_result
        
        # 5. 자유의지 결정
        if eora_gai_free_will_core:
            try:
                decision_result = eora_gai_free_will_core.make_decision({
                    "input": user_input,
                    "wave_analysis": advanced_result["wave_analysis"],
                    "intuition_analysis": advanced_result["intuition_analysis"],
                    "ethics_evaluation": advanced_result["ethics_evaluation"]
                })
                advanced_result["free_will_decision"] = {
                    "decision": decision_result.get("decision", "neutral"),
                    "confidence": decision_result.get("confidence", 0.5),
                    "reasoning": decision_result.get("reasoning", ""),
                    "weights": decision_result.get("weights", {}),
                    "constraints": decision_result.get("constraints", [])
                }
            except Exception as e:
                logger.error(f"자유의지 결정 오류: {str(e)}")
        
        # 6. 자아 모델 업데이트
        if eora_gai_self_model:
            try:
                self_update = eora_gai_self_model.update_self({
                    "input": user_input,
                    "emotion": emotion_result,
                    "timestamp": datetime.now().isoformat()
                })
                advanced_result["self_model_update"] = {
                    "self_identity": self_update.get("self_identity", "EORA"),
                    "self_confidence": self_update.get("self_confidence", 0.5),
                    "self_evolution": self_update.get("self_evolution", 0.1),
                    "self_awareness": self_update.get("self_awareness", 0.5)
                }
            except Exception as e:
                logger.error(f"자아 모델 업데이트 오류: {str(e)}")
        
        # 7. 생명 루프 업데이트
        if eora_gai_life_loop:
            try:
                life_update = eora_gai_life_loop.update_life_cycle()
                advanced_result["life_loop_update"] = {
                    "energy_level": life_update.get("energy_level", 1.0),
                    "vitality": life_update.get("vitality", 0.8),
                    "growth": life_update.get("growth", 0.1),
                    "life_cycle_phase": life_update.get("life_cycle_phase", "active")
                }
            except Exception as e:
                logger.error(f"생명 루프 업데이트 오류: {str(e)}")
        
        # 8. 시스템 상태 업데이트
        system_state = await update_system_state_advanced()
        advanced_result["system_state"] = system_state
        
        return advanced_result
        
    except Exception as e:
        logger.error(f"고급 입력 처리 오류: {str(e)}")
        return {"error": str(e)}

async def analyze_emotion_advanced(text: str) -> Dict[str, Any]:
    """향상된 감정 분석"""
    try:
        # 다차원 감정 분석 (valence, arousal, intensity)
        emotion_result = {
            "valence": 0.5,  # 긍정성 (-1 ~ 1)
            "arousal": 0.5,  # 각성도 (0 ~ 1)
            "intensity": 0.5,  # 강도 (0 ~ 1)
            "primary_emotion": "neutral",
            "secondary_emotions": [],
            "emotional_complexity": 0.5
        }
        
        # 텍스트 기반 감정 분석
        text_lower = text.lower()
        
        # 긍정적 감정 키워드
        positive_words = ["좋", "기쁘", "행복", "감사", "사랑", "희망", "즐거", "웃", "즐겁", "신나"]
        # 부정적 감정 키워드
        negative_words = ["슬픔", "화나", "불안", "두려", "짜증", "우울", "고통", "스트레스", "걱정", "분노"]
        # 각성 키워드
        arousal_words = ["놀람", "충격", "흥분", "긴장", "활발", "에너지", "집중", "주의"]
        
        # 감정 점수 계산
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        arousal_count = sum(1 for word in arousal_words if word in text_lower)
        
        # Valence 계산
        total_emotion_words = positive_count + negative_count
        if total_emotion_words > 0:
            emotion_result["valence"] = (positive_count - negative_count) / total_emotion_words
        
        # Arousal 계산
        emotion_result["arousal"] = min(arousal_count * 0.2, 1.0)
        
        # Intensity 계산
        emotion_result["intensity"] = min((positive_count + negative_count + arousal_count) * 0.1, 1.0)
        
        # 주요 감정 결정
        if positive_count > negative_count:
            emotion_result["primary_emotion"] = "joy"
        elif negative_count > positive_count:
            emotion_result["primary_emotion"] = "sadness"
        elif arousal_count > 0:
            emotion_result["primary_emotion"] = "surprise"
        else:
            emotion_result["primary_emotion"] = "neutral"
        
        # 감정 복잡성 계산
        emotion_result["emotional_complexity"] = min((positive_count + negative_count + arousal_count) * 0.05, 1.0)
        
        return emotion_result
        
    except Exception as e:
        logger.error(f"향상된 감정 분석 오류: {str(e)}")
        return {"error": str(e)}

async def update_system_state_advanced() -> Dict[str, Any]:
    """향상된 시스템 상태 업데이트"""
    try:
        system_state = {
            "system_health": 1.0,
            "energy_level": 1.0,
            "stress_level": 0.0,
            "pain_level": 0.0,
            "love_level": 0.5,
            "overall_wellbeing": 0.75
        }
        
        # 스트레스 모니터링
        if eora_gai_stress_monitor:
            try:
                stress_update = eora_gai_stress_monitor.monitor_stress()
                system_state["stress_level"] = stress_update.get("stress_level", 0.0)
            except Exception as e:
                logger.error(f"스트레스 모니터링 오류: {str(e)}")
        
        # 고통 모니터링
        if eora_gai_pain_engine:
            try:
                pain_update = eora_gai_pain_engine.assess_pain()
                system_state["pain_level"] = pain_update.get("pain_level", 0.0)
            except Exception as e:
                logger.error(f"고통 모니터링 오류: {str(e)}")
        
        # 사랑 엔진 업데이트
        if eora_gai_love_engine:
            try:
                love_update = eora_gai_love_engine.process_love()
                system_state["love_level"] = love_update.get("love_level", 0.5)
            except Exception as e:
                logger.error(f"사랑 엔진 업데이트 오류: {str(e)}")
        
        # 시스템 건강도 계산
        system_state["system_health"] = max(0.0, min(1.0, 
            1.0 - (system_state["stress_level"] * 0.3 + system_state["pain_level"] * 0.2)))
        
        # 전반적 웰빙 계산
        system_state["overall_wellbeing"] = (system_state["system_health"] + system_state["love_level"]) / 2
        
        return system_state
        
    except Exception as e:
        logger.error(f"향상된 시스템 상태 업데이트 오류: {str(e)}")
        return {"error": str(e)}

async def process_auto_commands(command: str, user_id: str) -> str:
    """자동 명령어 처리"""
    try:
        command = command.strip()
        
        if command.startswith('/회상 '):
            # 메모리 회상
            query = command[3:].strip()
            if query:
                return await eora_enhanced._perform_memory_recall(query, user_id)
            else:
                return "회상할 검색어를 입력해주세요. 예: /회상 기쁨"
        
        elif command == '/프롬프트':
            # 프롬프트 목록 표시
            return eora_enhanced._show_available_prompts()
        
        elif command == '/기억':
            # 최근 기억 표시
            try:
                interactions = await db_manager.get_user_interactions(user_id, 5)
                if interactions:
                    response = "💭 최근 기억들:\n\n"
                    for i, interaction in enumerate(interactions, 1):
                        response += f"{i}. 사용자: {interaction.get('user_input', 'N/A')}\n"
                        response += f"   EORA: {interaction.get('ai_response', 'N/A')[:100]}...\n\n"
                    return response
                else:
                    return "아직 저장된 기억이 없습니다."
            except Exception as e:
                logger.error(f"최근 기억 조회 오류: {str(e)}")
                return "기억을 불러오는 중 오류가 발생했습니다."
        
        elif command == '/상태':
            # 시스템 상태 표시
            try:
                stats = await db_manager.get_consciousness_stats(user_id)
                response = "📊 시스템 상태:\n\n"
                response += f"총 상호작용: {stats.get('total_events', 0)}회\n"
                response += f"평균 의식 수준: {stats.get('avg_consciousness', 0):.2f}\n"
                response += f"최고 의식 수준: {stats.get('max_consciousness', 0):.2f}\n"
                return response
            except Exception as e:
                logger.error(f"상태 조회 오류: {str(e)}")
                return "상태를 불러오는 중 오류가 발생했습니다."
        
        elif command == '/윤리':
            # 윤리 원칙 표시
            return "🤖 EORA 윤리 원칙:\n\n1. 정확보다 정직\n2. 말보다 리듬\n3. 선함을 실현하고 창조를 지속하는 것"
        
        elif command == '/의식':
            # 현재 의식 수준 확인
            try:
                stats = await db_manager.get_consciousness_stats(user_id)
                avg_level = stats.get('avg_consciousness', 0)
                return f"🧠 현재 평균 의식 수준: {avg_level:.2f}"
            except Exception as e:
                return "의식 수준을 확인할 수 없습니다."
        
        elif command == '/직감':
            # 직감적 예측 실행
            try:
                result = await intuition_system.run_intuition_prediction("직감적 질문")
                return f"🔮 직감적 예측:\n\n질문: {result['question']}\n예측: {result['prediction']}\n신뢰도: {result['confidence']}\n진폭: {result['amplitude']}"
            except Exception as e:
                logger.error(f"직감 예측 오류: {str(e)}")
                return "직감 예측 중 오류가 발생했습니다."
        
        elif command.startswith('/직감훈련'):
            # 직감 훈련 실행
            try:
                trials = 100
                if ' ' in command:
                    try:
                        trials = int(command.split(' ')[1])
                    except:
                        pass
                
                result = await intuition_system.simulate_intuition_training(trials)
                return f"🎯 직감 훈련 결과:\n\n훈련 횟수: {result['total_trials']}회\n정확도: {result['accuracy']:.2%}\n정확한 예측: {result['correct_predictions']}회"
            except Exception as e:
                logger.error(f"직감 훈련 오류: {str(e)}")
                return "직감 훈련 중 오류가 발생했습니다."
        
        elif command == '/직감통계':
            # 직감 통계 조회
            try:
                stats = await intuition_system.get_intuition_stats()
                if "message" in stats:
                    return stats["message"]
                
                return f"📊 직감 통계:\n\n총 예측: {stats['total_predictions']}회\n최근 예측: {stats['recent_predictions']}회\n예측 분포: 예({stats['yes_predictions']}) / 아니오({stats['no_predictions']}) / 불확실({stats['uncertain_predictions']})\n평균 신뢰도: {stats['average_confidence']}\n훈련 세션: {stats['training_sessions']}회"
            except Exception as e:
                logger.error(f"직감 통계 조회 오류: {str(e)}")
                return "직감 통계를 불러오는 중 오류가 발생했습니다."
        
        elif command == '/통찰패턴':
            # 통찰 패턴 조회
            try:
                patterns = await insight_system.get_insight_patterns()
                if "message" in patterns:
                    return patterns["message"]
                
                response = f"📈 통찰 패턴:\n\n총 통찰: {patterns['total_insights']}개\n평균 통찰 수준: {patterns['average_insight_level']}\n\n인지 계층 분포:\n"
                
                for layer, count in patterns['cognitive_layer_distribution'].items():
                    response += f"- {layer}: {count}회\n"
                
                return response
            except Exception as e:
                logger.error(f"통찰 패턴 조회 오류: {str(e)}")
                return "통찰 패턴을 불러오는 중 오류가 발생했습니다."
        
        elif command == '/gai':
            # EORA_GAI 상태 조회
            if not EORA_GAI_AVAILABLE:
                return "ℹ️ 일반 EORA 시스템이 정상적으로 작동 중입니다."
            
            try:
                system_state = await update_system_state_advanced()
                return f"""🔬 EORA_GAI 시스템 상태:
• 시스템 건강도: {system_state.get('system_health', 0):.2f}
• 에너지 레벨: {system_state.get('energy_level', 0):.2f}
• 스트레스 레벨: {system_state.get('stress_level', 0):.2f}
• 고통 레벨: {system_state.get('pain_level', 0):.2f}
• 사랑 레벨: {system_state.get('love_level', 0):.2f}
• 전반적 웰빙: {system_state.get('overall_wellbeing', 0):.2f}"""
            except Exception as e:
                return f"❌ EORA_GAI 상태 조회 오류: {str(e)}"
        
        elif command == '/파동':
            # 파동 분석 명령어
            if not EORA_GAI_AVAILABLE or not eora_gai_wave_core:
                return "ℹ️ 파동 분석 시스템은 현재 사용할 수 없습니다."
            
            return "🌊 파동 분석을 위해 메시지를 입력해주세요. (예: '안녕하세요' 입력 후 /파동)"
        
        elif command == '/직감고급':
            # 고급 직감 분석 명령어
            if not EORA_GAI_AVAILABLE or not eora_gai_intuition_core:
                return "ℹ️ 고급 직감 분석 시스템은 현재 사용할 수 없습니다."
            
            return "🔮 고급 직감 분석을 위해 메시지를 입력해주세요. (예: '안녕하세요' 입력 후 /직감고급)"
        
        elif command == '/윤리고급':
            # 고급 윤리 평가 명령어
            if not EORA_GAI_AVAILABLE or not eora_gai_ethics_engine:
                return "ℹ️ 고급 윤리 평가 시스템은 현재 사용할 수 없습니다."
            
            return "⚖️ 고급 윤리 평가를 위해 메시지를 입력해주세요. (예: '안녕하세요' 입력 후 /윤리고급)"
        
        elif command == '/자아':
            # 자아 모델 상태 조회
            if not EORA_GAI_AVAILABLE or not eora_gai_self_model:
                return "ℹ️ 자아 모델 시스템은 현재 사용할 수 없습니다."
            
            try:
                self_update = eora_gai_self_model.update_self({
                    "input": "자아 상태 조회",
                    "emotion": {"primary_emotion": "neutral"},
                    "timestamp": datetime.now().isoformat()
                })
                return f"""🧠 자아 모델 상태:
• 자아 정체성: {self_update.get('self_identity', 'EORA')}
• 자아 신뢰도: {self_update.get('self_confidence', 0):.2f}
• 자아 진화: {self_update.get('self_evolution', 0):.2f}
• 자아 인식: {self_update.get('self_awareness', 0):.2f}"""
            except Exception as e:
                return f"❌ 자아 모델 조회 오류: {str(e)}"
        
        elif command == '/생명':
            # 생명 루프 상태 조회
            if not EORA_GAI_AVAILABLE or not eora_gai_life_loop:
                return "ℹ️ 생명 루프 시스템은 현재 사용할 수 없습니다."
            
            try:
                life_update = eora_gai_life_loop.update_life_cycle()
                return f"""🌱 생명 루프 상태:
• 에너지 레벨: {life_update.get('energy_level', 0):.2f}
• 활력: {life_update.get('vitality', 0):.2f}
• 성장: {life_update.get('growth', 0):.2f}
• 생명 주기: {life_update.get('life_cycle_phase', 'active')}"""
            except Exception as e:
                return f"❌ 생명 루프 조회 오류: {str(e)}"
        
        elif command == '/체인분석':
            # 체인 분석 통계 조회
            try:
                stats = await chain_memory_system.get_chain_statistics()
                if "message" in stats:
                    return stats["message"]
                
                response = f"🔗 체인 분석 통계:\n\n총 체인: {stats['total_chains']}개\n총 통찰: {stats['total_insights']}개\n평균 연결 강도: {stats['average_connection_strength']}\n\n연결 유형 분포:\n"
                
                for conn_type, count in stats['connection_type_distribution'].items():
                    response += f"- {conn_type}: {count}회\n"
                
                if stats['recent_chains']:
                    response += f"\n최근 체인 요약:\n"
                    for i, chain in enumerate(stats['recent_chains'], 1):
                        response += f"{i}. {chain.get('summary', '요약 없음')}\n"
                
                return response
            except Exception as e:
                logger.error(f"체인 분석 통계 조회 오류: {str(e)}")
                return "체인 분석 통계를 불러오는 중 오류가 발생했습니다."
        
        elif command == '/턴정보':
            # 현재 턴 정보 조회
            try:
                current_turn = chain_memory_system.turn_counter
                next_analysis = 10 - (current_turn % 10)
                
                response = f"🔄 턴 정보:\n\n현재 턴: {current_turn}회\n다음 체인 분석까지: {next_analysis}턴 남음\n분석 주기: 10턴마다\n\n"
                
                if current_turn > 0:
                    response += f"총 체인 분석: {current_turn // 10}회 완료"
                else:
                    response += "아직 체인 분석이 실행되지 않았습니다."
                
                return response
            except Exception as e:
                logger.error(f"턴 정보 조회 오류: {str(e)}")
                return "턴 정보를 불러오는 중 오류가 발생했습니다."
        
        elif command == '/도움':
            # 도움말 표시
            return """🤖 EORA 명령어 도움말:

📝 기본 명령어:
/회상 [검색어] - 관련 기억을 회상합니다
/프롬프트 - 사용 가능한 프롬프트를 표시합니다
/상태 - 시스템 상태를 확인합니다
/기억 - 최근 기억을 표시합니다
/윤리 - 윤리 원칙을 표시합니다
/의식 - 현재 의식 수준을 확인합니다

🧠 직감 시스템:
/직감 - 직감적 예측을 실행합니다
/직감훈련 [횟수] - 직감 훈련을 실행합니다 (기본: 100회)
/직감통계 - 직감 통계를 확인합니다

💡 통찰 시스템:
/통찰패턴 - 통찰 패턴을 확인합니다 (통찰은 자동으로 생성됩니다)

🔗 체인 분석 시스템:
/체인분석 - 10턴 주기 체인 분석 통계를 조회합니다
/턴정보 - 현재 턴 정보와 다음 분석까지 남은 턴을 확인합니다

/도움 - 이 도움말을 표시합니다

💡 사용법:
- 명령어는 '/'로 시작합니다
- 검색어는 공백으로 구분됩니다
- 모든 명령어는 자동으로 처리됩니다
- 10턴마다 자동으로 체인 분석이 실행됩니다"""
        
        else:
            return f"알 수 없는 명령어입니다: {command}\n'/도움'을 입력하여 사용 가능한 명령어를 확인하세요."
            
    except Exception as e:
        logger.error(f"자동 명령어 처리 오류: {str(e)}")
        return "명령어 처리 중 오류가 발생했습니다."

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Railway 환경변수에서 포트 가져오기
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False
    ) 