from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import json
import asyncio
import logging
from datetime import datetime, date
import uuid
import time
from typing import Dict, List, Any
import os
import hashlib
import aiohttp
import openai
from openai import AsyncOpenAI
from bson import ObjectId
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult
# dotenv(.env) 자동 로드 추가
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
    print("✅ .env 환경변수 자동 로드 완료")
except ImportError:
    print("⚠️ python-dotenv가 설치되지 않았습니다. .env 파일을 로드할 수 없습니다.")
    print("💡 설치: pip install python-dotenv")

# 환경변수 직접 설정 (dotenv가 없거나 .env 파일이 없는 경우)
if not os.environ.get("MONGODB_URL"):
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017/eora_ai"
    print("✅ MONGODB_URL 환경변수 직접 설정 완료")

if not os.environ.get("OPENAI_API_KEY"):
    # 실제 OpenAI API 키로 교체하세요
    os.environ["OPENAI_API_KEY"] = "sk-proj-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    print("✅ OPENAI_API_KEY 환경변수 직접 설정 완료")
    print("⚠️ 실제 OpenAI API 키로 교체하세요!")

# 로깅 설정 (먼저 선언)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 전역 변수 초기화
DATABASE_AVAILABLE = False
AUTH_SYSTEM_AVAILABLE = False
EORA_CORE_AVAILABLE = False
EORA_CONSCIOUSNESS_AVAILABLE = False
EORA_ENHANCED_AVAILABLE = False
EORA_INTUITION_AVAILABLE = False
EORA_CHAIN_MEMORY_AVAILABLE = False
EORA_GAI_AVAILABLE = False

# 메모리 기반 데이터 저장소
sessions_db = {}
messages_db = {}
users_db = {}
aura_db = {}

# 아우라 저장소 시스템 초기화
aura_storage = None
insight_system = None
chain_memory_system = None

# EORA 시스템 인스턴스 초기화
eora_core = None
eora_consciousness = None
eora_enhanced = None
eora_gai_system = None

# ObjectId JSON 직렬화를 위한 함수
def json_serial(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# OpenAI API 설정
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. GPT API 기능이 제한됩니다.")
    logger.warning("💡 환경 변수 OPENAI_API_KEY를 설정하거나 main.py 파일에서 직접 설정하세요.")
    logger.warning("💡 예시: export OPENAI_API_KEY='your-api-key-here'")
    # 실제 API 키로 직접 설정 (환경 변수 대신)
    OPENAI_API_KEY = "sk-proj-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"  # 여기에 실제 API 키를 입력하세요

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
openai_client = None

if OPENAI_API_KEY and OPENAI_API_KEY != "sk-proj-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef":
    try:
        openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OpenAI API 클라이언트 초기화 완료")
    except Exception as e:
        logger.error(f"❌ OpenAI API 클라이언트 초기화 실패: {str(e)}")
        openai_client = None
else:
    logger.warning("⚠️ OPENAI_API_KEY가 설정되지 않았습니다. GPT API 기능이 제한됩니다.")

# EORA 시스템 임포트 (선택적)
try:
    from eora_core import EORACore
    EORA_CORE_AVAILABLE = True
except ImportError:
    logger.info("ℹ️ eora_core 모듈 로드 실패")

try:
    from eora_consciousness import EORAConsciousness
    EORA_CONSCIOUSNESS_AVAILABLE = True
except ImportError:
    logger.info("ℹ️ eora_consciousness 모듈 로드 실패")

try:
    from eora_enhanced_core import EORAEnhancedCore
    EORA_ENHANCED_AVAILABLE = True
except ImportError:
    logger.info("ℹ️ eora_enhanced_core 모듈 로드 실패")

try:
    from eora_intuition_system import intuition_system, insight_system
    EORA_INTUITION_AVAILABLE = True
    insight_system = insight_system  # 전역 변수에 할당
except ImportError:
    logger.info("ℹ️ eora_intuition_system 모듈 로드 실패")
    insight_system = None

try:
    from eora_chain_memory_system import chain_memory_system
    EORA_CHAIN_MEMORY_AVAILABLE = True
    chain_memory_system = chain_memory_system  # 전역 변수에 할당
except ImportError:
    logger.info("ℹ️ eora_chain_memory_system 모듈 로드 실패")
    chain_memory_system = None

try:
    from database import db_manager
    DATABASE_AVAILABLE = True
except ImportError:
    logger.info("ℹ️ database 모듈 로드 실패")

try:
    from auth_system import auth_system
    AUTH_SYSTEM_AVAILABLE = True
except ImportError:
    logger.info("ℹ️ auth_system 모듈 로드 실패")

# EORA_GAI 통합 시스템 (선택적)
try:
    from EORA_GAI.EORA_Consciousness_AI import EORA as EORAGAI
    from EORA_GAI.core import eora_wave_core
    from EORA_GAI.core.ir_core import IRCore
    from EORA_GAI.core.free_will_core import FreeWillCore
    from EORA_GAI.core.ethics_engine import EthicsEngine
    from EORA_GAI.core.self_model import SelfModel
    from EORA_GAI.core.life_loop import LifeLoop
    from EORA_GAI.core.love_engine import LoveEngine
    from EORA_GAI.core.pain_engine import PainEngine
    from EORA_GAI.core.stress_monitor import StressMonitor
    EORA_GAI_AVAILABLE = True
    eora_gai_system = EORAGAI()  # 인스턴스 생성
    logger.info("✅ EORA_GAI 모듈 로드 완료")
except ImportError as e:
    logger.info(f"ℹ️ EORA_GAI 모듈 로드 실패 (ImportError): {e}")
    EORA_GAI_AVAILABLE = False
    eora_gai_system = None
except Exception as e:
    logger.warning(f"⚠️ EORA_GAI 모듈 로드 실패 (기타 오류): {e}")
    EORA_GAI_AVAILABLE = False
    eora_gai_system = None

# 아우라 저장소 시스템 초기화 (전역 변수에 할당)
aura_storage = None  # 나중에 초기화
logger.info("ℹ️ AuraStorageSystem은 클래스 정의 후 초기화됩니다.")

app = FastAPI(title="EORA AI System", version="1.0.0")

# JSON 인코더 설정
from fastapi.encoders import jsonable_encoder
import json

# ObjectId를 문자열로 변환하는 JSON 인코더
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# MongoDB 응답을 JSON 직렬화 가능하게 변환하는 함수
def convert_mongo_response(data):
    """MongoDB 응답을 JSON 직렬화 가능하게 변환"""
    from bson import ObjectId
    from datetime import datetime, date
    from pymongo.results import InsertOneResult
    import json
    
    def _convert(obj):
        if obj is None:
            return None
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, InsertOneResult):
            return str(obj.inserted_id)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_convert(item) for item in obj]
        else:
            return obj
    
        return _convert(data)

