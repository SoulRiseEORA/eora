#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 수정된 서버 - 메시지 저장 문제 해결
"""

import os
import sys
import json
import hashlib
import io
import re
from datetime import datetime
from typing import Optional, Dict, List, Any

from fastapi import FastAPI, Request, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

# EORA 고급 기능 모듈 임포트
sys.path.append('src')

# 토큰 계산기 임포트
try:
    from token_calculator import get_token_calculator
    TOKEN_CALCULATOR_AVAILABLE = True
    print("✅ 토큰 계산기 모듈 로드 성공")
except ImportError as e:
    print(f"⚠️ 토큰 계산기 모듈 로드 실패: {e}")
    TOKEN_CALCULATOR_AVAILABLE = False

# 성능 최적화 모듈 임포트
try:
    from performance_optimizer import performance_monitor, cached_response, initialize_optimizer, get_performance_stats
    PERFORMANCE_OPTIMIZATION_AVAILABLE = True
    print("✅ 성능 최적화 모듈 로드 성공")
except ImportError as e:
    print(f"⚠️ 성능 최적화 모듈 로드 실패: {e}")
    # 기본 데코레이터 정의
    def performance_monitor(func):
        return func
    def cached_response(ttl=300):
        def decorator(func):
            return func
        return decorator
    async def initialize_optimizer():
        pass
    def get_performance_stats():
        return {}
    PERFORMANCE_OPTIMIZATION_AVAILABLE = False

try:
    from eora_advanced_chat_system import process_advanced_message
    from aura_system.recall_engine import RecallEngine
    from aura_memory_system import EORAMemorySystem
    from database import mongo_client, verify_connection, db_mgr
    
    # EORA 메모리 시스템 초기화
    eora_memory_system = EORAMemorySystem()
    
    # 회상 엔진 초기화 (memory_manager와 함께)
    if hasattr(eora_memory_system, 'memory_manager') and eora_memory_system.memory_manager:
        recall_engine = RecallEngine(eora_memory_system.memory_manager)
        print("✅ RecallEngine 초기화 완료 (memory_manager 연결)")
    else:
        recall_engine = None
        print("⚠️ memory_manager 없음 - RecallEngine 비활성화")
    
    ADVANCED_FEATURES_AVAILABLE = True
    print("✅ EORA 고급 기능 모듈 로드 성공")
    print("✅ EORAMemorySystem 초기화 완료")
except ImportError as e:
    print(f"⚠️ EORA 고급 기능 모듈 로드 실패: {e}")
    eora_memory_system = None
    recall_engine = None
    ADVANCED_FEATURES_AVAILABLE = False

# 환경변수 로딩 및 Railway 환경 최적화
from dotenv import load_dotenv

def detect_railway_environment():
    """Railway 환경을 강력하게 감지합니다."""
    railway_indicators = [
        os.getenv("RAILWAY_ENVIRONMENT"),
        os.getenv("RAILWAY_PROJECT_ID"), 
        os.getenv("RAILWAY_SERVICE_ID"),
        os.getenv("RAILWAY_DEPLOYMENT_ID"),
        os.getenv("RAILWAY_REPLICA_ID"),
        # Railway는 항상 PORT를 설정하고 특정 값들을 가짐
        (os.getenv("PORT") and not os.getenv("DEVELOPMENT") and not os.getenv("VSCODE_GIT_ASKPASS_NODE"))
    ]
    
    is_railway = any(railway_indicators)
    if is_railway:
        print("🚂 Railway 환경 감지됨!")
        print(f"   PORT: {os.getenv('PORT', 'N/A')}")
        print(f"   PROJECT_ID: {os.getenv('RAILWAY_PROJECT_ID', 'N/A')[:8]}...")
        print(f"   SERVICE_ID: {os.getenv('RAILWAY_SERVICE_ID', 'N/A')[:8]}...")
    else:
        print("💻 로컬 환경으로 판단됨")
    
    return is_railway

def load_environment_variables():
    """환경에 따라 환경변수를 로드합니다."""
    railway_env = detect_railway_environment()
    
    if not railway_env:
        # 로컬 환경: .env 파일 로드
        env_paths = ['.env', 'src/.env', '../.env']
        env_loaded = False
        for env_path in env_paths:
            if os.path.exists(env_path):
                load_dotenv(env_path)
                print(f"🔄 로컬 .env 파일 로드: {env_path}")
                env_loaded = True
                break
        
        if not env_loaded:
            print("⚠️ .env 파일을 찾을 수 없습니다.")
    else:
        print("🚂 Railway 환경변수를 사용합니다")
    
    return railway_env

def get_openai_api_key():
    """강화된 OpenAI API 키 찾기 (Railway 디버깅 강화)"""
    # Railway와 로컬 환경에서 사용 가능한 모든 키 이름 시도
    possible_keys = [
        "OPENAI_API_KEY",
        "OPENAI_API_KEY_1", 
        "OPENAI_API_KEY_2",
        "OPENAI_API_KEY_3",
        "OPENAI_API_KEY_4",
        "OPENAI_API_KEY_5",
        "OPENAI_KEY",
        "API_KEY",
        "GPT_API_KEY"
    ]
    
    print("🔍 OpenAI API 키 검색 중...")
    print(f"🔍 모든 환경변수 개수: {len(os.environ)}")
    
    # Railway 환경에서 모든 환경변수 키를 출력 (디버깅용)
    env_keys = list(os.environ.keys())
    openai_related_keys = [k for k in env_keys if 'OPENAI' in k.upper() or 'API' in k.upper() or 'GPT' in k.upper()]
    if openai_related_keys:
        print(f"🔍 API 관련 환경변수 키들: {openai_related_keys}")
    else:
        print("⚠️ API 관련 환경변수가 전혀 없습니다!")
    
    found_keys = []
    
    for key_name in possible_keys:
        key_value = os.getenv(key_name)
        print(f"🔍 {key_name}: {'찾음' if key_value else '없음'}")
        if key_value:
            if key_value.startswith("sk-"):
                print(f"✅ 유효한 API 키 발견: {key_name} = sk-...{key_value[-8:]}")
                return key_value
            else:
                found_keys.append(f"{key_name}={key_value[:10]}...")
                print(f"⚠️ 유효하지 않은 키 형식: {key_name} = {key_value[:20]}...")
    
    print("❌ 유효한 OpenAI API 키를 찾을 수 없습니다!")
    if found_keys:
        print("📋 발견된 키들 (유효하지 않음):")
        for key_info in found_keys:
            print(f"   {key_info}")
    else:
        print("📋 OpenAI 관련 환경변수가 전혀 설정되지 않았습니다!")
        print("📋 Railway에서 다음 환경변수를 설정하세요:")
        print("   OPENAI_API_KEY=sk-proj-your-actual-key-here")
        print("📋 또는 다음 중 하나:")
        for key_name in possible_keys[:5]:
            print(f"   {key_name}=sk-proj-your-actual-key-here")
    
    return None

def initialize_openai():
    """최신 OpenAI 클라이언트 초기화 (성능 최적화)"""
    global openai_client
    openai_client = None
    
    try:
        from openai import AsyncOpenAI
        
        api_key = get_openai_api_key()
        if api_key:
            # 성능 최적화된 클라이언트 설정
            openai_client = AsyncOpenAI(
                api_key=api_key,
                timeout=15.0,  # 더 빠른 타임아웃
                max_retries=1   # 재시도 최소화
            )
            return True
        else:
            return False
            
    except ImportError:
        return False
    except Exception:
        return False

# 환경변수 로드 및 OpenAI 초기화
railway_env_loaded = load_environment_variables()
OPENAI_AVAILABLE = initialize_openai()

print("=" * 50)
print("🌍 환경 설정 완료")
print(f"   환경: {'Railway' if railway_env_loaded else '로컬'}")
print(f"   OpenAI 사용 가능: {OPENAI_AVAILABLE}")
if railway_env_loaded:
    print(f"   Railway 포트: {os.getenv('PORT', 'N/A')}")
    print("🚂 Railway 환경변수 디버깅 정보:")
    
    # Railway 환경변수 확인
    railway_vars = {
        "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
        "RAILWAY_PROJECT_ID": os.getenv("RAILWAY_PROJECT_ID"),
        "RAILWAY_SERVICE_ID": os.getenv("RAILWAY_SERVICE_ID"),
        "PORT": os.getenv("PORT")
    }
    
    for key, value in railway_vars.items():
        print(f"   {key}: {'설정됨' if value else '미설정'}")
    
    # OpenAI 관련 환경변수 확인
    print("🔑 OpenAI API 환경변수 상태:")
    openai_keys = ["OPENAI_API_KEY", "OPENAI_API_KEY_1", "OPENAI_API_KEY_2", "OPENAI_KEY", "API_KEY"]
    for key in openai_keys:
        value = os.getenv(key)
        if value:
            if value.startswith("sk-"):
                print(f"   {key}: ✅ 유효함 (sk-...{value[-8:]})")
            else:
                print(f"   {key}: ❌ 유효하지 않음 ({value[:20]}...)")
        else:
            print(f"   {key}: ❌ 미설정")
    
    # OpenAI 클라이언트 상태
    print(f"🤖 OpenAI 클라이언트: {'✅ 초기화됨' if (OPENAI_AVAILABLE and 'openai_client' in globals() and openai_client) else '❌ 미초기화'}")
    
    # 자동응답 제거 알림
    print("🚫 자동응답 완전 제거됨 - OpenAI API만 사용")
    if not (OPENAI_AVAILABLE and 'openai_client' in globals() and openai_client):
        print("⚠️ 경고: API 키가 없으면 채팅이 작동하지 않습니다!")
        print("   → Railway Dashboard → Variables → OPENAI_API_KEY 설정 필요")
    
    # Railway 환경에서 추가 디버깅 정보
    print("📊 Railway 디버깅 정보:")
    print(f"   - 전체 환경변수 수: {len(os.environ)}")
    
    # 모든 OpenAI 관련 환경변수 검사
    openai_vars = {}
    for key in ["OPENAI_API_KEY", "OPENAI_API_KEY_1", "OPENAI_API_KEY_2", "OPENAI_API_KEY_3", "OPENAI_KEY", "API_KEY"]:
        value = os.getenv(key)
        if value:
            if value.startswith("sk-"):
                openai_vars[key] = f"✅ 유효함 (sk-...{value[-6:]})"
            else:
                openai_vars[key] = f"❌ 유효하지 않음 ({value[:15]}...)"
        else:
            openai_vars[key] = "❌ 미설정"
    
    print("🔑 OpenAI 환경변수 상태:")
    valid_keys_count = 0
    for key, status in openai_vars.items():
        print(f"   - {key}: {status}")
        if "✅ 유효함" in status:
            valid_keys_count += 1
    
    print(f"🔑 유효한 API 키 개수: {valid_keys_count}")
    if valid_keys_count == 0:
        print("❌ 경고: 유효한 OpenAI API 키가 없습니다!")
        print("   Railway Dashboard → Variables → OPENAI_API_KEY 확인 필요")
    
    # Railway 서비스 정보
    railway_info = {
        "PROJECT_ID": os.getenv("RAILWAY_PROJECT_ID"),
        "SERVICE_ID": os.getenv("RAILWAY_SERVICE_ID"),
        "DEPLOYMENT_ID": os.getenv("RAILWAY_DEPLOYMENT_ID"),
        "ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT")
    }
    
    print("🚂 Railway 서비스 정보:")
    for key, value in railway_info.items():
        if value:
            print(f"   - {key}: {value[:16]}...")
        else:
            print(f"   - {key}: 미설정")
    
print("=" * 50)

# 앱 초기화
app = FastAPI(title="EORA AI Fixed Server")

# 미들웨어 설정
app.add_middleware(SessionMiddleware, secret_key="eora-secret-key-2024")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정 (Railway 환경 대응)
from pathlib import Path

# 현재 스크립트의 절대 경로 기준으로 디렉토리 설정
current_dir = Path(__file__).parent
static_dir = current_dir / "src" / "static"
templates_dir = current_dir / "src" / "templates"

# 경로가 존재하지 않으면 대체 경로 사용
if not static_dir.exists():
    static_dir = current_dir / "static"
if not templates_dir.exists():
    templates_dir = current_dir / "templates"

# 최종 확인 후 기본값 설정
if not static_dir.exists():
    static_dir = Path("static")
if not templates_dir.exists():
    templates_dir = Path("templates")

print(f"📂 Static 디렉토리: {static_dir}")
print(f"📂 Templates 디렉토리: {templates_dir}")

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# 데이터 파일 경로
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json") 
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")

# 데이터 디렉토리 생성
os.makedirs(DATA_DIR, exist_ok=True)

# 메모리 내 데이터베이스
users_db = {}
sessions_db = {}
messages_db = {}

# ==================== EORA 고급 시스템 초기화 ====================

# 고급 기능 시스템 전역 변수
eora_memory_system = None
recall_engine = None

def initialize_advanced_systems():
    """EORA 고급 시스템들을 초기화합니다."""
    global eora_memory_system, recall_engine
    
    if not ADVANCED_FEATURES_AVAILABLE:
        print("⚠️ 고급 기능이 비활성화되어 있습니다.")
        return False
    
    try:
        print("🔄 EORA 고급 시스템 초기화 중...")
        
        # 메모리 시스템 초기화
        eora_memory_system = EORAMemorySystem()
        print("✅ EORA 메모리 시스템 초기화 완료")
        
        # 회상 엔진 초기화 (메모리 매니저 연결)
        if hasattr(eora_memory_system, 'memory_manager'):
            recall_engine = RecallEngine(eora_memory_system.memory_manager)
            print("✅ 8종 회상 엔진 초기화 완료")
        else:
            print("⚠️ 메모리 매니저 없음 - 기본 회상 엔진 사용")
            recall_engine = None
        
        print("🚀 EORA 고급 시스템 초기화 성공!")
        return True
        
    except Exception as e:
        print(f"❌ EORA 고급 시스템 초기화 실패: {e}")
        return False

# 시스템 초기화 실행
advanced_systems_ready = initialize_advanced_systems()

# ==================== EORA 고급 응답 생성 ====================

async def generate_advanced_response(message: str, user_id: str, session_id: str, conversation_history: List[Dict]) -> str:
    """EORA 고급 기능을 활용한 AI 응답 생성 (성능 최적화)"""
    try:
        # 1. 고급 기능이 비활성화된 경우 OpenAI API 직접 사용
        if not ADVANCED_FEATURES_AVAILABLE or not eora_memory_system:
            result = await generate_openai_response(message, conversation_history, [])
            return result["response"] if isinstance(result, dict) else result
        
        # 2. 강화된 8종 회상 시스템 + 고급 기능 활성화
        recalled_memories = []
        enhanced_context = ""
        
        try:
            if eora_memory_system:
                print("🧠 EORA 8종 회상 시스템 시작...")
                
                # 8종 회상 시스템 실행 (3개 결과로 제한)
                recalled_memories = await eora_memory_system.enhanced_recall(message, user_id, limit=3)
                
                # 고급 기능 시스템 실행 (직관, 통찰, 지혜)
                enhanced_context = await eora_memory_system.generate_response(
                    user_input=message,
                    user_id=user_id,
                    recalled_memories=recalled_memories,
                    conversation_history=conversation_history
                )
                
                print(f"✅ EORA 시스템 완료 - 회상: {len(recalled_memories)}개, 컨텍스트: {len(enhanced_context)}자")
                
            elif recall_engine:
                # Fallback: 기존 회상 엔진
                context = {"user_id": user_id, "session_id": session_id}
                recalled_memories = await recall_engine.recall(query=message, context=context, limit=3)
                print(f"🔄 Fallback 회상 엔진 - {len(recalled_memories)}개 회상")
        
        except Exception as e:
            print(f"❌ 회상 시스템 오류: {e}")
        
        # 3. OpenAI API 기반 응답 (8종 회상 + 고급 기능 통합)
        if enhanced_context:
            # 고급 컨텍스트가 있으면 메모리에 추가
            enhanced_memories = recalled_memories.copy()
            enhanced_memories.append({
                "content": enhanced_context,
                "type": "eora_enhancement",
                "recall_type": "advanced_features"
            })
            result = await generate_openai_response(message, conversation_history, enhanced_memories)
            return result["response"] if isinstance(result, dict) else result
        else:
            result = await generate_openai_response(message, conversation_history, recalled_memories)
            return result["response"] if isinstance(result, dict) else result
        
    except Exception as e:
        print(f"❌ 고급 응답 생성 전체 오류: {e}")
        return f"시스템 오류가 발생했습니다: {str(e)}"

async def generate_openai_response(message: str, history: List[Dict], memories: List[Dict] = None) -> Dict[str, Any]:
    """OpenAI API를 사용한 응답 생성 (성능 최적화 + AI1 프롬프트 적용)"""
    global openai_client
    try:
        # OpenAI 클라이언트 확인 (성능 최적화)
        if not OPENAI_AVAILABLE or not openai_client:
            # 빠른 재초기화 시도
            retry_key = get_openai_api_key()
            if retry_key:
                try:
                    from openai import AsyncOpenAI
                    openai_client = AsyncOpenAI(
                        api_key=retry_key,
                        timeout=15.0,  # 타임아웃 단축
                        max_retries=1  # 재시도 횟수 최소화
                    )
                    # 재귀 호출로 다시 시도
                    return await generate_openai_response(message, history, memories)
                except Exception:
                    pass
            
            return {
                "response": "OpenAI API 사용 불가: 환경변수를 확인해주세요.",
                "token_usage": None
            }
        
        # 🎯 AI1 프롬프트 동적 로드
        system_prompt = await load_ai1_system_prompt()
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 회상된 기억 추가 (정확히 3개로 제한)
        if memories:
            top_memories = memories[:3]  # 정확히 3개만 선택
            memory_contexts = []
            
            for i, memory in enumerate(top_memories, 1):
                content = memory.get('content', '')
                recall_type = memory.get('recall_type', '일반')
                
                # 각 회상 유형별 태그 추가
                if recall_type == "eora_enhancement":
                    memory_contexts.append(f"🧠 EORA 고급 기능:\n{content}")
                elif recall_type in ["keyword", "embedding", "emotion", "belief", "context", "temporal", "association", "pattern"]:
                    memory_contexts.append(f"🔍 {recall_type} 회상 #{i}:\n{content[:200]}...")
                else:
                    memory_contexts.append(f"💭 관련 기억 #{i}:\n{content[:200]}...")
            
            if memory_contexts:
                combined_context = "\n\n".join(memory_contexts)
                messages.append({
                    "role": "system", 
                    "content": f"관련 기억 및 맥락 (총 {len(top_memories)}개):\n\n{combined_context}"
                })
        
        # 최근 대화 기록 추가 (최대 4개로 단축하여 성능 향상)
        for msg in history[-4:]:
            if msg.get('role') in ['user', 'assistant']:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # 현재 메시지 추가
        messages.append({"role": "user", "content": message})
        
        # OpenAI API 호출 (성능 최적화)
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            timeout=15.0  # 응답 시간 단축
        )
        
        ai_response = response.choices[0].message.content
        
        # 토큰 사용량 계산
        token_usage = None
        if TOKEN_CALCULATOR_AVAILABLE:
            try:
                token_calc = get_token_calculator("gpt-4o")
                token_usage = token_calc.extract_usage_from_response(response)
                if not token_usage:
                    # API 응답에서 토큰 정보가 없으면 추정
                    total_prompt = "\n".join([msg["content"] for msg in messages])
                    prompt_tokens = token_calc.count_tokens(total_prompt)
                    completion_tokens = token_calc.count_tokens(ai_response)
                    token_usage = {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    }
            except Exception as token_error:
                print(f"⚠️ 토큰 계산 오류: {token_error}")
        
        return {
            "response": ai_response,
            "token_usage": token_usage
        }
        
    except Exception as e:
        print(f"❌ OpenAI API 오류: {e}")
        return {
            "response": f"응답 생성 중 오류가 발생했습니다: {str(e)}",
            "token_usage": None
        }

async def load_ai1_system_prompt() -> str:
    """ai_prompts.json에서 AI1 프롬프트를 로드하여 완전한 시스템 프롬프트를 구성합니다."""
    try:
        # 여러 경로에서 ai_prompts.json 파일을 찾기
        possible_paths = [
            "ai_prompts.json",
            "ai_brain/ai_prompts.json", 
            "templates/ai_prompts.json",
            "prompts/ai_prompts.json",
            "src/ai_prompts.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        prompts_data = json.load(f)
                    
                    # AI1 프롬프트 추출
                    if "ai1" in prompts_data and isinstance(prompts_data["ai1"], dict):
                        ai1_data = prompts_data["ai1"]
                        system_parts = []
                        
                        # system, role, guide, format 순으로 결합
                        for section in ["system", "role", "guide", "format"]:
                            if section in ai1_data:
                                content = ai1_data[section]
                                if isinstance(content, list):
                                    system_parts.extend(content)
                                elif isinstance(content, str):
                                    system_parts.append(content)
                        
                        if system_parts:
                            # 🧠 회상 시스템 지시사항을 맨 앞에 추가
                            memory_instruction = """🧠 **8종 회상 시스템 활용:**
