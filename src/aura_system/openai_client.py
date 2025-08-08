import os
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv

# langchain_community 안전 import
try:
    from langchain_community.vectorstores import Chroma
    CHROMA_AVAILABLE = True
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ langchain_community 모듈을 찾을 수 없습니다. Chroma 기능이 비활성화됩니다.")
    CHROMA_AVAILABLE = False
    Chroma = None

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일 로드 (지연 초기화)
def load_env_if_needed():
    """필요할 때만 .env 파일을 로드합니다."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_path)
    logger.info(f"🔄 Loaded .env from: {env_path}")

def get_api_key():
    """API 키를 안전하게 가져옵니다."""
    load_env_if_needed()
    
    # 여러 가능한 환경변수 이름 시도
    possible_keys = [
        "OPENAI_API_KEY",
        "OPENAI_API_KEY_1", 
        "OPENAI_API_KEY_2",
        "OPENAI_API_KEY_3",
        "OPENAI_API_KEY_4",
        "OPENAI_API_KEY_5"
    ]
    
    for key_name in possible_keys:
        key_value = os.getenv(key_name)
        if key_value and key_value.startswith("sk-") and len(key_value) > 50:
            logger.info(f"✅ OpenAI API 키 발견: {key_name}")
            return key_value
    
    logger.warning("⚠️ OpenAI API 키를 찾을 수 없습니다.")
    return None

# 전역 클라이언트 인스턴스
_openai_client = None

async def get_openai_client():
    """OpenAI 클라이언트 초기화"""
    global _openai_client
    if _openai_client is None:
        api_key = get_api_key()
        if not api_key:
            logger.error("❌ OpenAI API 키를 찾을 수 없어 클라이언트를 초기화할 수 없습니다.")
            return None
        _openai_client = AsyncOpenAI(
            api_key=api_key,
            # proxies 인수 제거 - httpx 0.28.1 호환성
        )
        logger.info("✅ OpenAI 클라이언트 초기화 완료")
    return _openai_client

async def get_embeddings():
    """OpenAI 임베딩 모델 초기화 (직접 사용)"""
    api_key = get_api_key()
    if not api_key:
        logger.error("❌ OpenAI API 키를 찾을 수 없어 임베딩 클라이언트를 초기화할 수 없습니다.")
        return None
    return AsyncOpenAI(
        api_key=api_key,
        # proxies 인수 제거 - httpx 0.28.1 호환성
    )

async def get_vector_store(embeddings):
    """Chroma 벡터 스토어 초기화"""
    if CHROMA_AVAILABLE and Chroma:
        try:
            return Chroma(
                persist_directory="./chroma_db",
                embedding_function=embeddings
            )
        except Exception as e:
            logger.warning(f"⚠️ Chroma 벡터 스토어 초기화 실패: {e}")
            return None
    else:
        logger.warning("⚠️ Chroma 모듈이 사용할 수 없습니다.")
        return None 

def init_openai():
    """환경 변수에서 OpenAI API 키 설정"""
    import openai
    import os
    
    # 여러 API 키 중 하나 사용
    api_key = get_api_key()
    if api_key:
        openai.api_key = api_key
        logger.info("✅ OpenAI API 키 설정 완료")
    else:
        logger.warning("⚠️ OpenAI API 키를 찾을 수 없습니다. 일부 기능이 제한됩니다.")
        openai.api_key = None
