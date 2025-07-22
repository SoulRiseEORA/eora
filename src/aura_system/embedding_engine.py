# embedding_engine.py
# 경로: src/aura_system/embedding_engine.py

import sys, os
import time
from openai import OpenAI
from dotenv import load_dotenv
import asyncio
from typing import List
import logging

# 상위 경로에서 모듈 불러오기 가능하도록 경로 확장
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))

# 환경변수 로딩
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    # proxies 인수 제거 - httpx 0.28.1 호환성
)

# ✅ 임베딩 생성 함수
async def embed_text(text: str) -> List[float]:
    """텍스트 임베딩 생성
    
    Args:
        text (str): 임베딩할 텍스트
        
    Returns:
        List[float]: 임베딩 벡터
    """
    try:
        # 동기 함수를 비동기로 실행
        def create_embedding():
            try:
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"⚠️ 임베딩 생성 실패: {str(e)}")
                return None
                
        return await asyncio.to_thread(create_embedding)
    except Exception as e:
        logger.error(f"⚠️ 임베딩 생성 실패: {str(e)}")
        return None

# 테스트
if __name__ == "__main__":
    sample = "직감 기반 기억 구조에 대해 설명해줘."
    emb = embed_text(sample)
    print("✅ 임베딩 생성 완료:", emb[:5], "...")