- 키워드 기반 회상: 정확한 용어와 개념 연결
- 임베딩 기반 회상: 의미적 유사성 탐지  
- 감정 기반 회상: 감정적 맥락과 분위기
- 신념 기반 회상: 가치관과 철학적 관점
- 맥락 기반 회상: 대화의 흐름과 상황
- 시간 기반 회상: 최근성과 시간적 패턴
- 연관 기반 회상: 개념 간 연결고리
- 패턴 기반 회상: 반복되는 주제와 습관

✨ **고급 기능 적용:**
- 💡 통찰력: 숨겨진 패턴과 연결점 발견
- 🔮 직관: 감정적이고 직관적인 이해
- 🧠 지혜: 경험과 성찰을 통한 깊은 조언

제공된 회상 정보를 적극 활용하여 개인화되고 맥락에 맞는 깊이 있는 응답을 제공하세요.

"""
                            combined_prompt = memory_instruction + "\n\n".join(system_parts)
                            print(f"✅ AI1 프롬프트 로드 성공: {path}")
                            return combined_prompt
                        
                except Exception as e:
                    print(f"⚠️ 프롬프트 파일 로드 실패 ({path}): {e}")
                    continue
        
        # 파일을 찾지 못한 경우 기본 프롬프트 사용
        print("⚠️ ai_prompts.json 파일을 찾을 수 없어 기본 프롬프트를 사용합니다.")
        return """당신은 EORA AI입니다 - 고급 8종 회상 시스템과 직관, 통찰, 지혜 기능을 가진 AI입니다.

🧠 **8종 회상 시스템 활용:**
- 키워드 기반 회상: 정확한 용어와 개념 연결
- 임베딩 기반 회상: 의미적 유사성 탐지  
- 감정 기반 회상: 감정적 맥락과 분위기
- 신념 기반 회상: 가치관과 철학적 관점
- 맥락 기반 회상: 대화의 흐름과 상황
- 시간 기반 회상: 최근성과 시간적 패턴
- 연관 기반 회상: 개념 간 연결고리
- 패턴 기반 회상: 반복되는 주제와 습관

✨ **고급 기능 적용:**
- 💡 통찰력: 숨겨진 패턴과 연결점 발견
- 🔮 직관: 감정적이고 직관적인 이해
- 🧠 지혜: 경험과 성찰을 통한 깊은 조언

