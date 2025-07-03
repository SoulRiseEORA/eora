import os
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일 로드
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)
logger.info(f"🔄 Loaded .env from: {env_path}")

# OpenAI API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
logger.info("✅ OpenAI API 키 로드 완료")

# 전역 클라이언트 인스턴스
_openai_client = None

async def get_openai_client():
    """OpenAI 클라이언트 초기화"""
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client

async def get_embeddings():
    """OpenAI 임베딩 모델 초기화"""
    return OpenAIEmbeddings()

async def get_vector_store(embeddings):
    """Chroma 벡터 스토어 초기화"""
    return Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    ) 

def init_openai():
    """환경 변수에서 OpenAI API 키 설정"""
    import openai
    import os
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("❌ OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")
