"""
resonance_engine.py
- 공명 엔진
- 텍스트 임베딩 및 공명도 계산
"""

import os
import json
import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime
import asyncio
import logging
from aura_system.vector_store import embed_text_async
from openai import OpenAI
from dotenv import load_dotenv
from tiktoken import encoding_for_model
from functools import lru_cache
from ai_core.engine_base import BaseEngine
from aura_system.emotion_analyzer import analyze_emotion
from aura_system.context_analyzer import analyze_context

load_dotenv()

logger = logging.getLogger(__name__)

# 토큰 계산을 위한 인코더 초기화
enc = encoding_for_model("gpt-3.5-turbo")

def embed_text(text: str) -> List[float]:
    """텍스트 임베딩 생성"""
    try:
        # 1. 토큰 수 제한
        tokens = enc.encode(text)
        if len(tokens) > 8000:
            text = enc.decode(tokens[:8000])
        
        # 2. 임베딩 생성
        api_key = os.getenv("OPENAI_API_KEY", "")
        client = OpenAI(
            api_key=api_key,
            # proxies 인수 제거 - httpx 0.28.1 호환성
        )
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        vector = response.data[0].embedding
        
        if not isinstance(vector, list):
            raise TypeError("⚠️ embed_text(): 반환값이 list가 아닙니다.")
        
        return vector
        
    except Exception as e:
        logger.error(f"⚠️ 텍스트 임베딩 실패: {str(e)}")
        return [0.0] * 1536

async def embed_text_async(text: str) -> List[float]:
    """비동기 텍스트 임베딩"""
    return await asyncio.to_thread(embed_text, text)

def calculate_resonance(embedding1: List[float], embedding2: List[float]) -> float:
    """두 임베딩 간의 공명도 계산"""
    try:
        # 1. 입력 검증
        if not embedding1 or not embedding2:
            return 0.0
        
        if len(embedding1) != len(embedding2):
            return 0.0
        
        # 2. numpy 배열로 변환
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # 3. 정규화
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)
        
        # 4. 코사인 유사도 계산
        similarity = np.dot(vec1_norm, vec2_norm)
        
        # 5. 결과 정규화 (0~1 범위)
        resonance = (similarity + 1) / 2
        
        return float(resonance)
        
    except Exception as e:
        logger.error(f"⚠️ 공명도 계산 실패: {str(e)}")
        return 0.0

async def estimate_emotion(text: str) -> str:
    """텍스트의 감정 추정
    
    Args:
        text (str): 분석할 텍스트
        
    Returns:
        str: 감정 레이블
    """
    try:
        client = OpenAI()
        
        # 동기 함수를 비동기로 실행
        def analyze_emotion():
            try:
                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "다음 텍스트의 감정을 분석해주세요. 기쁨, 슬픔, 분노, 두려움, 놀람, 혐오, 중립 중 하나로 답변해주세요."},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3,
                    max_tokens=10
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"⚠️ 감정 분석 실패: {str(e)}")
                return None
                
        return await asyncio.to_thread(analyze_emotion)
    except Exception as e:
        logger.error(f"⚠️ 감정 분석 실패: {str(e)}")
        return None

def extract_belief_vector(text: str) -> List[float]:
    """텍스트에서 신념 벡터 추출"""
    try:
        # 1. 임베딩 생성
        embedding = embed_text(text)
        
        # 2. 신념 벡터 추출 (임시 구현)
        # TODO: 실제 신념 벡터 추출 모델 구현
        belief_vector = embedding[:100]  # 임시로 임베딩의 일부 사용
        
        return belief_vector
        
    except Exception as e:
        logger.error(f"⚠️ 신념 벡터 추출 실패: {str(e)}")
        return [0.0] * 100

@lru_cache(maxsize=1000)
def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """두 텍스트 간의 의미적 유사도 계산"""
    try:
        # 1. 임베딩 생성
        embedding1 = embed_text(text1)
        embedding2 = embed_text(text2)
        
        # 2. 공명도 계산
        similarity = calculate_resonance(embedding1, embedding2)
        
        return similarity
        
    except Exception as e:
        logger.error(f"⚠️ 의미적 유사도 계산 실패: {str(e)}")
        return 0.0

async def calculate_semantic_similarity_async(text1: str, text2: str) -> float:
    """비동기 의미적 유사도 계산"""
    return await asyncio.to_thread(calculate_semantic_similarity, text1, text2)