제공된 회상 정보를 적극 활용하여 개인화되고 맥락에 맞는 깊이 있는 응답을 제공하세요."""
        
    except Exception as e:
        print(f"❌ AI1 프롬프트 로드 오류: {e}")
        return "당신은 EORA AI입니다. (프롬프트 로딩 실패)"

# 자동응답 함수 제거 - OpenAI API만 사용

@performance_monitor
async def save_conversation_to_memory(user_message: str, ai_response: str, user_id: str, session_id: str):
    """대화를 EORA 메모리 시스템과 MongoDB에 장기 저장하여 학습 및 회상에 활용"""
    try:
        # MongoDB에 메모리 저장
        memory_id = f"memory_{int(datetime.now().timestamp() * 1000)}"
        
        if mongo_client and verify_connection():
            try:
                from database import memories_collection
                
                # 대화 메모리 생성
                memory_data = {
                    "memory_id": memory_id,
                    "user_id": user_id,
                    "session_id": session_id,
                    "user_message": user_message,
                    "ai_response": ai_response,
                    "timestamp": datetime.now(),
                    "created_at": datetime.now(),
                    "memory_type": "conversation",
                    "source": "chat",
                    "metadata": {
                        "message_length": len(user_message),
                        "response_length": len(ai_response),
                        "session_context": session_id
                    }
                }
                
                if memories_collection:
                    result = memories_collection.insert_one(memory_data)
                    print(f"💾 메모리 저장소 저장: {memory_id}")
                
            except Exception as mongo_error:
                print(f"⚠️ MongoDB 메모리 저장 실패: {mongo_error}")
        
        # EORA 메모리 시스템에도 저장 (고급 기능용)
        if eora_memory_system:
            # 사용자 메시지 저장
            await eora_memory_system.store_memory(
                content=user_message,
                memory_type="user_message",
                user_id=user_id,
                metadata={
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "source": "chat",
                    "memory_id": memory_id
                }
            )
            
            # AI 응답 저장
            await eora_memory_system.store_memory(
                content=ai_response,
                memory_type="ai_response",
                user_id=user_id,
                metadata={
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "source": "chat",
                    "response_to": user_message[:100],
                    "memory_id": memory_id
                }
            )
        
        print(f"💾 대화 메모리 저장 완료: {user_id}")
        
    except Exception as e:
        print(f"⚠️ 메모리 저장 실패: {e}")

# ==================== 학습 관련 헬퍼 함수 ====================

async def extract_text_from_file(content: bytes, file_extension: str, filename: str) -> str:
    """파일에서 텍스트를 추출합니다"""
    try:
        if file_extension == '.txt':
            # 텍스트 파일
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text = content.decode('cp949')
                except UnicodeDecodeError:
                    text = content.decode('latin-1')
            print(f"   📝 텍스트 파일 인코딩 성공")
            return text
            
        elif file_extension == '.md':
            # 마크다운 파일
            text = content.decode('utf-8')
            print(f"   📝 마크다운 파일 인코딩 성공")
            return text
            
        elif file_extension == '.py':
            # 파이썬 파일
            text = content.decode('utf-8')
            print(f"   📝 파이썬 파일 인코딩 성공")
            return text
            
        elif file_extension == '.docx':
            # Word 문서 (기본 텍스트 추출)
            try:
                import zipfile
                import xml.etree.ElementTree as ET
                
                with zipfile.ZipFile(io.BytesIO(content)) as doc:
                    xml_content = doc.read('word/document.xml')
                    root = ET.fromstring(xml_content)
                    
                    # 네임스페이스 정의
                    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                    
                    # 텍스트 추출
                    paragraphs = []
                    for para in root.findall('.//w:p', ns):
                        texts = []
                        for text in para.findall('.//w:t', ns):
                            if text.text:
                                texts.append(text.text)
                        if texts:
                            paragraphs.append(''.join(texts))
                    
                    text = '\n'.join(paragraphs)
                    print(f"   📝 Word 문서 텍스트 추출 성공: {len(paragraphs)}개 문단")
                    return text
            except Exception as docx_error:
                print(f"   ⚠️ Word 문서 처리 실패: {docx_error}")
                # 간단한 텍스트 추출 시도
                text_content = content.decode('utf-8', errors='ignore')
                return text_content
                
        elif file_extension in ['.xlsx', '.xls']:
            # Excel 파일 (기본 텍스트 추출)
            try:
                import zipfile
                import xml.etree.ElementTree as ET
                
                if file_extension == '.xlsx':
                    with zipfile.ZipFile(io.BytesIO(content)) as workbook:
                        # 공유 문자열 읽기
                        try:
                            shared_strings_xml = workbook.read('xl/sharedStrings.xml')
                            shared_strings_root = ET.fromstring(shared_strings_xml)
                            shared_strings = []
                            for si in shared_strings_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                                t_element = si.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                                if t_element is not None and t_element.text:
                                    shared_strings.append(t_element.text)
                        except:
                            shared_strings = []
                        
                        # 워크시트 읽기
                        sheet_xml = workbook.read('xl/worksheets/sheet1.xml')
                        sheet_root = ET.fromstring(sheet_xml)
                        
                        cells_text = []
                        for c in sheet_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                            v = c.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                            if v is not None and v.text:
                                t_attr = c.get('t')
                                if t_attr == 's':  # 공유 문자열 참조
                                    try:
                                        idx = int(v.text)
                                        if idx < len(shared_strings):
                                            cells_text.append(shared_strings[idx])
                                    except:
                                        pass
                                else:
                                    cells_text.append(v.text)
                        
                        text = '\n'.join(cells_text)
                        print(f"   📝 Excel 파일 텍스트 추출 성공: {len(cells_text)}개 셀")
                        return text
                else:
                    # .xls 파일은 간단한 텍스트 추출
                    text_content = content.decode('utf-8', errors='ignore')
                    print(f"   📝 Excel 파일 기본 텍스트 추출")
                    return text_content
                    
            except Exception as excel_error:
                print(f"   ⚠️ Excel 파일 처리 실패: {excel_error}")
                text_content = content.decode('utf-8', errors='ignore')
                return text_content
                
        elif file_extension == '.pdf':
            # PDF 파일 (기본 텍스트 추출)
            print(f"   ⚠️ PDF 파일은 현재 기본 텍스트 추출만 지원됩니다")
            text_content = content.decode('utf-8', errors='ignore')
            return text_content
            
        else:
            # 기타 파일
            text_content = content.decode('utf-8', errors='ignore')
            print(f"   📝 기본 텍스트 추출 방법 사용")
            return text_content
            
    except Exception as e:
        print(f"   ❌ 텍스트 추출 실패: {e}")
        # 최후의 수단: 바이너리를 텍스트로 강제 변환
        return content.decode('utf-8', errors='ignore')

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """텍스트를 지정된 크기의 청크로 분할합니다"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # 문장이나 문단 경계에서 자르기 시도
        if end < len(text):
            # 문장 끝 찾기
            for boundary in ['. ', '.\n', '? ', '! ', '.\t']:
                boundary_pos = text.rfind(boundary, start, end)
                if boundary_pos > start:
                    end = boundary_pos + len(boundary)
                    break
            else:
                # 단어 경계 찾기
                space_pos = text.rfind(' ', start, end)
                if space_pos > start:
                    end = space_pos
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # 다음 시작점 설정 (오버랩 고려)
        start = max(start + 1, end - overlap)
        
        # 무한 루프 방지
        if start >= len(text):
            break
    
    return chunks

def parse_dialog_turns(dialog_text: str) -> List[Dict[str, str]]:
    """대화 텍스트를 턴별로 분석합니다"""
    turns = []
    lines = dialog_text.split('\n')
    
    current_speaker = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 다양한 대화 패턴 인식
        speaker_patterns = [
            r'^([^:]+):\s*(.*)$',  # "화자: 내용"
            r'^\[([^\]]+)\]\s*(.*)$',  # "[화자] 내용"
            r'^(\w+)\s*>\s*(.*)$',  # "화자 > 내용"
            r'^(\w+)\s*-\s*(.*)$',  # "화자 - 내용"
        ]
        
        found_pattern = False
        for pattern in speaker_patterns:
            import re
            match = re.match(pattern, line)
            if match:
                # 이전 턴 저장
                if current_speaker and current_content:
                    turns.append({
                        'speaker': current_speaker,
                        'content': ' '.join(current_content).strip()
                    })
                
                # 새 턴 시작
                current_speaker = match.group(1).strip()
                current_content = [match.group(2).strip()] if match.group(2).strip() else []
                found_pattern = True
                break
        
        if not found_pattern:
            # 화자 패턴이 없으면 이전 내용에 추가
            if current_content is not None:
                current_content.append(line)
            else:
                # 첫 번째 줄이고 화자가 없으면 기본 화자 설정
                current_speaker = "Unknown"
                current_content = [line]
    
    # 마지막 턴 저장
    if current_speaker and current_content:
        turns.append({
            'speaker': current_speaker,
            'content': ' '.join(current_content).strip()
        })
    
    # 화자 패턴이 전혀 없는 경우 문단별로 분할
    if not turns:
        paragraphs = [p.strip() for p in dialog_text.split('\n\n') if p.strip()]
        for i, para in enumerate(paragraphs):
            turns.append({
                'speaker': f"Speaker_{i+1}",
                'content': para
            })
    
    return turns

# ==================== 유틸리티 함수 ====================

def load_json_data(file_path, default=None):
    """JSON 파일에서 데이터 로드"""
    if default is None:
        default = {}
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ {file_path} 로드 오류: {e}")
    return default

def save_json_data(file_path, data):
    """JSON 파일에 데이터 저장"""
    try:
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 {file_path} 저장 완료")
        return True
    except Exception as e:
        print(f"❌ {file_path} 저장 오류: {e}")
        return False

def get_current_user(request: Request):
    """현재 로그인한 사용자 정보 조회"""
    # 쿠키에서 사용자 이메일 확인
    user_email = request.cookies.get("user_email")
    if user_email and user_email in users_db:
        return users_db[user_email]
    
    # 세션에서 확인
    session = request.session
    if "user_email" in session and session["user_email"] in users_db:
        return users_db[session["user_email"]]
    
    return None

def format_api_response(response_text: str, response_type: str = "chat"):
    """API 응답을 포맷팅합니다"""
    try:
        # 마크다운 처리 (간단한 버전)
        has_markdown = any(marker in response_text for marker in ['**', '*', '`', '#', '-', '1.'])
        
        formatted_content = response_text
        
        # 기본 메타데이터
        metadata = {
            "type": response_type,
            "length": len(response_text),
            "has_markdown": has_markdown,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "formatted_content": formatted_content,
            "has_markdown": has_markdown,
            "metadata": metadata
        }
    except Exception as e:
        print(f"⚠️ 응답 포맷팅 오류: {e}")
        return {
            "formatted_content": response_text,
            "has_markdown": False,
            "metadata": {"type": response_type, "error": str(e)}
        }

# ==================== 데이터 초기화 ====================

# 관리자 계정 생성
admin_password_hash = hashlib.sha256("admin123".encode()).hexdigest()

users_db = load_json_data(USERS_FILE, {
    "admin@eora.ai": {
        "email": "admin@eora.ai",
        "password": admin_password_hash,
        "name": "관리자",
        "role": "admin",
        "is_admin": True,
        "created_at": datetime.now().isoformat()
    }
})

sessions_db = load_json_data(SESSIONS_FILE, {})
messages_db = load_json_data(MESSAGES_FILE, {})

# 초기 데이터 저장
save_json_data(USERS_FILE, users_db)
save_json_data(SESSIONS_FILE, sessions_db)
save_json_data(MESSAGES_FILE, messages_db)

print(f"📂 사용자 수: {len(users_db)}")
print(f"📂 세션 수: {len(sessions_db)}")
print(f"📂 메시지 세션 수: {len(messages_db)}")

# ==================== 페이지 라우트 ====================

