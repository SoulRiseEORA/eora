"""
ai_core/engines/__init__.py
- AI 엔진 초기화 및 관리
"""

import os
import sys
import json
import time
import redis
import asyncio
import logging
import threading
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# aura_system의 엔진들을 import
from aura_system.belief_engine import BeliefEngine
from aura_system.memory_engine import MemoryEngine
from aura_system.insight_engine import InsightEngine
from aura_system.consciousness_engine import ConsciousnessEngine

class GAI:
    """GAI 엔진 클래스"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """초기화
        
        Args:
            config (Optional[Dict[str, Any]]): 설정
        """
        self.config = config or {}
        self.engines = {}
        self.initialize_engines()
    
    def initialize_engines(self):
        """엔진 초기화"""
        try:
            # 엔진들을 지연 로딩으로 초기화
            self.engines = {
                'belief': None,
                'memory': None,
                'insight': None,
                'consciousness': None
            }
            logger.info("✅ GAI 엔진 초기화 완료")
        except Exception as e:
            logger.error(f"❌ GAI 엔진 초기화 실패: {str(e)}")
            raise
    
    def get_engine(self, engine_type: str):
        """엔진 가져오기
        
        Args:
            engine_type (str): 엔진 타입
            
        Returns:
            Optional[BaseEngine]: 엔진 인스턴스
        """
        try:
            if engine_type not in self.engines:
                raise ValueError(f"지원하지 않는 엔진 타입: {engine_type}")
            
            if self.engines[engine_type] is None:
                # 지연 로딩으로 엔진 초기화
                self.engines[engine_type] = get_engine(engine_type)
            
            return self.engines[engine_type]
        except Exception as e:
            logger.error(f"❌ 엔진 가져오기 실패: {str(e)}")
            return None
    
    async def analyze(self, engine_type: str, input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """분석 수행
        
        Args:
            engine_type (str): 엔진 타입
            input_data (str): 입력 데이터
            context (Optional[Dict[str, Any]]): 컨텍스트
            
        Returns:
            Dict[str, Any]: 분석 결과
        """
        try:
            engine = self.get_engine(engine_type)
            if engine is None:
                raise ValueError(f"엔진을 찾을 수 없음: {engine_type}")
            
            result = await engine.process(input_data, context)
            return result
        except Exception as e:
            logger.error(f"❌ 분석 실패: {str(e)}")
            return {"status": "error", "message": str(e)}

def get_engine(engine_type: str):
    """엔진 가져오기
    
    Args:
        engine_type (str): 엔진 타입
        
    Returns:
        Optional[BaseEngine]: 엔진 인스턴스
    """
    try:
        engines = {
            'belief': BeliefEngine,
            'memory': MemoryEngine,
            'insight': InsightEngine,
            'consciousness': ConsciousnessEngine
        }
        return engines.get(engine_type)()
    except Exception as e:
        logger.error(f"❌ 엔진 가져오기 실패: {str(e)}")
        return None

async def analyze(input_data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """분석 수행
    
    Args:
        input_data (str): 입력 데이터
        context (Optional[Dict[str, Any]]): 컨텍스트
        
    Returns:
        Dict[str, Any]: 분석 결과
    """
    try:
        result = {}
        engine_types = ['belief', 'memory', 'insight', 'consciousness']
        
        for engine_type in engine_types:
            engine = get_engine(engine_type)
            if engine:
                engine_result = await engine.process(input_data, context)
                result[engine_type] = engine_result
        
        return result
    except Exception as e:
        logger.error(f"❌ 분석 실패: {str(e)}")
        return {}

# FAISS 관련 함수들
def initialize_faiss():
    """FAISS 초기화
    
    Returns:
        Any: FAISS 인덱스
    """
    try:
        import faiss
        
        # 기본 FAISS 인덱스 생성
        dimension = 768  # 기본 임베딩 차원
        index = faiss.IndexFlatL2(dimension)
        
        logger.info("✅ FAISS 초기화 완료")
        return index
    except Exception as e:
        logger.error(f"❌ FAISS 초기화 실패: {str(e)}")
        return None

def create_faiss_index(dimension: int = 768) -> Any:
    """FAISS 인덱스 생성
    
    Args:
        dimension (int): 임베딩 차원
        
    Returns:
        Any: FAISS 인덱스
    """
    try:
        import faiss
        index = faiss.IndexFlatL2(dimension)
        logger.info(f"✅ FAISS 인덱스 생성 완료 (차원: {dimension})")
        return index
    except Exception as e:
        logger.error(f"❌ FAISS 인덱스 생성 실패: {str(e)}")
        return None

def search_faiss_index(index: Any, query_vector: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """FAISS 인덱스 검색
    
    Args:
        index (Any): FAISS 인덱스
        query_vector (np.ndarray): 쿼리 벡터
        k (int): 검색 결과 수
        
    Returns:
        Tuple[np.ndarray, np.ndarray]: (거리, 인덱스)
    """
    try:
        import faiss
        distances, indices = index.search(query_vector.reshape(1, -1), k)
        logger.info(f"✅ FAISS 검색 완료 (결과 수: {k})")
        return distances, indices
    except Exception as e:
        logger.error(f"❌ FAISS 검색 실패: {str(e)}")
        return np.array([]), np.array([])

def get_event_loop() -> asyncio.AbstractEventLoop:
    """이벤트 루프 가져오기
    
    Returns:
        asyncio.AbstractEventLoop: 이벤트 루프
    """
    try:
        loop = asyncio.get_event_loop()
        logger.info("✅ 이벤트 루프 가져오기 성공")
        return loop
    except Exception as e:
        logger.error(f"❌ 이벤트 루프 가져오기 실패: {str(e)}")
        return asyncio.new_event_loop()

def run_async(coro):
    """비동기 함수 실행
    
    Args:
        coro: 비동기 함수
        
    Returns:
        Any: 실행 결과
    """
    try:
        loop = get_event_loop()
        return loop.run_until_complete(coro)
    except Exception as e:
        logger.error(f"❌ 비동기 함수 실행 실패: {str(e)}")
        return None 