class ResonanceEngine(BaseEngine):
    """공명 엔진 클래스"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.resonance_store = {}
        self.emotion_weights = {
            "joy": 1.2,
            "love": 1.2,
            "peace": 1.1,
            "gratitude": 1.1,
            "hope": 1.0,
            "neutral": 0.8,
            "sadness": 0.7,
            "anger": 0.6,
            "fear": 0.5
        }
        self._cache = {}
        self._cache_size = 1000
        self.resonance_threshold = 0.7
        logger.info("✅ ResonanceEngine 초기화 완료")

    async def process(self, 
                     input_data: str, 
                     context: Optional[Dict[str, Any]] = None,
                     emotion: Optional[Dict[str, Any]] = None,
                     belief: Optional[Dict[str, Any]] = None,
                     wisdom: Optional[Dict[str, Any]] = None,
                     eora: Optional[Dict[str, Any]] = None,
                     system: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """입력 처리
        
        Args:
            input_data (str): 입력 텍스트
            context (Dict[str, Any], optional): 문맥 정보
            emotion (Dict[str, Any], optional): 감정 정보
            belief (Dict[str, Any], optional): 신념 정보
            wisdom (Dict[str, Any], optional): 지혜 정보
            eora (Dict[str, Any], optional): 이오라 정보
            system (Dict[str, Any], optional): 시스템 정보
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        try:
            # 1. 텍스트 임베딩
            embedding = await embed_text_async(input_data)
            
            # 2. 감정 분석
            emotion_result = await analyze_emotion(input_data)
            
            # 3. 문맥 분석
            context_result = await analyze_context(input_data)
            
            # 4. 신념 벡터 추출
            belief_vector = await self.extract_belief_vector(input_data)
            
            # 5. 결과 구성
            result = {
                "embedding": embedding,
                "emotion": emotion_result,
                "context": context_result,
                "belief": belief_vector,
                "metadata": {
                    "emotion": emotion,
                    "belief": belief,
                    "wisdom": wisdom,
                    "eora": eora,
                    "system": system
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"⚠️ 입력 처리 실패: {str(e)}")
            return {
                "embedding": [0.0] * 1536,
                "emotion": None,
                "context": None,
                "belief": [0.0] * 100,
                "metadata": {
                    "emotion": emotion,
                    "belief": belief,
                    "wisdom": wisdom,
                    "eora": eora,
                    "system": system
                }
            }
    
    def add_resonance(self, key: str, resonance: Any) -> bool:
        """공명 데이터 추가
        
        Args:
            key (str): 키
            resonance (Any): 공명 데이터
            
        Returns:
            bool: 성공 여부
        """
        try:
            self.resonance_store[key] = resonance
            return True
        except Exception as e:
            logger.error(f"⚠️ 공명 데이터 추가 실패: {str(e)}")
            return False
    
    def get_resonance(self, key: str) -> Optional[Any]:
        """공명 데이터 조회
        
        Args:
            key (str): 키
            
        Returns:
            Any: 공명 데이터
        """
        return self.resonance_store.get(key)

    async def calculate_resonance(self, query_embedding: List[float], memory_embedding: List[float]) -> float:
        """공명 점수 계산"""
        try:
            if not memory_embedding:
                return 0.0
                
            # 코사인 유사도 계산
            similarity = np.dot(query_embedding, memory_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(memory_embedding)
            )
            
            # 점수 정규화 (0~1 범위)
            normalized_score = (similarity + 1) / 2
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"⚠️ 공명 점수 계산 실패: {str(e)}")
            return 0.0

    async def estimate_emotion(self, text: str) -> Tuple[str, float]:
        """감정 추정"""
        try:
            # 1. 텍스트 임베딩
            embedding = await embed_text_async(text)
            
            # 2. 감정 점수 계산
            emotion_scores = self._calculate_emotion_scores(embedding)
            
            # 3. 최고 점수 감정 선택
            max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            logger.info("✅ 감정 추정 완료")
            return max_emotion
            
        except Exception as e:
            logger.error(f"⚠️ 감정 추정 실패: {str(e)}")
            return "neutral", 0.5

    def _calculate_emotion_scores(self, embedding: List[float]) -> Dict[str, float]:
        """감정 점수 계산"""
        try:
            # 기본 감정 점수
            base_scores = {
                "joy": 0.3,
                "sadness": 0.2,
                "anger": 0.1,
                "fear": 0.1,
                "surprise": 0.1,
                "neutral": 0.2
            }
            
            # 임베딩 기반 조정
            for emotion in base_scores:
                base_scores[emotion] *= self.emotion_weights[emotion]
            
            # 정규화
            total = sum(base_scores.values())
            return {k: v/total for k, v in base_scores.items()}
            
        except Exception as e:
            logger.error(f"⚠️ 감정 점수 계산 실패: {str(e)}")
            return {"neutral": 1.0}

    async def extract_belief_vector(self, text: str) -> List[float]:
        """신념 벡터 추출"""
        try:
            # 1. 텍스트 임베딩
            embedding = await embed_text_async(text)
            
            # 2. 신념 벡터 생성
            belief_vector = self._generate_belief_vector(embedding)
            
            logger.info("✅ 신념 벡터 추출 완료")
            return belief_vector
            
        except Exception as e:
            logger.error(f"⚠️ 신념 벡터 추출 실패: {str(e)}")
            return [0.0] * 100

    def _generate_belief_vector(self, embedding: List[float]) -> List[float]:
        """신념 벡터 생성"""
        try:
            # 임시로 임베딩의 일부 사용
            return embedding[:100]
        except Exception as e:
            logger.error(f"⚠️ 신념 벡터 생성 실패: {str(e)}")
            return [0.0] * 100

    def find_resonant_memories(self, query: str, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """공명하는 메모리 찾기"""
        try:
            resonant_memories = []
            
            for memory in memories:
                resonance = self.calculate_resonance(query, memory.get('content', ''))
                if resonance >= self.resonance_threshold:
                    memory['resonance'] = resonance
                    resonant_memories.append(memory)
                    
            # 공명도 기준으로 정렬
            resonant_memories.sort(key=lambda x: x.get('resonance', 0), reverse=True)
            
            return resonant_memories
            
        except Exception as e:
            logger.error(f"⚠️ 공명 메모리 찾기 중 오류: {str(e)}")
            return []

def get_resonance_engine() -> ResonanceEngine:
    """ResonanceEngine 인스턴스 반환"""
    return ResonanceEngine()

if __name__ == "__main__":
    print("✅ Resonance Engine (감정지도 확장 포함) 로딩 완료")