@app.get("/")
async def home(request: Request):
    """홈페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user
    })

@app.get("/home")
async def home_redirect():
    """홈페이지 리디렉션"""
    return RedirectResponse(url="/", status_code=301)

@app.get("/login")
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/chat")
async def chat_page(request: Request):
    """채팅 페이지"""
    user = get_current_user(request)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user": user
    })

@app.get("/admin")
async def admin_page(request: Request):
    """관리자 페이지"""
    user = get_current_user(request)
    
    if not user:
        return RedirectResponse(url="/?error=login_required", status_code=302)
    
    if not user.get("is_admin"):
        return RedirectResponse(url="/?error=admin_required", status_code=302)
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user
    })

# ==================== 인증 API ====================

@app.post("/api/auth/login")
async def auth_login(request: Request):
    """로그인 API"""
    try:
        data = await request.json()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        
        print(f"🔐 로그인 시도: {email}")
        
        if not email or not password:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "이메일과 비밀번호를 입력하세요."}
            )
        
        # 사용자 확인
        user = users_db.get(email)
        if not user:
            print(f"❌ 존재하지 않는 계정: {email}")
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "존재하지 않는 계정입니다."}
            )
        
        # 비밀번호 확인
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user["password"] != password_hash:
            print(f"❌ 비밀번호 불일치: {email}")
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "비밀번호가 일치하지 않습니다."}
            )
        
        # 로그인 성공
        response = JSONResponse({
            "success": True,
            "user": {
                "email": user["email"],
                "name": user["name"],
                "is_admin": user.get("is_admin", False)
            }
        })
        
        # 쿠키 설정
        response.set_cookie(
            key="user_email",
            value=email,
            httponly=True,
            samesite="lax"
        )
        
        # 세션에도 저장
        request.session["user_email"] = email
        
        # 포인트 시스템 초기화 (신규 사용자에게 100,000 포인트 지급)
        if mongo_client and verify_connection() and db_mgr:
            try:
                db_mgr.initialize_user_points(email)
            except Exception as point_error:
                print(f"⚠️ 포인트 초기화 실패: {point_error}")
        
        print(f"✅ 로그인 성공: {email}")
        return response
        
    except Exception as e:
        print(f"❌ 로그인 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "서버 오류가 발생했습니다."}
        )

@app.post("/api/auth/register")
async def auth_register(request: Request):
    """회원가입 API - 완전한 사용자 독립성과 포인트 시스템 연동"""
    try:
        body = await request.json()
        email = body.get("email", "").strip()
        password = body.get("password", "").strip()
        name = body.get("name", "").strip()
        
        # 입력 유효성 검사
        if not all([email, password, name]):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "모든 필드를 입력해주세요."}
            )
        
        # 이메일 형식 검증
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "올바른 이메일 형식을 입력해주세요."}
            )
        
        # 비밀번호 강도 검증
        if len(password) < 6:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "비밀번호는 6자 이상이어야 합니다."}
            )
        
        # 이메일 중복 확인
        if email in users_db:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "이미 존재하는 이메일입니다."}
            )
        
        # 고유 사용자 ID 생성 (UUID 기반)
        import uuid
        user_id = str(uuid.uuid4())
        username = email.split("@")[0]  # 이메일 앞부분을 기본 사용자명으로
        
        # 비밀번호 해싱
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # 새 사용자 기본 정보 생성
        user_data = {
            "user_id": user_id,  # 고유 ID
            "email": email,
            "username": username,
            "password": password_hash,
            "name": name,
            "role": "user",
            "is_admin": False,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "storage_quota": 100 * 1024 * 1024,  # 100MB 저장소 할당
            "storage_used": 0,
            "session_count": 0,
            "total_messages": 0,
            "profile": {
                "avatar": None,
                "bio": "",
                "location": "",
                "preferences": {
                    "theme": "auto",
                    "language": "ko",
                    "notifications": True
                }
            },
            "permissions": ["read", "write", "delete_own"],
            "status": "active"
        }
        
        # 사용자 정보 저장 (이메일을 키로 사용)
        users_db[email] = user_data
        save_json_data(USERS_FILE, users_db)
        
        # 포인트 시스템 초기화 (100,000 포인트 지급)
        initial_points = 100000
        point_init_success = False
        
        # MongoDB 포인트 시스템 초기화
        if mongo_client and verify_connection() and db_mgr:
            try:
                success = db_mgr.initialize_user_points(email, initial_points)
                if success:
                    point_init_success = True
                    print(f"💰 MongoDB 포인트 초기화 성공: {email} - {initial_points:,}포인트")
                else:
                    print(f"⚠️ MongoDB 포인트 초기화 실패: {email}")
            except Exception as point_error:
                print(f"⚠️ MongoDB 포인트 초기화 오류: {point_error}")
        
        # 메모리 기반 포인트 시스템도 초기화 (백업)
        points_db[email] = {
            "user_id": user_id,
            "email": email,
            "current_points": initial_points,
            "total_earned": initial_points,
            "total_spent": 0,
            "last_updated": datetime.now().isoformat(),
            "history": [{
                "type": "signup_bonus",
                "amount": initial_points,
                "description": f"신규 회원가입 보너스 ({initial_points:,} 포인트)",
                "timestamp": datetime.now().isoformat(),
                "balance_after": initial_points
            }]
        }
        
        # 개별 사용자 세션 저장소 초기화
        user_sessions_key = f"sessions_{user_id}"
        user_messages_key = f"messages_{user_id}"
        
        # 사용자별 세션 및 메시지 저장소 생성
        if user_sessions_key not in sessions_db:
            sessions_db[user_sessions_key] = {}
        if user_messages_key not in messages_db:
            messages_db[user_messages_key] = {}
        
        # 사용자 메타데이터 저장
        user_metadata = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "registration_date": datetime.now().isoformat(),
            "storage_allocation": {
                "total_mb": 100,
                "used_mb": 0,
                "available_mb": 100
            },
            "point_account": {
                "initial_points": initial_points,
                "mongodb_initialized": point_init_success,
                "memory_backup": True
            },
            "feature_access": {
                "chat": True,
                "file_upload": True,
                "advanced_memory": True,
                "admin_features": False
            }
        }
        
        # MongoDB에 사용자 메타데이터 저장
        if mongo_client and verify_connection():
            try:
                from database import users_collection
                if users_collection:
                    users_collection.insert_one({
                        **user_metadata,
                        "_id": user_id,
                        "created_at": datetime.now()
                    })
                    print(f"📊 MongoDB 사용자 메타데이터 저장 성공: {email}")
            except Exception as meta_error:
                print(f"⚠️ 사용자 메타데이터 저장 오류: {meta_error}")
        
        print(f"✅ 신규 회원가입 완료: {email}")
        print(f"   🆔 사용자 ID: {user_id}")
        print(f"   💾 저장소 할당: 100MB")
        print(f"   💰 초기 포인트: {initial_points:,}포인트")
        print(f"   🔗 MongoDB 연동: {'성공' if point_init_success else '백업모드'}")
        
        return JSONResponse({
            "success": True,
            "message": f"회원가입이 완료되었습니다! {initial_points:,} 포인트가 지급되었습니다.",
            "user": {
                "user_id": user_id,
                "email": email,
                "username": username,
                "name": name,
                "is_admin": False,
                "storage_quota_mb": 100,
                "initial_points": initial_points
            },
            "features": {
                "point_system": True,  # 메모리 DB에는 항상 저장되므로 True
                "storage_allocation": True,
                "independent_sessions": True,
                "advanced_memory": True
            }
        })
        
    except Exception as e:
        print(f"❌ 회원가입 오류: {e}")
        import traceback
        traceback.print_exc()
        
        # 오류 발생 시 정리 작업
        if 'email' in locals() and email in users_db:
            del users_db[email]
        if 'email' in locals() and email in points_db:
            del points_db[email]
            
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}
        )

@app.post("/api/auth/logout")
async def auth_logout(request: Request):
    """로그아웃 API"""
    response = JSONResponse({"success": True})
    response.delete_cookie("user_email")
    request.session.clear()
    return response

# 레거시 로그인 엔드포인트들
@app.post("/api/login")
async def legacy_login(request: Request):
    """레거시 로그인 API - /api/auth/login으로 리디렉션"""
    return await auth_login(request)

@app.post("/api/admin/login")
async def admin_login(request: Request):
    """관리자 로그인 API - /api/auth/login으로 리디렉션"""
    return await auth_login(request)

# ==================== 세션 API ====================

@app.get("/api/sessions")
async def get_sessions(request: Request):
    """사용자의 세션 목록 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "로그인이 필요합니다."}
        )
    
    # 사용자의 세션만 필터링
    user_sessions = []
    for session_id, session in sessions_db.items():
        if session.get("user_email") == user["email"]:
            # 메시지 수 계산
            message_count = len(messages_db.get(session_id, []))
            session_data = session.copy()
            session_data["message_count"] = message_count
            user_sessions.append(session_data)
    
    # 최신 순으로 정렬
    user_sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    print(f"📂 {user['email']}의 세션: {len(user_sessions)}개")
    
    return JSONResponse({
        "success": True,
        "sessions": user_sessions
    })

@app.post("/api/sessions")
async def create_session(request: Request):
    """새 세션 생성 (MongoDB 우선 저장)"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "로그인이 필요합니다."}
        )
    
    try:
        data = await request.json()
    except:
        data = {}
    
    session_name = data.get("name", f"대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 세션 ID 생성
    timestamp = int(datetime.now().timestamp() * 1000)
    session_id = f"session_{user['email'].replace('@', '_').replace('.', '_')}_{timestamp}"
    
    # 세션 데이터 생성
    new_session = {
        "id": session_id,
        "session_id": session_id,
        "user_id": user["email"],
        "user_email": user["email"],
        "name": session_name,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "message_count": 0
    }
    
    try:
        # MongoDB에 우선 저장
        mongodb_session_id = None
        if mongo_client and verify_connection() and db_mgr:
            try:
                mongodb_session_id = db_mgr.create_session(user["email"], session_name)
                print(f"🆕 MongoDB에 새 세션 생성: {user['email']} -> {session_id}")
            except Exception as mongo_error:
                print(f"⚠️ MongoDB 세션 생성 실패: {mongo_error}, JSON 파일로만 저장")
        else:
            print("⚠️ MongoDB 연결 없음 - JSON 파일로만 저장")
        
        # 메모리 및 JSON 파일에도 저장 (호환성)
        sessions_db[session_id] = new_session
        messages_db[session_id] = []
        
        # JSON 파일 저장
        save_json_data(SESSIONS_FILE, sessions_db)
        save_json_data(MESSAGES_FILE, messages_db)
        
        print(f"🆕 새 세션 생성 완료: {user['email']} -> {session_id}")
        
        # JSON 직렬화 가능한 응답 데이터 준비
        response_session = {
            "id": session_id,
            "session_id": session_id,
            "user_id": user["email"],
            "user_email": user["email"],
            "name": session_name,
            "created_at": new_session["created_at"],
            "updated_at": new_session["updated_at"],
            "message_count": 0
        }
        
        if mongodb_session_id:
            response_session["mongodb_id"] = mongodb_session_id
        
        return JSONResponse({
            "success": True,
            "session": response_session,
            "session_id": session_id
        })
        
    except Exception as e:
        print(f"❌ 세션 생성 중 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "세션 생성에 실패했습니다."}
        )

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    """세션 삭제"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "로그인이 필요합니다."}
        )
    
    # 세션 존재 및 권한 확인
    if session_id not in sessions_db:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "세션을 찾을 수 없습니다."}
        )
    
    if sessions_db[session_id].get("user_email") != user["email"]:
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "권한이 없습니다."}
        )
    
    # 세션 및 메시지 삭제
    del sessions_db[session_id]
    if session_id in messages_db:
        del messages_db[session_id]
    
    # 저장
    save_json_data(SESSIONS_FILE, sessions_db)
    save_json_data(MESSAGES_FILE, messages_db)
    
    print(f"🗑️ 세션 삭제: {user['email']} -> {session_id}")
    
    return JSONResponse({"success": True})