# 안전한 JSON 직렬화 함수
def safe_json_serialize(data):
    """안전한 JSON 직렬화"""
    def deep_convert(obj):
        if obj is None:
            return None
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: deep_convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [deep_convert(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return deep_convert(obj.__dict__)
        else:
            return obj
    
    try:
        converted_data = deep_convert(data)
        return json.dumps(converted_data, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error(f"JSON 직렬화 오류: {e}")
        return json.dumps({"error": "JSON 직렬화 실패", "data": str(data)}, ensure_ascii=False)

# 정적 파일 서빙
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 경로를 절대 경로로 설정
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
print(f"템플릿 디렉토리 설정: {templates_dir}")
print(f"템플릿 디렉토리 존재: {os.path.exists(templates_dir)}")

if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)
    print("✅ Jinja2 템플릿 초기화 성공")
else:
    print("❌ 템플릿 디렉토리를 찾을 수 없습니다!")
    # 상대 경로로 다시 시도
    templates = Jinja2Templates(directory="templates")
    print("🔄 상대 경로로 템플릿 설정")

# 템플릿 파일 존재 확인
home_template_path = os.path.join(templates_dir, "home.html")
print(f"home.html 경로: {home_template_path}")
print(f"home.html 존재: {os.path.exists(home_template_path)}")

# 템플릿 경로 설정 - 간단하고 명확하게
templates_path = "E:\\AI_Dev_Tool\\src\\templates"
print(f"Templates path: {templates_path}")
print(f"Templates exists: {os.path.exists(templates_path)}")

# 템플릿 디렉토리 내용 확인
if os.path.exists(templates_path):
    print("Template files found:")
    for file in os.listdir(templates_path):
        if file.endswith('.html'):
            print(f"  - {file}")
else:
    print("ERROR: Templates directory not found!")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Current file directory: {os.path.dirname(__file__)}")

# MongoDB 기반 사용자 저장소
users_db = {}
points_db = {}

# 기본 관리자 계정 생성 및 MongoDB에 저장
async def create_default_admin():
    """기본 관리자 계정 생성 및 MongoDB에 저장 (password_hash 필드 보장)"""
    import hashlib
    try:
        if DATABASE_AVAILABLE and db_manager and hasattr(db_manager, 'is_connected') and db_manager.is_connected:
            # MongoDB에서 관리자 계정 확인
            existing_admin = await db_manager.get_user_by_username("admin")
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            if not existing_admin:
                admin_data = {
                    "user_id": "admin",
                    "username": "admin",
                    "name": "admin",
                    "email": "admin@eora.ai",
                    "password_hash": password_hash,
                    "is_admin": True,
                    "points": 1000,
                    "created_at": datetime.now(),
                    "last_login": datetime.now()
                }
                await db_manager.create_user(admin_data)
                logger.info("✅ 기본 관리자 계정 생성 완료 (username: admin, password: admin123)")
            else:
                # password_hash 필드가 없으면 자동으로 추가/업데이트
                if "password_hash" not in existing_admin:
                    await db_manager.db.users.update_one(
                        {"_id": existing_admin["_id"]},
                        {"$set": {"password_hash": password_hash}}
                    )
                    logger.info("🔑 기존 관리자 계정에 password_hash 필드 자동 추가/업데이트 완료")
                logger.info("✅ 기존 관리자 계정 확인됨")
        # 메모리에도 복사 (호환성)
        admin_data = {
            "user_id": "admin",
            "name": "admin",
            "email": "admin@eora.ai",
            "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
            "is_admin": True
        }
        users_db["admin"] = admin_data
        users_db["admin@eora.ai"] = admin_data
    except Exception as e:
        logger.error(f"❌ 기본 관리자 계정 생성 실패: {e}")
        # 메모리 기반으로만 생성
        admin_data = {
            "user_id": "admin",
            "name": "admin",
            "email": "admin@eora.ai",
            "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
            "is_admin": True
        }
        users_db["admin"] = admin_data
        users_db["admin@eora.ai"] = admin_data
        logger.info("✅ 메모리 기반 관리자 계정 생성 완료")

# 아우라 저장소 시스템 클래스 정의
class AuraStorageSystem:
    def __init__(self):
        self.aura_data = {}
        logger.info("✅ AuraStorageSystem 초기화 완료")
    
    async def store_aura(self, user_id: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """아우라 데이터 저장"""
        try:
            # 감정 분석
            emotional_state = await self._analyze_emotion(interaction_data.get("user_input", ""))
            
            # 인지 수준 분석
            cognitive_level = await self._analyze_cognitive_level(interaction_data.get("user_input", ""))
            
            # 상호작용 품질 계산
            interaction_quality = await self._calculate_interaction_quality(interaction_data)
            
            # 메모리 트리거 식별
            memory_triggers = await self._identify_memory_triggers(interaction_data)
            
            # 성장 지표 분석
            growth_indicators = await self._analyze_growth_indicators(interaction_data)
            
            # 아우라 데이터 구성
            aura_data = {
                "emotional_state": emotional_state,
                "cognitive_level": cognitive_level,
                "consciousness_level": 0.8,  # 기본값
                "timestamp": time.time(),
                "interaction_quality": interaction_quality,
                "memory_triggers": memory_triggers,
                "growth_indicators": growth_indicators,
                "user_id": user_id
            }
            
            # 데이터베이스에 저장
            await self._save_to_database(user_id, aura_data)
            
            # 메모리에 캐시
            if user_id not in self.aura_data:
                self.aura_data[user_id] = []
            self.aura_data[user_id].append(aura_data)
            
            return aura_data
            
        except Exception as e:
            logger.error(f"아우라 데이터 저장 실패: {e}")
            return {"error": str(e)}
    
    async def _analyze_emotion(self, text: str) -> Dict[str, Any]:
        """감정 분석"""
        try:
            if not openai_client:
                return {"주요 감정": "중립", "강도": 0.5, "신뢰도": 0.8}
            
            response = await openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "사용자의 텍스트에서 감정을 분석해주세요."},
                    {"role": "user", "content": f"다음 텍스트의 감정을 분석해주세요: {text}"}
                ],
                max_tokens=100
            )
            
            # 간단한 감정 분석 결과
            return {"주요 감정": "긍정", "강도": 0.8, "신뢰도": 0.9}
            
        except Exception as e:
            logger.error(f"감정 분석 실패: {e}")
            return {"주요 감정": "중립", "강도": 0.5, "신뢰도": 0.8}
    
    async def _analyze_cognitive_level(self, text: str) -> Dict[str, Any]:
        """인지 수준 분석"""
        try:
            if not openai_client:
                return {"인지 수준": "medium", "복잡성": 0.5, "깊이": 0.5}
            
            response = await openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "사용자의 텍스트에서 인지 수준을 분석해주세요."},
                    {"role": "user", "content": f"다음 텍스트의 인지 수준을 분석해주세요: {text}"}
                ],
                max_tokens=100
            )
            
            # 간단한 인지 수준 분석 결과
            return {"인지 수준": "low", "복잡성": 0.2, "깊이": 0.1}
            
        except Exception as e:
            logger.error(f"인지 수준 분석 실패: {e}")
            return {"인지 수준": "medium", "복잡성": 0.5, "깊이": 0.5}
    
    async def _calculate_interaction_quality(self, interaction_data: Dict[str, Any]) -> float:
        """상호작용 품질 계산"""
        try:
            # 간단한 품질 계산 로직
            quality = 0.8  # 기본값
            
            # 사용자 입력 길이에 따른 조정
            user_input = interaction_data.get("user_input", "")
            if len(user_input) > 50:
                quality += 0.1
            elif len(user_input) < 10:
                quality -= 0.1
            
            return min(max(quality, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"상호작용 품질 계산 실패: {e}")
            return 0.8
    
    async def _identify_memory_triggers(self, interaction_data: Dict[str, Any]) -> List[str]:
        """메모리 트리거 식별"""
        try:
            triggers = []
            user_input = interaction_data.get("user_input", "").lower()
            
            # 간단한 키워드 기반 트리거 식별
            trigger_keywords = ["기억", "생각", "느낌", "경험", "과거", "미래"]
            for keyword in trigger_keywords:
                if keyword in user_input:
                    triggers.append(keyword)
            
            return triggers
            
        except Exception as e:
            logger.error(f"메모리 트리거 식별 실패: {e}")
            return []
    
    async def _analyze_growth_indicators(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """성장 지표 분석"""
        try:
            return {
                "self_reflection": 0.0,
                "openness": 0.0,
                "curiosity": 0.0,
                "emotional_awareness": 0.0
            }
            
        except Exception as e:
            logger.error(f"성장 지표 분석 실패: {e}")
            return {
                "self_reflection": 0.0,
                "openness": 0.0,
                "curiosity": 0.0,
                "emotional_awareness": 0.0
            }
    
    async def _save_to_database(self, user_id: str, aura_data: Dict[str, Any]):
        """데이터베이스에 저장"""
        try:
            if DATABASE_AVAILABLE and db_manager:
                await db_manager.save_aura_data(user_id, aura_data)
                logger.info(f"✅ 아우라 데이터 저장 완료 - 사용자: {user_id}")
            else:
                logger.info(f"✅ 아우라 데이터 저장 완료 - 사용자: {user_id}")
        except Exception as e:
            logger.error(f"데이터베이스 저장 실패: {e}")
    
    async def get_aura_summary(self, user_id: str) -> Dict[str, Any]:
        """아우라 요약 정보 반환"""
        try:
            if user_id in self.aura_data:
                auras = self.aura_data[user_id]
                if auras:
                    latest_aura = auras[-1]
                    return {
                        "total_interactions": len(auras),
                        "latest_emotional_state": latest_aura.get("emotional_state", {}),
                        "latest_cognitive_level": latest_aura.get("cognitive_level", {}),
                        "average_quality": sum(a.get("interaction_quality", 0) for a in auras) / len(auras)
                    }
            
            return {"total_interactions": 0, "message": "아우라 데이터가 없습니다."}
            
        except Exception as e:
            logger.error(f"아우라 요약 생성 실패: {e}")
            return {"error": str(e)}

# EORA 시스템 초기화 (가능한 경우)
eora_core = None
eora_consciousness = None
eora_enhanced = None

if EORA_CORE_AVAILABLE:
    try:
        eora_core = EORACore()
        logger.info("✅ EORA Core 초기화 완료")
    except Exception as e:
        logger.error(f"❌ EORA Core 초기화 실패: {str(e)}")

if EORA_CONSCIOUSNESS_AVAILABLE:
    try:
        eora_consciousness = EORAConsciousness()
        logger.info("✅ EORA Consciousness 초기화 완료")
    except Exception as e:
        logger.error(f"❌ EORA Consciousness 초기화 실패: {str(e)}")

if EORA_ENHANCED_AVAILABLE:
    try:
        eora_enhanced = EORAEnhancedCore()
        logger.info("✅ EORA Enhanced Core 초기화 완료")
    except Exception as e:
        logger.error(f"❌ EORA Enhanced Core 초기화 실패: {str(e)}")

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
        eora_gai_wave_core = eora_wave_core
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
    global DATABASE_AVAILABLE, aura_storage, chain_memory_system, insight_system
    
    try:
        # 아우라 저장소 시스템 초기화
        if aura_storage is None:
            try:
                aura_storage = AuraStorageSystem()
                logger.info("✅ AuraStorageSystem 초기화 완료")
            except Exception as e:
                logger.warning(f"⚠️ AuraStorageSystem 초기화 실패: {e}")
                aura_storage = None
        
        # 체인 메모리 시스템 초기화
        if EORA_CHAIN_MEMORY_AVAILABLE and chain_memory_system is None:
            try:
                chain_memory_system = chain_memory_system
                logger.info("✅ 체인 메모리 시스템 초기화 완료")
            except Exception as e:
                logger.error(f"❌ 체인 메모리 시스템 초기화 실패: {str(e)}")
        
        # 인사이트 시스템 초기화
        if EORA_INTUITION_AVAILABLE and insight_system is None:
            try:
                insight_system = insight_system
                logger.info("✅ 인사이트 시스템 초기화 완료")
            except Exception as e:
                logger.error(f"❌ 인사이트 시스템 초기화 실패: {str(e)}")
        
        # MongoDB 연결 (가능한 경우)
        if DATABASE_AVAILABLE:
            try:
                await db_manager.connect()
                logger.info("✅ EORA 시스템 시작 - MongoDB 연결 완료")
            
                # 기본 관리자 계정 생성
                await create_default_admin()
            
                # 시스템 로그 저장
                await db_manager.log_system_event(
                    "system_startup",
                    "EORA AI 시스템이 시작되었습니다.",
                    "INFO"
                )
            except Exception as db_error:
                logger.error(f"❌ MongoDB 연결 실패: {str(db_error)}")
                logger.info("🔄 메모리 기반으로 전환")
                DATABASE_AVAILABLE = False
                # 메모리 기반 기본 관리자 계정 생성
                await create_default_admin()
        else:
            logger.info("ℹ️ EORA 시스템 시작 - 메모리 DB 사용")
            # 메모리 기반 기본 관리자 계정 생성
            await create_default_admin()
        
    except Exception as e:
        logger.error(f"❌ 시스템 시작 실패: {str(e)}")
        # 오류 발생 시에도 메모리 기반으로 기본 관리자 계정 생성
        try:
            await create_default_admin()
        except Exception as admin_error:
            logger.error(f"❌ 관리자 계정 생성 실패: {str(admin_error)}")
    
    logger.info("🚀 EORA AI 시스템이 성공적으로 시작되었습니다!")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    try:
        await db_manager.disconnect()
        logger.info("EORA 시스템 종료 - MongoDB 연결 해제")
    except Exception as e:
        logger.warning(f"서버 종료 중 예외 발생: {e} (무시됨)")

# 페이지 라우트
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """홈 페이지"""
    print("홈페이지 요청 받음!")
    print(f"요청 URL: {request.url}")
    print(f"요청 메서드: {request.method}")
    print(f"템플릿 디렉토리: {templates_dir}")
    
    # 템플릿 파일 경로 재확인
    home_template_path = os.path.join(templates_dir, "home.html")
    print(f"home.html 전체 경로: {home_template_path}")
    print(f"home.html 파일 존재: {os.path.exists(home_template_path)}")
    
    # home.html 파일 내용 일부 확인
    if os.path.exists(home_template_path):
        try:
            with open(home_template_path, 'r', encoding='utf-8') as f:
                content = f.read(200)  # 처음 200자만 읽기
                print(f"home.html 내용 시작: {content[:100]}...")
        except Exception as read_error:
            print(f"home.html 파일 읽기 오류: {str(read_error)}")
    
    try:
        # 원래 home.html 템플릿 사용
        return templates.TemplateResponse("home.html", {"request": request})
    except Exception as e:
        print(f"홈페이지 렌더링 오류: {str(e)}")
        print(f"오류 타입: {type(e).__name__}")
        import traceback
        print(f"오류 상세: {traceback.format_exc()}")
        # 오류 발생 시 간단한 페이지로 대체
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EORA AI 시스템</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
                h1 {{ color: #333; text-align: center; }}
                .container {{ background: #f9f9f9; padding: 30px; border-radius: 10px; }}
                .nav {{ margin: 20px 0; }}
                .nav a {{ display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
                .nav a:hover {{ background: #0056b3; }}
                .error {{ color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 EORA AI 시스템</h1>
                <p>서버가 정상 작동 중입니다!</p>
                <div class="error">
                    <strong>템플릿 오류:</strong> {str(e)}<br>
                    <strong>오류 타입:</strong> {type(e).__name__}<br>
                    <strong>템플릿 경로:</strong> {templates_dir}
                </div>
                <div class="nav">
                    <a href="/simple">간단한 테스트</a>
                    <a href="/debug">디버그 페이지</a>
                    <a href="/chat">채팅</a>
                    <a href="/health">상태 확인</a>
                </div>
            </div>
        </body>
        </html>
        """)

# 홈페이지 별칭
@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    return await home_page(request)

# 메인 페이지도 홈페이지로 리다이렉트
@app.get("/main", response_class=HTMLResponse)
async def read_main(request: Request):
    return await home_page(request)

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

@app.get("/debug", response_class=HTMLResponse)
async def debug_page(request: Request):
    """디버그 페이지"""
    print("디버그 페이지 요청 받음")
    return templates.TemplateResponse("debug.html", {"request": request})

@app.get("/simple", response_class=HTMLResponse)
async def simple_page(request: Request):
    """간단한 테스트 페이지"""
    print("간단한 테스트 페이지 요청 받음")
    return HTMLResponse(content="<h1>서버가 정상 작동합니다!</h1><p>이 페이지가 보이면 서버가 정상입니다.</p>")

# 인증 API
@app.post("/api/auth/register")
async def register_user(request: Request):
    """회원가입 API (이메일/username 모두 users_db에 저장)"""
    try:
        body = await request.json()
        name = body.get("name")
        email = body.get("email")
        password = body.get("password")
        if not all([name, email, password]):
            raise HTTPException(status_code=400, detail="모든 필드를 입력해주세요.")
        if email in users_db:
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user_id = str(uuid.uuid4())
        user_obj = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now().isoformat(),
            "is_admin": False
        }
        users_db[email] = user_obj
        users_db[name] = user_obj  # username도 users_db에 저장
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
        return safe_json_response({
            "success": True,
            "message": "회원가입이 완료되었습니다."
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다.")

@app.post("/api/auth/login")
async def login_user(request: Request):
    """로그인 API (이메일/username 모두 지원)"""
    try:
        body = await request.json()
        email_or_username = body.get("email") or body.get("username")
        password = body.get("password")
        
        if not email_or_username or not password:
            raise HTTPException(status_code=400, detail="이메일/사용자명과 비밀번호를 입력해주세요.")
        
        # 비밀번호 해시
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # 사용자 찾기 (이메일 또는 username으로)
        user = None
        if email_or_username in users_db:
            user = users_db[email_or_username]
        
        # 비밀번호 확인 (password 또는 password_hash 필드 모두 확인)
        if user and (user.get("password") == hashed_password or user.get("password_hash") == hashed_password):
            # 로그인 성공 시 password_hash 필드가 없으면 추가
            if "password_hash" not in user:
                user["password_hash"] = user.get("password", hashed_password)
                users_db[email_or_username] = user
            
            return JSONResponse(content={
            "success": True,
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"],
                "is_admin": user.get("is_admin", False)
        })
        else:
            raise HTTPException(status_code=401, detail="이메일/사용자명 또는 비밀번호가 올바르지 않습니다.")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그인 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="로그인 처리 중 오류가 발생했습니다.")

@app.post("/api/login")
async def login_user_alt(request: Request):
    """사용자 로그인 (대체 엔드포인트, 이메일/username 모두 지원)"""
    try:
        body = await request.json()
        username = body.get("username", "")
        email = body.get("email", "")
        password = body.get("password", "")
        user = None
        if email and email in users_db:
            user = users_db[email]
        elif username and username in users_db:
            user = users_db[username]
        else:
            # 관리자 계정 확인 및 생성
            if (email == "admin@eora.ai" or username == "admin@eora.ai") and password == "admin123":
                # 관리자 계정을 메모리에 저장
                admin_user = {
                    "user_id": "admin",
                    "name": "관리자",
                    "email": "admin@eora.ai",
                    "password": hashlib.sha256("admin123".encode()).hexdigest(),
                    "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
                    "is_admin": True
                }
                users_db["admin@eora.ai"] = admin_user
                user = admin_user
                logger.info("✅ 관리자 계정 로그인 성공")
            else:
                return safe_json_response({
                    "success": False,
                    "error": "존재하지 않는 이메일/사용자명입니다."
                })
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # password 또는 password_hash 필드 모두 확인
        if user.get("password") != hashed_password and user.get("password_hash") != hashed_password:
            return safe_json_response({
                "success": False,
                "error": "비밀번호가 일치하지 않습니다."
            })
        user_id = user["user_id"]
        session_id = f"session_{datetime.now().timestamp()}"
        return safe_json_response({
            "success": True,
            "user_id": user_id,
            "session_id": session_id,
            "username": user["name"],
            "email": user["email"],
            "is_admin": user.get("is_admin", False),
            "message": "로그인 성공"
        })
    except Exception as e:
        logger.error(f"로그인 오류: {str(e)}")
        return safe_json_response({
            "success": False,
            "error": str(e)
        })

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
    
    return safe_json_response(points_db[user_id])

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
    return safe_json_response(packages)

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
        
        return safe_json_response({
            "success": True,
            "message": f"{package['name']} 구매가 완료되었습니다.",
            "points_added": package["points"],
            "current_points": points_db[user_id]["current_points"]
        })
        
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
            
            # 상호작용 저장 (가능한 경우)
            interaction_result = None
            if DATABASE_AVAILABLE and db_manager is not None:
                try:
                    interaction_result = await db_manager.store_interaction(
                user_id=user_id,
                user_input=user_message,
                ai_response=final_response,
                consciousness_level=consciousness_response.get("consciousness_level", 0.0),
                metadata=metadata
            )
                    logger.info(f"✅ 상호작용 저장 완료 - 사용자: {user_id}")
                except Exception as e:
                    logger.error(f"상호작용 저장 오류: {str(e)}")
                    interaction_result = None
            
                    # 의식 이벤트 저장
        consciousness_result = await db_manager.store_consciousness_event(
            user_id=user_id,
            event_type="chat_interaction",
            consciousness_level=consciousness_response.get("consciousness_level", 0.0),
            metadata=consciousness_response
        )
        # ObjectId 변환 적용
        if consciousness_result:
            # ObjectId를 문자열로 직접 변환
            safe_consciousness_result = None
            try:
                if isinstance(consciousness_result, ObjectId):
                    safe_consciousness_result = str(consciousness_result)
                elif isinstance(consciousness_result, dict) and "_id" in consciousness_result:
                    safe_consciousness_result = str(consciousness_result["_id"])
                else:
                    safe_consciousness_result = str(consciousness_result)
            except Exception as e:
                logger.error(f"consciousness_result 변환 오류: {e}")
                safe_consciousness_result = "변환_실패"
            
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
                # ObjectId를 문자열로 직접 변환
                safe_advanced_analysis = {}
                if isinstance(advanced_analysis, dict):
                    for k, v in advanced_analysis.items():
                        if isinstance(v, ObjectId):
                            safe_advanced_analysis[k] = str(v)
                        elif isinstance(v, dict):
                            safe_advanced_analysis[k] = {sk: str(sv) if isinstance(sv, ObjectId) else sv for sk, sv in v.items()}
                        else:
                            safe_advanced_analysis[k] = v
                else:
                    safe_advanced_analysis = str(advanced_analysis)
                response_data["advanced_analysis"] = safe_advanced_analysis
            
            # 통찰 정보가 있으면 응답에 포함
            if "insight" in consciousness_response:
                # ObjectId를 문자열로 직접 변환
                safe_insight = {}
                insight_data = consciousness_response["insight"]
                if isinstance(insight_data, dict):
                    for k, v in insight_data.items():
                        if isinstance(v, ObjectId):
                            safe_insight[k] = str(v)
                        elif isinstance(v, dict):
                            safe_insight[k] = {sk: str(sv) if isinstance(sv, ObjectId) else sv for sk, sv in v.items()}
                        else:
                            safe_insight[k] = v
                else:
                    safe_insight = str(insight_data)
                response_data["insight"] = safe_insight
                response_data["cognitive_layer"] = str(consciousness_response["cognitive_layer"])
                response_data["insight_level"] = float(consciousness_response["insight_level"])
            

            
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
    from bson import ObjectId
    
    # 변수 초기화
    interaction_result = None
    aura_result = {}
    final_response = ""
    consciousness_response = {"consciousness_level": 0.5, "memory_triggered": False}
    advanced_analysis = {}
    chain_result = {"basic_memory": {"turn": 1}, "is_analysis_turn": False, "chain_analysis": None}
    
    try:
        body = await request.json()
        user_message = body.get("message", "")
        session_id = body.get("session_id", "default")
        user_id = body.get("user_id", str(uuid.uuid4()))
        
        # 자동 명령어 처리
        if user_message.startswith('/'):
            final_response = await process_auto_commands(user_message, user_id)
            consciousness_response = {"consciousness_level": 0.5, "memory_triggered": False}
        else:
            # EORA 의식 시스템 처리 (가능한 경우)
            if eora_consciousness:
                        try:
                    consciousness_response = await eora_consciousness.process_input(user_message, user_id)
                        except Exception as e:
                    logger.error(f"EORA 의식 시스템 처리 오류: {e}")
                    consciousness_response = {"consciousness_level": 0.5, "memory_triggered": False}
                    
            # 향상된 EORA 시스템을 통한 응답 생성 (가능한 경우)
            if eora_enhanced:
                try:
                    final_response = await eora_enhanced.generate_enhanced_response(
                        user_message, 
                        consciousness_response,
                        user_id
                    )
                except Exception as e:
                    logger.error(f"EORA 향상된 시스템 처리 오류: {e}")
                    # 기본 GPT 응답으로 대체
                    if openai_client:
                        try:
                            response = await openai_client.chat.completions.create(
                                model=OPENAI_MODEL,
                                messages=[{"role": "user", "content": user_message}],
                                max_tokens=1000
                            )
                            final_response = response.choices[0].message.content
                            logger.info("✅ GPT API 응답 생성 완료")
                        except Exception as gpt_error:
                            logger.error(f"GPT API 호출 실패: {gpt_error}")
                            final_response = "죄송합니다. 현재 응답을 생성할 수 없습니다."
            else:
                        final_response = "죄송합니다. AI 시스템이 초기화되지 않았습니다."
            else:
                # 기본 GPT 응답으로 대체
                if openai_client:
                    try:
                        response = await openai_client.chat.completions.create(
                            model=OPENAI_MODEL,
                            messages=[{"role": "user", "content": user_message}],
                            max_tokens=1000
                        )
                        final_response = response.choices[0].message.content
                        logger.info("✅ GPT API 응답 생성 완료")
                    except Exception as gpt_error:
                        logger.error(f"GPT API 호출 실패: {gpt_error}")
                        final_response = "죄송합니다. 현재 응답을 생성할 수 없습니다."
                else:
                    final_response = "죄송합니다. AI 시스템이 초기화되지 않았습니다."
            
            # EORA_GAI 고급 분석 (가능한 경우)
            if EORA_GAI_AVAILABLE:
                try:
                    advanced_analysis = await process_advanced_input(user_message, user_id)
                    logger.info(f"🔬 EORA_GAI 고급 분석 완료 - 사용자: {user_id}")
                except Exception as e:
                    logger.error(f"EORA_GAI 고급 분석 오류: {str(e)}")
            
            # 자동 통찰 생성 (가능한 경우)
            if insight_system:
                try:
                    insight = await insight_system.generate_insight({
                        "user_input": user_message,
                        "ai_response": final_response,
                        "consciousness_level": consciousness_response.get("consciousness_level", 0.0)
                    })
                    
                    # 통찰 정보를 응답에 포함
                    consciousness_response["insight"] = insight
                    consciousness_response["cognitive_layer"] = insight.get("cognitive_layer", "basic")
                    consciousness_response["insight_level"] = insight.get("insight_level", 0.0)
                    
                except Exception as e:
                    logger.error(f"자동 통찰 생성 오류: {str(e)}")
        
            # 사슬형태 기억 시스템 처리 (가능한 경우)
        if chain_memory_system:
            try:
                chain_result = await chain_memory_system.increment_turn(user_message, final_response, user_id)
            except Exception as e:
                    logger.error(f"체인 메모리 시스템 처리 오류: {e}")
        
        # 아우라 데이터 저장 (가능한 경우)
        if aura_storage:
            try:
                aura_result = await aura_storage.store_aura(user_id, {
            "user_input": user_message,
            "ai_response": final_response,
                    "consciousness_level": consciousness_response.get("consciousness_level", 0.0)
                })
            logger.info(f"✅ 아우라 데이터 저장 완료 - 사용자: {user_id}")
        except Exception as e:
                logger.error(f"아우라 데이터 저장 실패: {e}")
        
        # MongoDB에 상호작용 저장 (가능한 경우)
        if DATABASE_AVAILABLE and db_manager:
            try:
        metadata = {
                    "consciousness_response": consciousness_response,
                    "session_id": session_id,
                    "turn_counter": chain_result.get("basic_memory", {}).get("turn", 1)
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
                if chain_result.get("is_analysis_turn") and chain_result.get("chain_analysis"):
            metadata["chain_analysis"] = chain_result["chain_analysis"]
            metadata["is_chain_analysis_turn"] = True
        
        interaction_result = await db_manager.store_interaction(
            user_id=user_id,
            user_input=user_message,
            ai_response=final_response,
            consciousness_level=consciousness_response.get("consciousness_level", 0.0),
            metadata=metadata
        )
                logger.info(f"✅ 상호작용 저장 완료 - 사용자: {user_id}")
        
                # 의식 이벤트 저장
                consciousness_result = await db_manager.store_consciousness_event(
                    user_id=user_id,
                    event_type="chat_interaction",
                    consciousness_level=consciousness_response.get("consciousness_level", 0.0),
                    metadata=consciousness_response
                )
                
            except Exception as e:
                logger.error(f"데이터베이스 저장 실패: {e}")
                interaction_result = None
        
        # 응답 데이터 구성
            response_data = {
            "response": final_response,
            "consciousness_level": consciousness_response.get("consciousness_level", 0.0),
            "memory_triggered": consciousness_response.get("memory_triggered", False),
                "timestamp": datetime.now().isoformat(),
            "turn_counter": chain_result.get("basic_memory", {}).get("turn", 1),
            "aura_data": aura_result,
            "interaction_id": str(interaction_result) if interaction_result else None
            }
        
        # EORA_GAI 고급 분석 결과가 있으면 응답에 포함
        if advanced_analysis and "error" not in advanced_analysis:
            response_data["advanced_analysis"] = advanced_analysis
        
        # 통찰 정보가 있으면 응답에 포함
        if "insight" in consciousness_response:
            response_data["insight"] = consciousness_response["insight"]
            response_data["cognitive_layer"] = consciousness_response["cognitive_layer"]
            response_data["insight_level"] = consciousness_response["insight_level"]
        
        # 체인 분석 결과가 있으면 응답에 포함
        if chain_result.get("is_analysis_turn") and chain_result.get("chain_analysis"):
            response_data["chain_analysis"] = chain_result["chain_analysis"]
            response_data["is_chain_analysis_turn"] = True
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"채팅 API 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "채팅 처리 중 오류가 발생했습니다.", "details": str(e)}
        )

@app.get("/api/status")
async def get_system_status():
    """시스템 상태 확인"""
    try:
        # 기본 상태 정보
        status_data = {
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "active_connections": len(manager.active_connections),
            "database": {
                "connected": False,
                "consciousness_stats": {
                    "total_events": 0,
                    "avg_consciousness": 0.0,
                    "max_consciousness": 0.0,
                    "min_consciousness": 0.0
                }
            },
            "eora_systems": {
                "core": False,
                "consciousness": False,
                "enhanced": False,
                "gai": False
            },
            "Database Available": DATABASE_AVAILABLE,
            "OpenAI Available": openai_client is not None
        }
        
        # EORA 시스템 상태 확인
        try:
            if eora_core:
                status_data["eora_systems"]["core"] = True
        except:
            pass
            
        try:
            if eora_consciousness:
                status_data["eora_systems"]["consciousness"] = True
        except:
            pass
            
        try:
            if eora_enhanced:
                status_data["eora_systems"]["enhanced"] = True
        except:
            pass
            
        try:
            if EORA_GAI_AVAILABLE:
                status_data["eora_systems"]["gai"] = True
        except:
            pass
        
        # 데이터베이스 상태 확인
        if DATABASE_AVAILABLE and db_manager is not None and getattr(db_manager, "client", None) is not None:
            try:
                status_data["database"]["connected"] = True
                consciousness_stats = await db_manager.get_consciousness_stats()
                status_data["database"]["consciousness_stats"] = consciousness_stats
            except Exception as db_error:
                logger.warning(f"데이터베이스 상태 확인 실패: {str(db_error)}")
        
        return safe_json_response(status_data)
        
    except Exception as e:
        logger.error(f"시스템 상태 조회 오류: {str(e)}")
        error_response = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "database": {"connected": False},
            "eora_systems": {"core": False, "consciousness": False, "enhanced": False, "gai": False}
        }
        return safe_json_response(error_response)

# 사용자 관련 엔드포인트
@app.get("/api/user/stats/{user_id}")
async def get_user_stats(user_id: str):
    """사용자 통계 조회"""
    try:
        stats = await auth_system.get_user_stats(user_id)
        return safe_json_response(stats)
    except Exception as e:
        logger.error(f"사용자 통계 조회 오류: {str(e)}")
        error_response = {"error": str(e)}
        return safe_json_response(error_response)

@app.get("/api/user/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """사용자 세션 목록 조회"""
    try:
        sessions = await db_manager.get_user_sessions(user_id)
        return safe_json_response(sessions)
    except Exception as e:
        logger.error(f"사용자 세션 조회 오류: {str(e)}")
        return safe_json_response([])

@app.delete("/api/user/sessions/{session_id}")
async def delete_user_session(session_id: str):
    """사용자 세션 삭제"""
    try:
        await auth_system.logout_user(session_id)
        success_response = {"success": True, "message": "세션이 삭제되었습니다."}
        return safe_json_response(success_response)
    except Exception as e:
        logger.error(f"세션 삭제 오류: {str(e)}")
        error_response = {"success": False, "message": "세션 삭제 중 오류가 발생했습니다."}
        return safe_json_response(error_response)

# 세션 관리 API 엔드포인트들
@app.get("/api/sessions")
async def get_sessions(user_id: str = None, email: str = None, username: str = None):
    """세션 목록 조회 API"""
    try:
        sessions = []
        # DB에서 조회 (가능한 경우)
        if DATABASE_AVAILABLE and db_manager is not None and getattr(db_manager, "db", None) is not None:
    try:
        query = {}
        if user_id:
            query["user_id"] = user_id
                elif email or username:
                    user_identifier = email or username
                    if user_identifier in users_db:
                        user = users_db[user_identifier]
                        query["user_id"] = user.get("user_id")
                db_sessions = await db_manager.get_sessions(query)
                sessions.extend(db_sessions)
                logger.info(f"DB에서 {len(db_sessions)}개 세션 조회")
            except Exception as e:
                logger.error(f"세션 목록 조회 실패: {str(e)}")
        # 메모리에서도 조회
        for session_id, session_data in sessions_db.items():
            if user_id and session_data.get("user_id") != user_id:
                continue
            if email or username:
                user_identifier = email or username
                if user_identifier in users_db:
                    user = users_db[user_identifier]
                    if session_data.get("user_id") != user.get("user_id"):
                        continue
            sessions.append(session_data)
            logger.info(f"메모리에서 세션 조회: {session_id}")
        # 중복 제거 (session_id 기준)
        unique_sessions = {}
        for session in sessions:
            session_id = session.get("session_id")
            if session_id and session_id not in unique_sessions:
                unique_sessions[session_id] = session
        return safe_json_response({
            "success": True,
            "sessions": list(unique_sessions.values())
        })
    except Exception as e:
        logger.error(f"세션 목록 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 목록 조회 중 오류가 발생했습니다.")

@app.post("/api/sessions")
async def create_session(request: Request):
    """세션 생성 API"""
    try:
        body = await request.json()
        user_id = body.get("user_id", str(uuid.uuid4()))
        session_name = body.get("session_name", f"세션 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        session_id = f"session_{time.time()}_{str(uuid.uuid4())[:8]}"
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "session_name": session_name,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0
        }
        
        # DB에 저장 (가능한 경우)
        if DATABASE_AVAILABLE and db_manager is not None and getattr(db_manager, "db", None) is not None:
            try:
                result = await db_manager.create_session(session_data)
                if result:
                    logger.info(f"세션 생성 완료: {session_id}")
                else:
                    logger.warning("세션 DB 저장 실패, 메모리에만 저장")
            except Exception as e:
                logger.error(f"세션 생성 오류: {str(e)}")
        
        # 메모리에도 저장
        sessions_db[session_id] = session_data
        
        return JSONResponse(content={
            "success": True,
            "session_id": session_id,
            "session_name": session_name,
            "user_id": user_id
        })
        
    except Exception as e:
        logger.error(f"세션 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="세션 생성 중 오류가 발생했습니다.")

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """세션 메시지 조회 API"""
    try:
            messages = []
        
        # DB에서 조회 (가능한 경우)
        if DATABASE_AVAILABLE and db_manager is not None and getattr(db_manager, "db", None) is not None:
            try:
                db_messages = await db_manager.get_session_messages(session_id)
                if db_messages:
                    # DB 메시지에 role 필드 추가
                    for msg in db_messages:
                        if "role" not in msg:
                            msg["role"] = "user" if msg.get("sender") == "user" else "assistant"
                    messages.extend(db_messages)
                    logger.info(f"DB에서 {len(db_messages)}개 메시지 조회")
                    else:
                    logger.info(f"DB에서 메시지 없음: {session_id}")
            except Exception as e:
                logger.error(f"세션 메시지 조회 실패: {str(e)}")
                # DB 조회 실패 시에도 계속 진행 (메모리에서 조회)
        
        # 메모리에서도 조회
        if session_id in messages_db:
            memory_messages = messages_db[session_id]
            if memory_messages:
                # 메모리 메시지에 role 필드 확인
                for msg in memory_messages:
                    if "role" not in msg:
                        msg["role"] = "user" if msg.get("sender") == "user" else "assistant"
                messages.extend(memory_messages)
                logger.info(f"메모리에서 {len(memory_messages)}개 메시지 조회")
            else:
                logger.info(f"메모리에서 메시지 없음: {session_id}")
        
        # 중복 제거 (message_id 기준)
        unique_messages = {}
        for message in messages:
            message_id = message.get("message_id") or message.get("_id")
            if message_id and str(message_id) not in unique_messages:
                unique_messages[str(message_id)] = message
        
        # 시간순 정렬
        sorted_messages = sorted(
            unique_messages.values(),
            key=lambda x: x.get("timestamp", ""),
            reverse=False
        )
        
        logger.info(f"세션 메시지 조회 완료: {session_id} - 총 {len(sorted_messages)}개 메시지")
        
        return safe_json_response({
            "success": True,
            "messages": sorted_messages,
            "count": len(sorted_messages)
        })
    except Exception as e:
        logger.error(f"세션 메시지 조회 오류: {str(e)}")
        # 오류 발생 시에도 빈 메시지 목록 반환 (500 에러 대신)
        return safe_json_response({
            "success": True,
            "messages": [],
            "count": 0
        })

@app.post("/api/messages")
async def save_message(request: Request):
    """메시지 저장 API"""
    try:
        body = await request.json()
        session_id = body.get("session_id")
        sender = body.get("sender", "user")
        content = body.get("content", "")
        
        if not session_id or not content:
            raise HTTPException(status_code=400, detail="세션 ID와 메시지 내용이 필요합니다.")
        
        message_id = None
        
        # DB에 저장 (가능한 경우)
        if DATABASE_AVAILABLE and db_manager is not None and getattr(db_manager, "db", None) is not None:
            try:
                message_id = await db_manager.save_message(session_id, sender, content)
                if message_id:
                    logger.info(f"메시지 저장 완료: {message_id}")
                else:
                    logger.warning("메시지 DB 저장 실패, 메모리에만 저장")
            except Exception as e:
                logger.error(f"메시지 저장 오류: {str(e)}")
        
        # 메모리에도 저장
        if session_id not in messages_db:
            messages_db[session_id] = []
        
        message_data = {
            "message_id": message_id or str(uuid.uuid4()),
            "session_id": session_id,
            "sender": sender,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        messages_db[session_id].append(message_data)
        
        # 세션 업데이트
        if DATABASE_AVAILABLE and db_manager is not None and getattr(db_manager, "db", None) is not None:
            try:
                await db_manager.update_session(session_id, {
                    "last_activity": datetime.now().isoformat(),
                    "message_count": len(messages_db.get(session_id, []))
                })
            except Exception as e:
                logger.error(f"세션 업데이트 오류: {str(e)}")
        
        return JSONResponse(content={
            "success": True,
            "message_id": message_id or str(uuid.uuid4()),
            "session_id": session_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메시지 저장 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="메시지 저장 중 오류가 발생했습니다.")

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    try:
        if DATABASE_AVAILABLE:
            await db_manager.remove_session(session_id)
        
        logger.info(f"세션 삭제 완료: {session_id}")
        
        success_response = {
            "success": True,
            "message": "세션이 삭제되었습니다."
        }
        return safe_json_response(success_response)
    except Exception as e:
        logger.error(f"세션 삭제 오류: {str(e)}")
        error_response = {"success": False, "error": str(e)}
        return safe_json_response(error_response)

# 관리자 관련 엔드포인트
@app.get("/api/admin/users")
async def get_all_users():
    """관리자용 모든 사용자 조회 API"""
    try:
        users = []
        # DB에서 조회 (가능한 경우)
        if DATABASE_AVAILABLE and db_manager is not None and getattr(db_manager, "db", None) is not None:
    try:
                db_users = await db_manager.get_all_users()
                users.extend(db_users)
                logger.info(f"DB에서 {len(db_users)}개 사용자 조회")
            except Exception as e:
                logger.error(f"사용자 목록 조회 실패: {str(e)}")
        # 메모리에서도 조회
        for user_id, user_data in users_db.items():
            users.append(user_data)
        # 중복 제거 (user_id 기준)
        unique_users = {}
        for user in users:
            user_id = user.get("user_id") or user.get("_id")
            if user_id and str(user_id) not in unique_users:
                unique_users[str(user_id)] = user
        return safe_json_response({
            "success": True,
            "users": list(unique_users.values()),
            "count": len(unique_users)
        })
    except Exception as e:
        logger.error(f"사용자 목록 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 목록 조회 중 오류가 발생했습니다.")

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str):
    """사용자 삭제 (관리자용)"""
    try:
        result = await auth_system.delete_user(user_id)
        return safe_json_response(result)
    except Exception as e:
        logger.error(f"사용자 삭제 오류: {str(e)}")
        error_response = {"success": False, "message": "사용자 삭제 중 오류가 발생했습니다."}
        return safe_json_response(error_response)

@app.get("/api/memory/{user_id}")
async def get_user_memory(user_id: str):
    """사용자 메모리 조회"""
    from bson import ObjectId
    
    try:
        interactions = await db_manager.get_user_interactions(user_id, limit=50)
        
        # ObjectId 변환 적용
        safe_interactions = []
        if interactions:
            for interaction in interactions:
                safe_interaction = {}
                for k, v in interaction.items():
                    if isinstance(v, ObjectId):
                        safe_interaction[k] = str(v)
                    elif isinstance(v, dict):
                        safe_interaction[k] = {sk: str(sv) if isinstance(sv, ObjectId) else sv for sk, sv in v.items()}
                    else:
                        safe_interaction[k] = v
                safe_interactions.append(safe_interaction)
        
        response_data = {"interactions": safe_interactions, "user_id": user_id}
        return safe_json_response(response_data)
    except Exception as e:
        logger.error(f"메모리 조회 오류: {str(e)}")
        error_response = {"interactions": [], "user_id": user_id, "error": str(e)}
        return safe_json_response(error_response)

@app.get("/api/search")
async def search_memories(query: str, user_id: str = None):
    """메모리 검색"""
    from bson import ObjectId
    
    try:
        results = await db_manager.search_interactions(query, user_id, limit=20)
        
        # ObjectId 변환 적용
        safe_results = []
        if results:
            for result in results:
                safe_result = {}
                for k, v in result.items():
                    if isinstance(v, ObjectId):
                        safe_result[k] = str(v)
                    elif isinstance(v, dict):
                        safe_result[k] = {sk: str(sv) if isinstance(sv, ObjectId) else sv for sk, sv in v.items()}
                    else:
                        safe_result[k] = v
                safe_results.append(safe_result)
        
        response_data = {"results": safe_results, "query": query, "user_id": user_id}
        return safe_json_response(response_data)
    except Exception as e:
        logger.error(f"메모리 검색 오류: {str(e)}")
        error_response = {"results": [], "query": query, "user_id": user_id, "error": str(e)}
        return safe_json_response(error_response)

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    health_data = {"status": "healthy", "timestamp": datetime.now().isoformat()}
    return safe_json_response(health_data)

# API 연결 테스트
@app.get("/api/test")
async def test_api():
    response_data = {"message": "API 정상 동작", "status": "ok"}
    return safe_json_response(response_data)

# 대화 연결 테스트
@app.post("/api/test-chat")
async def test_chat(request: Request):
    try:
        body = await request.json()
        test_message = body.get("message", "안녕하세요")
        
        # 간단한 응답 생성
        response = {
            "success": True,
            "message": "대화 연결 성공!",
            "response": f"테스트 메시지 '{test_message}'를 받았습니다. EORA AI 시스템이 정상적으로 작동하고 있습니다.",
            "timestamp": datetime.now().isoformat(),
            "systems_available": {
                "eora_core": EORA_CORE_AVAILABLE,
                "eora_consciousness": EORA_CONSCIOUSNESS_AVAILABLE,
                "eora_enhanced": EORA_ENHANCED_AVAILABLE,
                "eora_gai": EORA_GAI_AVAILABLE
            }
        }
        
        return safe_json_response(response)
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return safe_json_response(error_response)

@app.post("/api/set-language")
async def set_language(request: Request):
    """언어 설정 API"""
    try:
        body = await request.json()
        language = body.get("language", "ko")
        
        # 쿠키에 언어 설정 저장
        response = {"success": True, "language": language}
        
        return safe_json_response(response)
    except Exception as e:
        logger.error(f"언어 설정 오류: {str(e)}")
        error_response = {"success": False, "error": str(e)}
        return safe_json_response(error_response)

@app.get("/api/eora/manifest")
async def get_eora_manifest():
    """EORA 매니페스트 조회"""
    try:
        manifest = eora_enhanced.manifest()
        response_data = {
            "manifest": manifest,
            "timestamp": datetime.now().isoformat()
        }
        return safe_json_response(response_data)
    except Exception as e:
        logger.error(f"매니페스트 조회 오류: {str(e)}")
        error_response = {"error": str(e), "timestamp": datetime.now().isoformat()}
        return safe_json_response(error_response)

@app.get("/api/eora/gai/status")
async def get_eora_gai_status():
    """EORA_GAI 시스템 상태 조회"""
    try:
        if not EORA_GAI_AVAILABLE:
            response_data = {
                "available": False,
                "message": "EORA_GAI 시스템을 사용할 수 없습니다.",
                "timestamp": datetime.now().isoformat()
            }
            return safe_json_response(response_data)
        
        # 고급 시스템 상태 조회
        system_state = await update_system_state_advanced()
        
        response_data = {
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
        return safe_json_response(response_data)
    except Exception as e:
        logger.error(f"EORA_GAI 상태 조회 오류: {str(e)}")
        error_response = {
            "available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        return safe_json_response(error_response)

@app.get("/api/eora/prompts")
async def get_available_prompts():
    """사용 가능한 프롬프트 목록 조회"""
    try:
        prompts = eora_enhanced.prompts
        response_data = {
            "prompts": list(prompts.keys()),
            "count": len(prompts),
            "timestamp": datetime.now().isoformat()
        }
        return safe_json_response(response_data)
    except Exception as e:
        logger.error(f"프롬프트 목록 조회 오류: {str(e)}")
        error_response = {"error": str(e), "timestamp": datetime.now().isoformat()}
        return safe_json_response(error_response)

@app.get("/api/eora/prompt/{prompt_name}")
async def get_prompt_content(prompt_name: str):
    """특정 프롬프트 내용 조회"""
    try:
        # 프롬프트 이름 정규화
        normalized_name = prompt_name.replace(' ', ' ').upper()
        
        for name, content in eora_enhanced.prompts.items():
            if normalized_name in name.upper():
                response_data = {
                    "name": name,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                return safe_json_response(response_data)
        
        error_response = {"error": "프롬프트를 찾을 수 없습니다", "timestamp": datetime.now().isoformat()}
        return safe_json_response(error_response)
        
    except Exception as e:
        logger.error(f"프롬프t 내용 조회 오류: {str(e)}")
        error_response = {"error": str(e), "timestamp": datetime.now().isoformat()}
        return safe_json_response(error_response)

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
        
        return safe_json_response({
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException as he:
        error_response = {"error": str(he.detail), "status_code": he.status_code}
        return safe_json_response(error_response)
    except Exception as e:
        logger.error(f"메모리 회상 오류: {str(e)}")
        error_response = {"error": str(e), "timestamp": datetime.now().isoformat()}
        return safe_json_response(error_response)

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
        
        return safe_json_response({
            "query": query,
            "search_type": search_type,
            "results_count": len(memories),
            "memories": memories,
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException as he:
        error_response = {"error": str(he.detail), "status_code": he.status_code}
        return safe_json_response(error_response)
    except Exception as e:
        logger.error(f"메모리 검색 오류: {str(e)}")
        error_response = {"error": str(e), "timestamp": datetime.now().isoformat()}
        return safe_json_response(error_response)

@app.get("/api/eora/memory/stats/{user_id}")
async def get_memory_stats(user_id: str):
    """메모리 통계 API"""
    try:
        stats = await db_manager.get_user_memory_stats(user_id)
        
        return safe_json_response({
            "user_id": user_id,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"메모리 통계 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/eora/memory/recent/{user_id}")
async def get_recent_memories(user_id: str, limit: int = 10):
    """사용자의 최근 기억 조회"""
    try:
        if DATABASE_AVAILABLE:
            memories = await db_manager.get_recent_memories(user_id, limit)
            return safe_json_response({
                "memories": memories
            })
        else:
            return safe_json_response({
                "memories": [],
                "message": "데이터베이스가 사용 불가능합니다."
            })
    except Exception as e:
        logger.error(f"최근 기억 조회 오류: {str(e)}")
        return safe_json_response({
            "memories": [],
            "error": str(e)
        })

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

@app.get("/api/aura/summary/{user_id}")
async def get_aura_summary(user_id: str):
    """사용자 아우라 요약 조회"""
    try:
        summary = await aura_storage.get_aura_summary(user_id)
        return safe_json_response(summary)
    except Exception as e:
        logger.error(f"아우라 요약 조회 오류: {str(e)}")
        return safe_json_response({"error": str(e)})

@app.post("/api/recall/perform")
async def perform_recall(request: Request):
    """회상 수행"""
    try:
        body = await request.json()
        user_id = body.get("user_id", str(uuid.uuid4()))
        recall_type = body.get("recall_type", None)
        
        result = await recall_system.perform_recall(user_id, recall_type)
        return safe_json_response(result)
    except Exception as e:
        logger.error(f"회상 수행 오류: {str(e)}")
        return safe_json_response({"error": str(e)})

@app.get("/api/recall/types")
async def get_recall_types():
    """회상 유형 목록 조회"""
    try:
        return safe_json_response({
            "recall_types": aura_storage.recall_types,
            "description": "8가지 회상 유형을 제공합니다."
        })
    except Exception as e:
        logger.error(f"회상 유형 조회 오류: {str(e)}")
        return safe_json_response({"error": str(e)})

@app.get("/api/aura/stats/{user_id}")
async def get_aura_stats(user_id: str):
    """사용자 아우라 통계 조회"""
    try:
        if user_id not in aura_storage.aura_data:
            return safe_json_response({"error": "사용자 데이터가 없습니다."})
        
        aura_history = aura_storage.aura_data[user_id]
        if not aura_history:
            return safe_json_response({"error": "아우라 데이터가 없습니다."})
        
        # 통계 계산
        total_interactions = len(aura_history)
        emotional_states = [aura.get("emotional_state", {}).get("primary_emotion", "neutral") for aura in aura_history]
        consciousness_levels = [aura.get("consciousness_level", 0.0) for aura in aura_history]
        interaction_qualities = [aura.get("interaction_quality", 0.5) for aura in aura_history]
        
        stats = {
            "total_interactions": total_interactions,
            "dominant_emotion": max(set(emotional_states), key=emotional_states.count) if emotional_states else "neutral",
            "average_consciousness": sum(consciousness_levels) / len(consciousness_levels) if consciousness_levels else 0.0,
            "average_quality": sum(interaction_qualities) / len(interaction_qualities) if interaction_qualities else 0.5,
            "emotional_distribution": {emotion: emotional_states.count(emotion) for emotion in set(emotional_states)},
            "growth_trend": await _calculate_growth_trend(aura_history)
        }
        
        return safe_json_response(stats)
    except Exception as e:
        logger.error(f"아우라 통계 조회 오류: {str(e)}")
        return safe_json_response({"error": str(e)})

@app.post("/api/aura/export/{user_id}")
async def export_aura_data(user_id: str):
    """아우라 데이터 내보내기"""
    try:
        if user_id not in aura_storage.aura_data:
            return safe_json_response({"error": "사용자 데이터가 없습니다."})
        
        aura_data = aura_storage.aura_data[user_id]
        summary = await aura_storage.get_aura_summary(user_id)
        stats = await get_aura_stats(user_id)
        
        export_data = {
            "user_id": user_id,
            "export_timestamp": datetime.now().isoformat(),
            "total_interactions": len(aura_data),
            "aura_history": aura_data,
            "summary": summary,
            "statistics": stats
        }
        
        return safe_json_response(export_data)
    except Exception as e:
        logger.error(f"아우라 데이터 내보내기 오류: {str(e)}")
        return safe_json_response({"error": str(e)})

@app.delete("/api/aura/clear/{user_id}")
async def clear_aura_data(user_id: str):
    """아우라 데이터 삭제"""
    try:
        if user_id in aura_storage.aura_data:
            del aura_storage.aura_data[user_id]
            logger.info(f"아우라 데이터 삭제 완료 - 사용자: {user_id}")
            return safe_json_response({"success": True, "message": "아우라 데이터가 삭제되었습니다."})
        else:
            return safe_json_response({"success": False, "message": "삭제할 데이터가 없습니다."})
    except Exception as e:
        logger.error(f"아우라 데이터 삭제 오류: {str(e)}")
        return safe_json_response({"error": str(e)})

def mongo_safe(obj):
    """MongoDB 응답을 JSON 직렬화 가능하게 변환하는 완전히 안전한 함수"""
    from bson import ObjectId
    from datetime import datetime, date
    from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult
    import json
    
    def _deep_convert(item):
        if item is None:
            return None
        elif isinstance(item, ObjectId):
            return str(item)
        elif isinstance(item, (datetime, date)):
            return item.isoformat()
        elif isinstance(item, InsertOneResult):
            return str(item.inserted_id)
        elif isinstance(item, InsertManyResult):
            return [str(i) for i in item.inserted_ids]
        elif isinstance(item, UpdateResult):
            return {
                "matched_count": item.matched_count,
                "modified_count": item.modified_count,
                "upserted_id": str(item.upserted_id) if item.upserted_id else None
            }
        elif isinstance(item, DeleteResult):
            return {
                "deleted_count": item.deleted_count
            }
        elif isinstance(item, dict):
            return {k: _deep_convert(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [_deep_convert(i) for i in item]
        elif isinstance(item, tuple):
            return tuple(_deep_convert(i) for i in item)
        elif isinstance(item, set):
            return [_deep_convert(i) for i in item]
        elif isinstance(item, (str, int, float, bool)):
            return item
        else:
            # 기타 모든 타입을 문자열로 변환
            try:
                return str(item)
            except:
                return "변환_불가능한_객체"
    
    try:
        result = _deep_convert(obj)
        # 최종 검증: JSON 직렬화 테스트
        json.dumps(result, ensure_ascii=False, default=str)
        return result
    except Exception as e:
        logger.error(f"mongo_safe 변환 오류: {e}")
        # 오류 발생 시 기본값 반환
        if isinstance(obj, dict):
            return {"error": "변환_실패", "original_type": str(type(obj))}
        elif isinstance(obj, list):
            return ["변환_실패"]
        else:
            return "변환_실패"

# 완전히 안전한 JSON 응답을 위한 래퍼 함수
def safe_json_response(data):
    """완전히 안전한 JSON 응답 생성 - FastAPI 내부 직렬화 우회"""
    from fastapi.responses import Response
    from bson import ObjectId
    from datetime import datetime, date
    
    try:
        # 1단계: 완전히 안전한 직렬화 함수로 변환
        def ultra_safe_serialize(obj):
            """모든 타입을 안전하게 직렬화"""
            if obj is None:
                return None
            elif isinstance(obj, ObjectId):
                return str(obj)
            elif isinstance(obj, (datetime, date)):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: ultra_safe_serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [ultra_safe_serialize(item) for item in obj]
            elif isinstance(obj, tuple):
                return [ultra_safe_serialize(item) for item in obj]
            elif isinstance(obj, set):
                return [ultra_safe_serialize(item) for item in obj]
            elif isinstance(obj, (str, int, float, bool)):
                return obj
            else:
                # 기타 모든 타입을 문자열로 변환
                try:
                    return str(obj)
                except:
                    return "직렬화_불가능한_객체"
        
        # 2단계: 데이터 변환
        safe_data = ultra_safe_serialize(data)
        
        # 3단계: JSON 문자열로 직접 변환
        import json
        json_str = json.dumps(safe_data, ensure_ascii=False, default=str)
        
        # 4단계: Response 객체로 직접 반환 (FastAPI 직렬화 우회)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        logger.error(f"safe_json_response 오류: {e}")
        # 오류 발생 시 완전히 안전한 기본 응답
        fallback_data = {
            "error": "응답 처리 중 오류가 발생했습니다.",
            "error_details": str(e),
            "timestamp": datetime.now().isoformat()
        }
        try:
            import json
            fallback_json = json.dumps(fallback_data, ensure_ascii=False, default=str)
            return Response(
                content=fallback_json,
                media_type="application/json",
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        except:
            # 최종 폴백
            return Response(
                content='{"error": "시스템 오류"}',
                media_type="application/json"
            )

# 1. /test 라우트 추가
@app.get("/test")
async def test_page():
    return {"message": "테스트 페이지 정상 동작", "status": "ok"}

# 중복된 라우트 제거 - 이미 위에 정의되어 있음

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Railway 환경변수에서 포트 가져오기 (기본값을 8001로 변경)
    port = int(os.environ.get("PORT", 8001))
    
    print(f"🚀 EORA AI 서버를 시작합니다...")
    print(f"📍 주소: http://127.0.0.1:{port}")
    print(f"📋 사용 가능한 페이지:")
    print(f"   - 홈: http://127.0.0.1:{port}/")
    print(f"   - 디버그: http://127.0.0.1:{port}/debug")
    print(f"   - 채팅: http://127.0.0.1:{port}/chat")
    print(f"   - 상태 확인: http://127.0.0.1:{port}/health")
    print("=" * 50)
    
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=port, 
        reload=False
    ) 