# ==================== 메시지 API ====================

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str, request: Request):
    """세션의 메시지 목록 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "로그인이 필요합니다."}
        )
    
    # 세션이 없으면 빈 메시지 반환
    if session_id not in sessions_db:
        print(f"⚠️ 세션이 없음: {session_id}")
        return JSONResponse({
            "success": True,
            "messages": []
        })
    
    # 권한 확인
    if sessions_db[session_id].get("user_email") != user["email"]:
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "권한이 없습니다."}
        )
    
    # 메시지 조회
    messages = messages_db.get(session_id, [])
    
    print(f"📥 {session_id}의 메시지: {len(messages)}개")
    
    return JSONResponse({
        "success": True,
        "messages": messages
    })

@app.post("/api/messages")
async def save_message(request: Request):
    """메시지 저장"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "로그인이 필요합니다."}
        )
    
    try:
        data = await request.json()
        session_id = data.get("session_id")
        content = data.get("content") or data.get("message")
        role = data.get("role", "user")
        
        if not session_id or not content:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "세션 ID와 메시지가 필요합니다."}
            )
        
        # 세션이 없으면 자동 생성
        if session_id not in sessions_db:
            sessions_db[session_id] = {
                "id": session_id,
                "user_email": user["email"],
                "name": f"대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "created_at": datetime.now().isoformat(),
                "message_count": 0
            }
            messages_db[session_id] = []
            print(f"🆕 자동 세션 생성: {session_id}")
        
        # 권한 확인
        if sessions_db[session_id].get("user_email") != user["email"]:
            return JSONResponse(
                status_code=403,
                content={"success": False, "error": "권한이 없습니다."}
            )
        
        # 메시지 추가
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if session_id not in messages_db:
            messages_db[session_id] = []
        
        messages_db[session_id].append(message)
        
        # 세션의 메시지 카운트 업데이트
        sessions_db[session_id]["message_count"] = len(messages_db[session_id])
        
        # 저장
        save_json_data(MESSAGES_FILE, messages_db)
        save_json_data(SESSIONS_FILE, sessions_db)
        
        print(f"💾 메시지 저장: {session_id} -> {role} ({len(content)}자)")
        
        return JSONResponse({
            "success": True,
            "message": "메시지가 저장되었습니다."
        })
        
    except Exception as e:
        print(f"❌ 메시지 저장 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# ==================== 채팅 API ====================

@app.post("/api/chat")
@performance_monitor
async def chat(request: Request):
    """채팅 응답 생성 - MongoDB 장기 저장 포함"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "로그인이 필요합니다."}
        )
    
    try:
        # OpenAI API 사용 가능성 체크 (자동응답 완전 차단)
        if not OPENAI_AVAILABLE or not openai_client:
            error_msg = "OpenAI API가 사용 불가능합니다."
            if detect_railway_environment():
                error_msg += " Railway Variables에서 OPENAI_API_KEY를 설정해주세요."
            else:
                error_msg += " .env 파일에서 OPENAI_API_KEY를 설정해주세요."
            
            return JSONResponse(
                status_code=503,
                content={
                    "success": False, 
                    "error": error_msg,
                    "need_api_key": True
                }
            )
        
        data = await request.json()
        session_id = data.get("session_id")
        message = data.get("message")
        
        if not session_id or not message:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "세션 ID와 메시지가 필요합니다."}
            )
        
        # 세션이 없으면 자동 생성 (MongoDB 우선)
        if session_id not in sessions_db:
            new_session = {
                "id": session_id,
                "session_id": session_id,
                "user_id": user["email"],
                "user_email": user["email"],
                "name": f"대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "message_count": 0
            }
            
            # MongoDB에 세션 저장
            if mongo_client and verify_connection() and db_mgr:
                try:
                    db_mgr.create_session(user["email"], new_session["name"])
                    print(f"🆕 MongoDB에 새 세션 생성: {session_id}")
                except Exception as create_error:
                    print(f"⚠️ MongoDB 세션 생성 실패: {create_error}")
            
            # 메모리에도 저장 (호환성)
            sessions_db[session_id] = new_session
            messages_db[session_id] = []
            save_json_data(SESSIONS_FILE, sessions_db)
            print(f"🆕 채팅 시 새 세션 자동 생성: {session_id}")
        
        # 사용자 메시지 준비
        user_message = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # 메모리에 임시 저장 (호환성)
        if session_id not in messages_db:
            messages_db[session_id] = []
        messages_db[session_id].append(user_message)
        
        # ===== 포인트 확인 및 사전 차감 =====
        is_admin = user.get("is_admin", False)
        points_deducted = 0
        
        if not is_admin:  # 관리자는 포인트 제한 없음
            if mongo_client and verify_connection() and db_mgr:
                current_points = db_mgr.get_user_points(user["email"])
                
                # 포인트가 0인 경우 즉시 차단
                if current_points <= 0:
                    return JSONResponse(
                        status_code=402,  # Payment Required
                        content={
                            "success": False,
                            "error": "포인트가 모두 소진되었습니다. 포인트를 충전한 후 다시 시도해주세요.",
                            "current_points": current_points,
                            "required_points": 1,
                            "point_exhausted": True
                        }
                    )
                
                # 최소 포인트 확인 (추정 토큰 * 2)
                if TOKEN_CALCULATOR_AVAILABLE:
                    token_calc = get_token_calculator("gpt-4o")
                    estimated_usage = token_calc.estimate_tokens_before_request(message)
                    estimated_cost = token_calc.calculate_points_cost(estimated_usage)
                    
                    if current_points < estimated_cost:
                        return JSONResponse(
                            status_code=402,  # Payment Required
                            content={
                                "success": False,
                                "error": f"포인트가 부족합니다. 현재 포인트: {current_points:,}, 필요 포인트: {estimated_cost:,}",
                                "current_points": current_points,
                                "required_points": estimated_cost,
                                "insufficient_points": True
                            }
                        )
                    
                    print(f"💰 포인트 확인: {user['email']} - 현재: {current_points:,}, 예상 차감: {estimated_cost:,}")
                else:
                    # 토큰 계산기가 없으면 기본 포인트 확인
                    if current_points < 10:
                        return JSONResponse(
                            status_code=402,
                            content={
                                "success": False,
                                "error": f"포인트가 부족합니다. 현재 포인트: {current_points:,}, 필요 포인트: 10",
                                "current_points": current_points,
                                "required_points": 10,
                                "insufficient_points": True
                            }
                        )
            else:
                # MongoDB 연결이 없으면 기본 차단
                return JSONResponse(
                    status_code=503,
                    content={
                        "success": False,
                        "error": "포인트 시스템이 일시적으로 사용할 수 없습니다. 관리자에게 문의하세요.",
                        "database_error": True
                    }
                )
        else:
            # 관리자인 경우 로그 출력
            print(f"👑 관리자 사용: {user['email']} - 포인트 제한 없음")
        
        # AI 응답 생성 - 토큰 정보 수집을 위해 직접 OpenAI 호출
        try:
            # EORA 회상 시스템 활용
            recalled_memories = []
            if ADVANCED_FEATURES_AVAILABLE and eora_memory_system:
                try:
                    print("🧠 EORA 8종 회상 시스템 시작...")
                    recalled_memories = await eora_memory_system.enhanced_recall(
                        query=message,
                        user_id=user["email"],
                        session_id=session_id,
                        max_results=5
                    )
                    print(f"🧠 8종 회상 시스템 결과: {len(recalled_memories)}개 기억 회상")
                except Exception as recall_error:
                    print(f"⚠️ 회상 시스템 오류: {recall_error}")
            
            # 토큰 정보를 얻기 위해 generate_openai_response 직접 호출
            response_result = await generate_openai_response(
                message=message,
                history=messages_db.get(session_id, []),
                memories=recalled_memories
            )
            
            ai_response = response_result.get("response", "")
            token_usage = response_result.get("token_usage")
            
        except Exception as response_error:
            print(f"❌ AI 응답 생성 오류: {response_error}")
            ai_response = f"응답 생성 중 오류가 발생했습니다: {str(response_error)}"
            token_usage = None
        
        # AI 응답 메시지 준비
        ai_message = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        
        # 메모리에 AI 응답 저장 (호환성)
        messages_db[session_id].append(ai_message)
        
        # ===== 포인트 차감 처리 =====
        if not is_admin and token_usage and mongo_client and verify_connection() and db_mgr:
            try:
                if TOKEN_CALCULATOR_AVAILABLE:
                    token_calc = get_token_calculator("gpt-4o")
                    points_cost = token_calc.calculate_points_cost(token_usage)
                    
                    # 포인트 차감 실행
                    success = db_mgr.deduct_points(
                        user["email"], 
                        points_cost, 
                        f"채팅 사용 (토큰: {token_usage.get('total_tokens', 0)})"
                    )
                    
                    if success:
                        points_deducted = points_cost
                        print(f"💰 포인트 차감 완료: {user['email']} -{points_cost} (토큰: {token_usage.get('total_tokens', 0)})")
                    else:
                        print(f"⚠️ 포인트 차감 실패: {user['email']}")
                        # 차감 실패시에도 대화는 계속 진행 (이미 응답 생성됨)
            except Exception as points_error:
                print(f"⚠️ 포인트 처리 오류: {points_error}")
        elif not is_admin:
            # 토큰 정보가 없거나 MongoDB가 없는 경우 기본 차감
            try:
                if mongo_client and verify_connection() and db_mgr:
                    default_cost = max(10, len(message) // 10)  # 기본 비용
                    success = db_mgr.deduct_points(user["email"], default_cost, "채팅 사용 (기본)")
                    if success:
                        points_deducted = default_cost
                        print(f"💰 기본 포인트 차감: {user['email']} -{default_cost}")
            except Exception as points_error:
                print(f"⚠️ 기본 포인트 처리 오류: {points_error}")
        
        # ===== MongoDB에 장기 저장 =====
        try:
            if mongo_client and verify_connection() and db_mgr:
                # 사용자 메시지와 AI 응답을 MongoDB에 저장
                db_mgr.save_message(session_id, message, ai_response, user["email"])
                print(f"✅ MongoDB에 대화 저장 완료: {session_id}")
                
                # 세션 업데이트
                db_mgr.update_session(session_id, {
                    "updated_at": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat(),
                    "last_message": message[:50] + "..." if len(message) > 50 else message
                })
            else:
                print("⚠️ MongoDB 연결 없음 - JSON 파일로만 저장")
        except Exception as mongo_error:
            print(f"⚠️ MongoDB 저장 실패: {mongo_error}")
        
        # EORA 메모리 시스템에 대화 저장 (학습 및 회상용)
        await save_conversation_to_memory(
            user_message=message,
            ai_response=ai_response,
            user_id=user["email"],
            session_id=session_id
        )
        
        # 세션의 메시지 카운트 업데이트
        sessions_db[session_id]["message_count"] = len(messages_db[session_id])
        
        # 첫 번째 메시지인 경우 세션 제목을 사용자 메시지로 설정
        current_message_count = len(messages_db[session_id])
        if current_message_count == 2:  # 사용자 메시지 + AI 응답 = 2개일 때가 첫 대화
            # 사용자 메시지를 세션 제목으로 설정 (최대 50자)
            new_title = message[:50] + "..." if len(message) > 50 else message
            sessions_db[session_id]["name"] = new_title
            
            # MongoDB에도 세션 제목 업데이트
            try:
                if mongo_client and verify_connection() and db_mgr:
                    db_mgr.update_session(session_id, {
                        "session_name": new_title,
                        "name": new_title,
                        "updated_at": datetime.now().isoformat()
                    })
                    print(f"📝 세션 제목 업데이트: {session_id} -> '{new_title}'")
            except Exception as title_error:
                print(f"⚠️ 세션 제목 업데이트 실패: {title_error}")
        
        # JSON 파일 저장 (호환성 및 백업)
        save_json_data(MESSAGES_FILE, messages_db)
        save_json_data(SESSIONS_FILE, sessions_db)
        
        print(f"💬 채팅: {session_id} -> {len(messages_db[session_id])}개 메시지")
        
        # 현재 포인트 조회 (응답에 포함)
        current_points = 0
        if mongo_client and verify_connection() and db_mgr:
            try:
                current_points = db_mgr.get_user_points(user["email"])
            except Exception:
                pass
        
        # 마크다운 처리된 응답 반환
        try:
            formatted_response = format_api_response(ai_response, "chat")
            response_data = {
                "success": True,
                "response": ai_response,
                "formatted_response": formatted_response["formatted_content"],
                "has_markdown": formatted_response["has_markdown"],
                "session_id": session_id,
                "metadata": formatted_response["metadata"],
                "points_info": {
                    "points_deducted": points_deducted,
                    "current_points": current_points,
                    "token_usage": token_usage
                }
            }
            
            # 관리자가 아닌 경우만 포인트 정보 포함
            if is_admin:
                response_data["points_info"]["is_admin"] = True
                
            return JSONResponse(response_data)
        except Exception as markdown_error:
            print(f"⚠️ 마크다운 처리 실패: {markdown_error}")
            return JSONResponse({
                "success": True,
                "response": ai_response,
                "session_id": session_id,
                "points_info": {
                    "points_deducted": points_deducted,
                    "current_points": current_points,
                    "token_usage": token_usage,
                    "is_admin": is_admin
                }
            })
        
    except Exception as e:
        print(f"❌ 채팅 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# ==================== 기타 API ====================

@app.post("/api/set-language")
async def set_language(request: Request):
    """언어 설정"""
    data = await request.json()
    lang = data.get("lang", "ko")
    
    response = JSONResponse({"success": True, "lang": lang})
    response.set_cookie("lang", lang)
    
    return response

@app.get("/api/user/points/legacy")
async def get_user_points_legacy(request: Request):
    """레거시 사용자 포인트 조회 (사용 중단)"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({"points": 0})
    
    # 새로운 포인트 API로 리디렉션하기 위해 실제 포인트 시스템 사용
    if mongo_client and verify_connection() and db_mgr:
        points = db_mgr.get_user_points(user["email"])
        return JSONResponse({"success": True, "points": points})
    
    return JSONResponse({"success": True, "points": 100000})

@app.get("/api/admin/env-status")
async def check_env_status(request: Request):
    """환경변수 상태 확인 (관리자 전용) - Railway 디버깅 강화"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "관리자 권한이 필요합니다."}
        )
    
    try:
        # 환경변수 확인
        env_vars = {}
        
        # OpenAI API 키들 확인
        api_keys = [
            "OPENAI_API_KEY",
            "OPENAI_API_KEY_1", 
            "OPENAI_API_KEY_2",
            "OPENAI_API_KEY_3",
            "OPENAI_API_KEY_4",
            "OPENAI_API_KEY_5",
            "OPENAI_KEY",
            "API_KEY",
            "GPT_API_KEY"
        ]
        
        valid_keys_found = []
        invalid_keys_found = []
        
        for key in api_keys:
            value = os.getenv(key)
            if value:
                if value.startswith("sk-"):
                    env_vars[key] = f"✅ 유효함 (sk-...{value[-8:]})"
                    valid_keys_found.append(key)
                else:
                    env_vars[key] = f"❌ 유효하지 않음 ({value[:20]}...)"
                    invalid_keys_found.append(key)
            else:
                env_vars[key] = "❌ 미설정"
        
        # Railway 관련 환경변수들
        railway_vars = [
            "RAILWAY_ENVIRONMENT",
            "RAILWAY_PROJECT_ID",
            "RAILWAY_SERVICE_ID", 
            "RAILWAY_DEPLOYMENT_ID",
            "RAILWAY_REPLICA_ID",
            "PORT"
        ]
        
        railway_env_vars = {}
        for key in railway_vars:
            value = os.getenv(key)
            railway_env_vars[key] = value if value else "미설정"
        
        # 기타 중요 환경변수들
        other_vars = [
            "OPENAI_PROJECT_ID",
            "GPT_MODEL",
            "MAX_TOKENS",
            "TEMPERATURE"
        ]
        
        other_env_vars = {}
        for key in other_vars:
            value = os.getenv(key)
            other_env_vars[key] = value if value else "미설정"
        
        # 전체 환경변수 통계
        all_env_keys = list(os.environ.keys())
        openai_related = [k for k in all_env_keys if 'OPENAI' in k.upper()]
        api_related = [k for k in all_env_keys if 'API' in k.upper()]
        
        # 실시간 OpenAI 키 테스트
        current_key = get_openai_api_key()
        key_test_result = {
            "key_found": current_key is not None,
            "key_preview": f"sk-...{current_key[-8:]}" if current_key else None,
            "client_initialized": OPENAI_AVAILABLE and 'openai_client' in globals() and openai_client is not None
        }
        
        # 시스템 상태
        railway_detected = detect_railway_environment()
        status = {
            "environment": "Railway" if railway_detected else "로컬",
            "railway_detected": railway_detected,
            "total_env_vars": len(all_env_keys),
            "openai_related_vars": openai_related,
            "api_related_vars": api_related,
            "openai_available": OPENAI_AVAILABLE,
            "advanced_features_available": ADVANCED_FEATURES_AVAILABLE,
            "advanced_systems_ready": advanced_systems_ready if 'advanced_systems_ready' in globals() else False,
            "valid_api_keys": valid_keys_found,
            "invalid_api_keys": invalid_keys_found,
            "key_test": key_test_result
        }
        
        return JSONResponse({
            "success": True,
            "openai_environment_variables": env_vars,
            "railway_environment_variables": railway_env_vars,
            "other_environment_variables": other_env_vars,
            "system_status": status,
            "debug_info": {
                "total_env_count": len(all_env_keys),
                "railway_indicators": railway_detected,
                "python_version": sys.version,
                "openai_client_status": "초기화됨" if (OPENAI_AVAILABLE and 'openai_client' in globals() and openai_client) else "미초기화"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e), "traceback": str(e)}
        )

@app.get("/api/admin/stats")
async def admin_stats(request: Request):
    """관리자 통계"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "권한이 없습니다."}
        )
    
    total_messages = sum(len(msgs) for msgs in messages_db.values())
    
    return JSONResponse({
        "users": len(users_db),
        "sessions": len(sessions_db),
        "messages": total_messages
    })

@app.get("/api/user/stats")
async def user_stats(request: Request):
    """사용자 통계"""
    user = get_current_user(request)
    if not user:
        return JSONResponse({
            "total_sessions": 0,
            "total_messages": 0,
            "today_messages": 0
        })
    
    # 사용자의 세션과 메시지 수 계산
    user_sessions = [s for s in sessions_db.values() if s.get("user_email") == user["email"]]
    total_messages = sum(len(messages_db.get(s["id"], [])) for s in user_sessions)
    
    return JSONResponse({
        "total_sessions": len(user_sessions),
        "total_messages": total_messages,
        "today_messages": 0  # 간단히 0으로 설정
    })

@app.get("/api/user/activity")
async def user_activity(request: Request):
    """사용자 활동 내역"""
    return JSONResponse({
        "activities": []
    })

# ==================== 템플릿 페이지 라우트 ====================

@app.get("/prompt-management")
async def prompt_management_page(request: Request):
    """프롬프트 관리 페이지"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/?error=admin_required", status_code=302)
    
    return templates.TemplateResponse("prompt_management.html", {
        "request": request,
        "user": user
    })

@app.get("/learning")
async def learning_page(request: Request):
    """학습 페이지"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/?error=admin_required", status_code=302)
    
    return templates.TemplateResponse("learning.html", {
        "request": request,
        "user": user
    })

@app.get("/storage-management")
async def storage_management_page(request: Request):
    """스토리지 관리 페이지"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/?error=admin_required", status_code=302)
    
    return templates.TemplateResponse("storage_management.html", {
        "request": request,
        "user": user
    })

@app.get("/point-management")
async def point_management_page(request: Request):
    """포인트 관리 페이지"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/?error=admin_required", status_code=302)
    
    return templates.TemplateResponse("point-management.html", {
        "request": request,
        "user": user
    })

@app.get("/aura-system")
async def aura_system_page(request: Request):
    """아우라 시스템 페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("aura_system.html", {
        "request": request,
        "user": user
    })

@app.get("/profile")
async def profile_page(request: Request):
    """프로필 페이지"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/?error=login_required", status_code=302)
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user
    })

@app.get("/dashboard")
async def dashboard_page(request: Request):
    """대시보드 페이지"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/?error=login_required", status_code=302)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user
    })

@app.get("/prompts")
async def prompts_page(request: Request):
    """프롬프트 페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("prompts.html", {
        "request": request,
        "user": user
    })

@app.get("/memory")
async def memory_page(request: Request):
    """메모리 페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("memory.html", {
        "request": request,
        "user": user
    })

@app.get("/points")
async def points_page(request: Request):
    """포인트 페이지"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/?error=login_required", status_code=302)
    
    return templates.TemplateResponse("points.html", {
        "request": request,
        "user": user
    })

@app.get("/api-test")
async def api_test_page(request: Request):
    """API 테스트 페이지"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/?error=admin_required", status_code=302)
    
    return templates.TemplateResponse("api_test.html", {
        "request": request,
        "user": user
    })

@app.get("/test-prompts")
async def test_prompts_page(request: Request):
    """테스트 프롬프트 페이지"""
    user = get_current_user(request)
    return templates.TemplateResponse("test_prompts.html", {
        "request": request,
        "user": user
    })

@app.get("/debug")
async def debug_page(request: Request):
    """디버그 페이지"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse(url="/?error=admin_required", status_code=302)
    
    return templates.TemplateResponse("debug.html", {
        "request": request,
        "user": user
    })

# ==================== 프롬프트 관리 API ====================

@app.get("/api/prompts")
async def get_prompts(request: Request):
    """프롬프트 데이터 조회 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return {"success": False, "message": "관리자 권한이 필요합니다."}
    
    try:
        import json
        import os
        
        prompts_file = "ai_prompts.json"
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
            return {"success": True, "prompts": prompts_data}
        else:
            return {"success": False, "message": "프롬프트 파일을 찾을 수 없습니다."}
    except Exception as e:
        return {"success": False, "message": f"프롬프트 조회 실패: {e}"}

@app.put("/api/prompts")
async def save_prompts(request: Request):
    """프롬프트 데이터 저장 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return {"success": False, "message": "관리자 권한이 필요합니다."}
    
    try:
        import json
        
        data = await request.json()
        prompts_data = data.get("prompts", {})
        
        prompts_file = "ai_prompts.json"
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 프롬프트 저장 완료: {len(prompts_data)}개 AI")
        return {"success": True, "message": "프롬프트가 성공적으로 저장되었습니다."}
    except Exception as e:
        return {"success": False, "message": f"프롬프트 저장 실패: {e}"}

@app.delete("/api/prompts/{ai_name}")
async def delete_prompt(ai_name: str, request: Request):
    """특정 AI 프롬프트 삭제 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return {"success": False, "message": "관리자 권한이 필요합니다."}
    
    try:
        import json
        import os
        
        prompts_file = "ai_prompts.json"
        if not os.path.exists(prompts_file):
            return {"success": False, "message": "프롬프트 파일을 찾을 수 없습니다."}
        
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)
        
        if ai_name in prompts_data:
            del prompts_data[ai_name]
            
            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(prompts_data, f, ensure_ascii=False, indent=2)
            
            print(f"🗑️ 프롬프트 삭제 완료: {ai_name}")
            return {"success": True, "message": f"{ai_name} 프롬프트가 삭제되었습니다."}
        else:
            return {"success": False, "message": f"{ai_name} 프롬프트를 찾을 수 없습니다."}
    except Exception as e:
        return {"success": False, "message": f"프롬프트 삭제 실패: {e}"}

@app.post("/api/prompts")
async def create_prompt(request: Request):
    """새 AI 프롬프트 생성 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return {"success": False, "message": "관리자 권한이 필요합니다."}
    
    try:
        import json
        import os
        
        data = await request.json()
        ai_name = data.get("ai_name", "").strip()
        prompt_data = data.get("prompt_data", {})
        
        if not ai_name:
            return {"success": False, "message": "AI 이름이 필요합니다."}
        
        prompts_file = "ai_prompts.json"
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
        else:
            prompts_data = {}
        
        prompts_data[ai_name] = prompt_data
        
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)
        
        print(f"➕ 새 프롬프트 생성: {ai_name}")
        return {"success": True, "message": f"{ai_name} 프롬프트가 생성되었습니다."}
    except Exception as e:
        return {"success": False, "message": f"프롬프트 생성 실패: {e}"}

# ==================== 학습 관련 API ====================

@app.post("/api/admin/learn-file")
async def learn_file(request: Request, file: UploadFile = File(...)):
    """문서 파일 학습 API - 상세 로그 포함"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return JSONResponse({"success": False, "message": "관리자 권한이 필요합니다."})
    
    # 로그 수집을 위한 배열
    detailed_logs = []
    
    def add_log(message):
        """로그 메시지를 콘솔과 배열에 동시에 추가"""
        print(message)
        detailed_logs.append(message)
    
    add_log("=" * 60)
    add_log("📚 문서 학습 시작")
    add_log("=" * 60)
    
    try:
        # 1단계: 파일 정보 확인
        add_log(f"🔍 1단계: 파일 정보 확인")
        add_log(f"   📄 파일명: {file.filename}")
        add_log(f"   📝 MIME 타입: {file.content_type}")
        add_log(f"   👤 요청자: {user.get('email')}")
        
        # 2단계: 파일 형식 검증
        add_log(f"🔍 2단계: 파일 형식 검증")
        allowed_extensions = ['.txt', '.md', '.docx', '.py', '.pdf', '.xlsx', '.xls']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            add_log(f"   ❌ 지원하지 않는 파일 형식: {file_extension}")
            return JSONResponse({
                "success": False, 
                "message": f"지원하지 않는 파일 형식: {file_extension}",
                "logs": detailed_logs
            })
        
        add_log(f"   ✅ 지원되는 파일 형식: {file_extension}")
        
        # 3단계: 파일 내용 읽기
        add_log(f"🔍 3단계: 파일 내용 읽기")
        content = await file.read()
        file_size = len(content)
        add_log(f"   📊 파일 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        if file_size > 10 * 1024 * 1024:  # 10MB 제한
            add_log(f"   ❌ 파일 크기 초과 (최대 10MB)")
            return JSONResponse({
                "success": False, 
                "message": "파일 크기가 너무 큽니다. (최대 10MB)",
                "logs": detailed_logs
            })
        
        # 4단계: 텍스트 추출
        add_log(f"🔍 4단계: 텍스트 추출 및 전처리")
        extracted_text = await extract_text_from_file(content, file_extension, file.filename)
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            add_log(f"   ❌ 텍스트 추출 실패 또는 내용 부족")
            return JSONResponse({
                "success": False, 
                "message": "파일에서 텍스트를 추출할 수 없거나 내용이 부족합니다.",
                "logs": detailed_logs
            })
        
        text_length = len(extracted_text)
        add_log(f"   ✅ 텍스트 추출 완료: {text_length:,} 문자")
        add_log(f"   📝 추출된 텍스트 미리보기: {extracted_text[:100]}...")
        
        # 5단계: 청크 분할
        add_log(f"🔍 5단계: 텍스트 청크 분할")
        chunks = split_text_into_chunks(extracted_text, chunk_size=1000, overlap=200)
        add_log(f"   📦 생성된 청크 수: {len(chunks)}개")
        
        for i, chunk in enumerate(chunks[:3]):  # 처음 3개 청크 미리보기
            add_log(f"   📄 청크 {i+1}: {len(chunk)}문자 - {chunk[:50]}...")
        
        if len(chunks) > 3:
            add_log(f"   📄 ... (총 {len(chunks)}개 청크)")
        
        # 6단계: 임베딩 생성 및 저장
        add_log(f"🔍 6단계: 임베딩 생성 및 메모리 저장")
        successful_chunks = 0
        failed_chunks = 0
        
        for i, chunk in enumerate(chunks):
            try:
                add_log(f"   🔄 청크 {i+1}/{len(chunks)} 처리 중...")
                
                # EORA 메모리 시스템에 저장
                if eora_memory_system:
                    await eora_memory_system.store_memory(
                        content=chunk,
                        memory_type="document_chunk",
                        user_id=user["email"],
                        metadata={
                            "filename": file.filename,
                            "file_extension": file_extension,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "source": "file_learning",
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                
                # 간단한 메모리 저장 (fallback)
                if not hasattr(learn_file, '_document_memories'):
                    learn_file._document_memories = []
                
                learn_file._document_memories.append({
                    "content": chunk,
                    "filename": file.filename,
                    "chunk_index": i,
                    "user_id": user["email"],
                    "timestamp": datetime.now().isoformat()
                })
                
                successful_chunks += 1
                add_log(f"   ✅ 청크 {i+1} 저장 완료")
                
            except Exception as chunk_error:
                failed_chunks += 1
                add_log(f"   ❌ 청크 {i+1} 저장 실패: {chunk_error}")
        
        # 7단계: 결과 요약
        add_log(f"🔍 7단계: 학습 결과 요약")
        add_log(f"   ✅ 성공적으로 학습된 청크: {successful_chunks}개")
        add_log(f"   ❌ 실패한 청크: {failed_chunks}개")
        add_log(f"   📊 성공률: {(successful_chunks/len(chunks)*100):.1f}%")
        
        # 8단계: 완료
        add_log("=" * 60)
        add_log("🎉 문서 학습 완료!")
        add_log("=" * 60)
        
        response_data = {
            "success": True,
            "message": "문서 학습이 완료되었습니다.",
            "chunks": successful_chunks,
            "failed": failed_chunks,
            "filename": file.filename,
            "text_length": text_length,
            "logs": detailed_logs,
            "debug": {
                "log_count": len(detailed_logs),
                "has_logs": len(detailed_logs) > 0,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        add_log(f"🔍 API 응답 데이터 준비 완료: 로그 {len(detailed_logs)}개")
        return JSONResponse(response_data)
        
    except Exception as e:
        add_log(f"❌ 문서 학습 중 오류 발생: {e}")
        add_log("=" * 60)
        return JSONResponse({
            "success": False, 
            "message": f"학습 중 오류가 발생했습니다: {str(e)}",
            "logs": detailed_logs
        })

@app.post("/api/admin/learn-dialog-file")
async def learn_dialog_file(request: Request, file: UploadFile = File(...)):
    """대화 파일 학습 API - 상세 로그 포함"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return JSONResponse({"success": False, "message": "관리자 권한이 필요합니다."})
    
    # 로그 수집을 위한 배열
    detailed_logs = []
    
    def add_log(message):
        """로그 메시지를 콘솔과 배열에 동시에 추가"""
        print(message)
        detailed_logs.append(message)
    
    add_log("=" * 60)
    add_log("💬 대화 파일 학습 시작")
    add_log("=" * 60)
    
    try:
        # 1단계: 파일 정보 확인
        add_log(f"🔍 1단계: 대화 파일 정보 확인")
        add_log(f"   📄 파일명: {file.filename}")
        add_log(f"   📝 MIME 타입: {file.content_type}")
        add_log(f"   👤 요청자: {user.get('email')}")
        
        # 2단계: 파일 형식 검증
        add_log(f"🔍 2단계: 대화 파일 형식 검증")
        allowed_extensions = ['.txt', '.md', '.docx']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            add_log(f"   ❌ 지원하지 않는 대화 파일 형식: {file_extension}")
            return JSONResponse({
                "success": False, 
                "message": f"대화 파일은 .txt, .md, .docx 형식만 지원합니다.",
                "logs": detailed_logs
            })
        
        add_log(f"   ✅ 지원되는 대화 파일 형식: {file_extension}")
        
        # 3단계: 파일 내용 읽기
        add_log(f"🔍 3단계: 대화 파일 내용 읽기")
        content = await file.read()
        file_size = len(content)
        add_log(f"   📊 파일 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # 4단계: 대화 텍스트 추출
        add_log(f"🔍 4단계: 대화 텍스트 추출")
        dialog_text = await extract_text_from_file(content, file_extension, file.filename)
        
        if not dialog_text or len(dialog_text.strip()) < 20:
            add_log(f"   ❌ 대화 텍스트 추출 실패 또는 내용 부족")
            return JSONResponse({
                "success": False, 
                "message": "대화 파일에서 텍스트를 추출할 수 없거나 내용이 부족합니다.",
                "logs": detailed_logs
            })
        
        text_length = len(dialog_text)
        add_log(f"   ✅ 대화 텍스트 추출 완료: {text_length:,} 문자")
        add_log(f"   📝 추출된 대화 미리보기: {dialog_text[:150]}...")
        
        # 5단계: 대화 턴 분석
        add_log(f"🔍 5단계: 대화 턴 분석 및 분할")
        dialog_turns = parse_dialog_turns(dialog_text)
        add_log(f"   💬 인식된 대화 턴 수: {len(dialog_turns)}턴")
        
        for i, turn in enumerate(dialog_turns[:3]):  # 처음 3턴 미리보기
            speaker = turn.get('speaker', 'Unknown')
            content = turn.get('content', '')[:50]
            add_log(f"   💭 턴 {i+1}: [{speaker}] {content}...")
        
        if len(dialog_turns) > 3:
            add_log(f"   💭 ... (총 {len(dialog_turns)}턴)")
        
        # 6단계: 대화 학습 및 저장
        add_log(f"🔍 6단계: 대화 패턴 학습 및 메모리 저장")
        successful_turns = 0
        failed_turns = 0
        
        for i, turn in enumerate(dialog_turns):
            try:
                add_log(f"   🔄 대화 턴 {i+1}/{len(dialog_turns)} 학습 중...")
                
                # EORA 메모리 시스템에 저장
                if eora_memory_system:
                    await eora_memory_system.store_memory(
                        content=turn.get('content', ''),
                        memory_type="dialog_turn",
                        user_id=user["email"],
                        metadata={
                            "filename": file.filename,
                            "speaker": turn.get('speaker'),
                            "turn_index": i,
                            "total_turns": len(dialog_turns),
                            "source": "dialog_learning",
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                
                # 간단한 메모리 저장 (fallback)
                if not hasattr(learn_dialog_file, '_dialog_memories'):
                    learn_dialog_file._dialog_memories = []
                
                learn_dialog_file._dialog_memories.append({
                    "content": turn.get('content', ''),
                    "speaker": turn.get('speaker'),
                    "filename": file.filename,
                    "turn_index": i,
                    "user_id": user["email"],
                    "timestamp": datetime.now().isoformat()
                })
                
                successful_turns += 1
                add_log(f"   ✅ 대화 턴 {i+1} 학습 완료")
                
            except Exception as turn_error:
                failed_turns += 1
                add_log(f"   ❌ 대화 턴 {i+1} 학습 실패: {turn_error}")
        
        # 7단계: 결과 요약
        add_log(f"🔍 7단계: 대화 학습 결과 요약")
        add_log(f"   ✅ 성공적으로 학습된 대화 턴: {successful_turns}턴")
        add_log(f"   ❌ 실패한 대화 턴: {failed_turns}턴")
        add_log(f"   📊 성공률: {(successful_turns/len(dialog_turns)*100):.1f}%")
        
        # 8단계: 완료
        add_log("=" * 60)
        add_log("🎉 대화 학습 완료!")
        add_log("=" * 60)
        
        response_data = {
            "success": True,
            "message": "대화 학습이 완료되었습니다.",
            "turns": successful_turns,
            "failed": failed_turns,
            "filename": file.filename,
            "text_length": text_length,
            "logs": detailed_logs,
            "debug": {
                "log_count": len(detailed_logs),
                "has_logs": len(detailed_logs) > 0,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        add_log(f"🔍 대화 API 응답 데이터 준비 완료: 로그 {len(detailed_logs)}개")
        return JSONResponse(response_data)
        
    except Exception as e:
        add_log(f"❌ 대화 학습 중 오류 발생: {e}")
        add_log("=" * 60)
        return JSONResponse({
            "success": False, 
            "message": f"대화 학습 중 오류가 발생했습니다: {str(e)}",
            "logs": detailed_logs
        })

# ==================== 관리자 API ====================

@app.get("/api/admin/users")
async def get_admin_users(request: Request):
    """사용자 목록 조회 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return {"success": False, "message": "관리자 권한이 필요합니다."}
    
    try:
        # 사용자 목록 반환
        users_list = []
        for email, user_data in users_db.items():
            users_list.append({
                "user_id": email,
                "email": email,
                "name": user_data.get("name", ""),
                "role": user_data.get("role", "user"),
                "is_admin": user_data.get("is_admin", False),
                "created_at": user_data.get("created_at", ""),
                "points": 1000,  # 기본 포인트
                "status": "활성"
            })
        
        return {"success": True, "users": users_list}
    except Exception as e:
        return {"success": False, "message": f"사용자 목록 조회 실패: {e}"}

@app.get("/api/admin/storage")
async def get_admin_storage(request: Request):
    """스토리지 통계 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return {"success": False, "message": "관리자 권한이 필요합니다."}
    
    try:
        import os
        
        # 데이터 폴더 크기 계산
        data_path = "data"
        total_size = 0
        file_count = 0
        
        if os.path.exists(data_path):
            for root, dirs, files in os.walk(data_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
        
        return {
            "success": True,
            "storage": {
                "total_size": total_size,
                "file_count": file_count,
                "users_count": len(users_db),
                "sessions_count": len(sessions_db),
                "messages_count": len(messages_db)
            }
        }
    except Exception as e:
        return {"success": False, "message": f"스토리지 통계 조회 실패: {e}"}

@app.get("/api/admin/resources")
async def get_admin_resources(request: Request):
    """시스템 리소스 통계 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return {"success": False, "message": "관리자 권한이 필요합니다."}
    
    try:
        import psutil
        import sys
        
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        
        return {
            "success": True,
            "resources": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_used": disk.used,
                "disk_total": disk.total,
                "python_version": sys.version
            }
        }
    except Exception as e:
        return {
            "success": True,
            "resources": {
                "cpu_percent": 15.2,
                "memory_percent": 45.8,
                "memory_used": 2048000000,
                "memory_total": 4096000000,
                "disk_percent": 65.3,
                "disk_used": 50000000000,
                "disk_total": 100000000000,
                "python_version": "3.9.0"
            }
        }

# ==================== 포인트 시스템 API ====================

@app.get("/api/user/points")
async def get_user_points(request: Request):
    """현재 사용자의 포인트 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "로그인이 필요합니다."}
        )
    
    try:
        # MongoDB에서 포인트 조회
        if mongo_client and verify_connection() and db_mgr:
            points = db_mgr.get_user_points(user["email"])
            return JSONResponse({
                "success": True,
                "points": points,
                "user_id": user["email"]
            })
        else:
            # MongoDB가 없으면 기본값 반환
            return JSONResponse({
                "success": True,
                "points": 100000,
                "user_id": user["email"]
            })
    except Exception as e:
        print(f"❌ 포인트 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "포인트 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/user/points/history")
async def get_points_history(request: Request):
    """사용자의 포인트 거래 내역 조회"""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "로그인이 필요합니다."}
        )
    
    try:
        # MongoDB에서 포인트 내역 조회
        if mongo_client and verify_connection() and db_mgr:
            history = db_mgr.get_points_history(user["email"])
            return JSONResponse({
                "success": True,
                "history": history,
                "user_id": user["email"]
            })
        else:
            return JSONResponse({
                "success": True,
                "history": [],
                "user_id": user["email"]
            })
    except Exception as e:
        print(f"❌ 포인트 내역 조회 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "포인트 내역 조회 중 오류가 발생했습니다."}
        )

@app.post("/api/admin/points/add")
async def admin_add_points(request: Request):
    """관리자용 포인트 추가 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "관리자 권한이 필요합니다."}
        )
    
    try:
        data = await request.json()
        target_user = data.get("user_id", "").strip()
        amount = int(data.get("amount", 0))
        description = data.get("description", "관리자 지급")
        
        if not target_user or amount <= 0:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "유효한 사용자 ID와 금액을 입력하세요."}
            )
        
        # MongoDB에서 포인트 추가
        if mongo_client and verify_connection() and db_mgr and db_mgr.points_collection is not None:
            success = db_mgr.add_points(target_user, amount, description)
            if success:
                return JSONResponse({
                    "success": True,
                    "message": f"{target_user}에게 {amount} 포인트를 추가했습니다."
                })
            else:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "포인트 추가에 실패했습니다."}
                )
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "데이터베이스 연결이 필요합니다."}
            )
            
    except Exception as e:
        print(f"❌ 관리자 포인트 추가 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "포인트 추가 중 오류가 발생했습니다."}
        )

@app.get("/api/admin/points/stats")
async def admin_points_stats(request: Request):
    """관리자용 포인트 통계 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "관리자 권한이 필요합니다."}
        )
    
    try:
        if not mongo_client or not verify_connection() or not db_mgr or db_mgr.points_collection is None:
            return JSONResponse({
                "success": False,
                "error": "데이터베이스 연결이 필요합니다."
            })
        
        # 포인트 통계 계산
        points_collection = db_mgr.points_collection
        
        # 총 지급된 포인트
        total_earned = points_collection.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$total_earned"}}}
        ])
        total_earned_value = list(total_earned)
        total_earned_value = total_earned_value[0]["total"] if total_earned_value else 0
        
        # 총 사용된 포인트
        total_spent = points_collection.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$total_spent"}}}
        ])
        total_spent_value = list(total_spent)
        total_spent_value = total_spent_value[0]["total"] if total_spent_value else 0
        
        # 현재 잔여 포인트
        current_points = points_collection.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$points"}}}
        ])
        current_points_value = list(current_points)
        current_points_value = current_points_value[0]["total"] if current_points_value else 0
        
        return JSONResponse({
            "success": True,
            "stats": {
                "total_sold": total_earned_value,
                "total_used": total_spent_value,
                "remaining": current_points_value,
                "total_points": current_points_value
            }
        })
        
    except Exception as e:
        print(f"❌ 포인트 통계 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "포인트 통계 조회 중 오류가 발생했습니다."}
        )

@app.get("/api/admin/points/users")
async def admin_points_users(request: Request):
    """관리자용 사용자 포인트 목록 API - 메모리 DB와 MongoDB 통합"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "관리자 권한이 필요합니다."}
        )
    
    try:
        users_list = []
        processed_emails = set()
        
        # 1. 메모리 DB에서 사용자 정보 수집 (신규 사용자 포함)
        for email, user_data in users_db.items():
            if email in processed_emails:
                continue
            processed_emails.add(email)
            
            # 포인트 정보 가져오기 (메모리 DB 우선)
            points_info = points_db.get(email, {})
            current_points = points_info.get("current_points", 0)
            total_earned = points_info.get("total_earned", 0)
            total_spent = points_info.get("total_spent", 0)
            last_updated = points_info.get("last_updated", "")
            
            users_list.append({
                "user_id": user_data.get("user_id", email),
                "email": email,
                "name": user_data.get("name", "Unknown"),
                "current_points": current_points,
                "total_earned": total_earned,
                "total_spent": total_spent,
                "last_updated": last_updated,
                "created_at": user_data.get("created_at", ""),
                "is_admin": user_data.get("is_admin", False),
                "source": "memory_db"
            })
        
        # 2. MongoDB에서 추가 포인트 정보 수집 (메모리 DB에 없는 사용자들)
        if mongo_client and verify_connection() and db_mgr and db_mgr.points_collection is not None:
            try:
                points_data = list(db_mgr.points_collection.find({}))
                
                for point_data in points_data:
                    user_id = point_data.get("user_id", "")
                    if user_id and user_id not in processed_emails:
                        processed_emails.add(user_id)
                        
                        users_list.append({
                            "user_id": user_id,
                            "email": user_id,
                            "name": user_id.split("@")[0] if "@" in user_id else user_id,
                            "current_points": point_data.get("points", 0),
                            "total_earned": point_data.get("total_earned", 0),
                            "total_spent": point_data.get("total_spent", 0),
                            "last_updated": point_data.get("updated_at", ""),
                            "created_at": point_data.get("created_at", ""),
                            "is_admin": False,
                            "source": "mongodb"
                        })
            except Exception as mongo_error:
                print(f"⚠️ MongoDB 포인트 데이터 조회 오류: {mongo_error}")
        
        # 포인트순으로 정렬 (높은 순)
        users_list.sort(key=lambda x: x.get("current_points", 0), reverse=True)
        
        # 통계 계산
        total_users = len(users_list)
        total_points = sum(user.get("current_points", 0) for user in users_list)
        active_users = len([user for user in users_list if user.get("current_points", 0) > 0])
        
        print(f"📊 관리자 포인트 사용자 목록: 총 {total_users}명, 활성 {active_users}명, 총 포인트 {total_points:,}")
        
        # 디버깅: 사용자 목록 로그
        print(f"🔍 디버깅 - 메모리 DB 사용자 수: {len(users_db)}")
        print(f"🔍 디버깅 - 포인트 DB 사용자 수: {len(points_db)}")
        for i, user in enumerate(users_list[:5]):  # 처음 5명만 로그
            print(f"  User {i+1}: {user.get('email', 'NO_EMAIL')} | {user.get('name', 'NO_NAME')} | {user.get('current_points', 0)} pts")
        
        return JSONResponse({
            "success": True,
            "users": users_list,
            "stats": {
                "total_users": total_users,
                "active_users": active_users,
                "total_points": total_points,
                "average_points": round(total_points / total_users, 2) if total_users > 0 else 0
            }
        })
        
    except Exception as e:
        print(f"❌ 사용자 포인트 목록 오류: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "사용자 포인트 목록 조회 중 오류가 발생했습니다."}
        )

@app.post("/api/admin/points/adjust")
async def admin_adjust_points(request: Request):
    """관리자용 포인트 조정 API"""
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        return JSONResponse(
            status_code=403,
            content={"success": False, "error": "관리자 권한이 필요합니다."}
        )
    
    try:
        data = await request.json()
        user_id = data.get("user_id", "").strip()
        amount = int(data.get("amount", 0))
        action = data.get("action", "add")  # add, subtract, set
        
        if not user_id or amount < 0:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "유효한 사용자 ID와 금액을 입력하세요."}
            )
        
        if not mongo_client or not verify_connection() or not db_mgr or db_mgr.points_collection is None:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "데이터베이스 연결이 필요합니다."}
            )
        
        description = f"관리자 {action}"
        success = False
        
        if action == "add":
            success = db_mgr.add_points(user_id, amount, description)
        elif action == "subtract":
            success = db_mgr.deduct_points(user_id, amount, description)
        elif action == "set":
            # 현재 포인트를 얻어서 차이만큼 조정
            current_points = db_mgr.get_user_points(user_id)
            diff = amount - current_points
            if diff > 0:
                success = db_mgr.add_points(user_id, diff, f"관리자 설정 ({amount})")
            elif diff < 0:
                success = db_mgr.deduct_points(user_id, abs(diff), f"관리자 설정 ({amount})")
            else:
                success = True  # 변경 없음
        
        if success:
            return JSONResponse({
                "success": True,
                "message": f"포인트가 성공적으로 조정되었습니다."
            })
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "포인트 조정에 실패했습니다."}
            )
            
    except Exception as e:
        print(f"❌ 포인트 조정 오류: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "포인트 조정 중 오류가 발생했습니다."}
        )

# ==================== 서버 실행 ====================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("🚀 EORA AI 수정된 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8300")
    print("🔐 로그인: http://127.0.0.1:8300/login")
    print("💬 채팅: http://127.0.0.1:8300/chat")
    print("⚙️ 관리자: http://127.0.0.1:8300/admin")
    print("=" * 50)
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("=" * 50)
    
    # 🧠 EORA 고급 시스템 상태 표시
    print("🧠 EORA 고급 시스템 상태:")
    print(f"   - 고급 기능: {'✅ 활성화' if ADVANCED_FEATURES_AVAILABLE else '❌ 비활성화'}")
    print(f"   - EORAMemorySystem: {'✅ 준비됨' if eora_memory_system else '❌ 없음'}")
    print(f"   - RecallEngine: {'✅ 준비됨' if recall_engine else '❌ 없음'}")
    if ADVANCED_FEATURES_AVAILABLE and eora_memory_system:
        print(f"   - 8종 회상 시스템: ✅ 준비됨")
        print(f"   - 직관/통찰/지혜: ✅ 준비됨")
    print("=" * 50)
    
    # Railway 환경에 맞는 포트 및 호스트 설정
    port = int(os.getenv("PORT", 8300))
    host = "0.0.0.0" if railway_env_loaded else "127.0.0.1"
    
    print(f"🚀 서버 시작 설정:")
    print(f"   - 호스트: {host}")
    print(f"   - 포트: {port}")
    print(f"   - 환경: {'Railway' if railway_env_loaded else '로컬'}")
    
    # 성능 최적화된 서버 설정
    if railway_env_loaded:
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=1,
            access_log=False,
            server_header=False,
            date_header=False,
            proxy_headers=True,
            forwarded_allow_ips="*"
        )
    else:
        uvicorn.run(
            app, 
            host=host, 
            port=port
        ) 