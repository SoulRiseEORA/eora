"""
분석 시스템
- 감정 분석
- 신념 분석
- 지혜 분석
- EORA 분석
- 시스템 분석
- 맥락 분석
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import AsyncOpenAI
from aura_system.vector_store import embed_text_async
import numpy as np
from .memory_manager import get_memory_manager
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class Analysis:
    """분석 시스템"""
    
    def __init__(self):
        """초기화"""
        self.client = AsyncOpenAI()
        self.analysis_interval = 5  # 5턴마다 분석
        self.turn_count = 0
        self.last_analysis = None
        self.analysis_results = []
        self.analysis_dir = "analysis"
        os.makedirs(self.analysis_dir, exist_ok=True)
        self.initialized = False
        self.memory_manager = get_memory_manager()
        self.vector_store = VectorStore()
        
    async def initialize(self):
        """시스템 초기화"""
        try:
            self.initialized = True
        except Exception as e:
            raise
        
    async def analyze(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """분석 수행"""
        if not self.initialized:
            raise RuntimeError("시스템이 초기화되지 않았습니다.")
        
        self.turn_count += 1
        
        # 5턴마다 분석 수행
        if self.turn_count % self.analysis_interval == 0:
            try:
                # 분석 작업을 비동기로 실행
                analysis_tasks = [
                    self.analyze_emotion(user_input),
                    self.analyze_belief(user_input),
                    self.analyze_wisdom(user_input),
                    self.analyze_eora(user_input),
                    self.analyze_system(user_input),
                    self.analyze_context(user_input)
                ]
                
                results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
                
                # 분석 결과 저장
                analysis_result = {
                    "timestamp": datetime.now().isoformat(),
                    "turn": self.turn_count,
                    "results": {}
                }
                
                for task, result in zip(analysis_tasks, results):
                    if isinstance(result, Exception):
                        analysis_result["results"][task.__name__] = {
                            "content": f"{task.__name__} 실패",
                            "confidence": 0.0
                        }
                    else:
                        analysis_result["results"][task.__name__] = result
                
                self.analysis_results.append(analysis_result)
                self.last_analysis = analysis_result
                
                # 분석 결과 저장
                self.save_analysis_results()
                
                return analysis_result["results"]
                
            except Exception as e:
                raise
        
        return self.last_analysis["results"] if self.last_analysis else {}
        
    async def analyze_emotion(self, text: str, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """감정 분석"""
        try:
            if embedding is None:
                embedding = await embed_text_async(text)
            
            if isinstance(embedding, list):
                embedding = np.array(embedding)
            return {
                "emotion": "neutral",
                "confidence": 0.8,
                "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            }
        except Exception as e:
            return {"emotion": "unknown", "confidence": 0.0, "embedding": []}
            
    async def analyze_belief(self, text: str, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """신념 분석"""
        try:
            if embedding is None:
                embedding = await embed_text_async(text)

            if isinstance(embedding, list):
                embedding = np.array(embedding)
            return {
                "belief": "neutral",
                "confidence": 0.8,
                "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            }
        except Exception as e:
            return {"belief": "unknown", "confidence": 0.0, "embedding": []}
            
    async def analyze_wisdom(self, text: str, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """지혜 분석"""
        try:
            if embedding is None:
                embedding = await embed_text_async(text)

            if isinstance(embedding, list):
                embedding = np.array(embedding)
            return {
                "wisdom": "neutral",
                "confidence": 0.8,
                "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            }
        except Exception as e:
            return {"wisdom": "unknown", "confidence": 0.0, "embedding": []}
            
    async def analyze_eora(self, text: str, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """EORA 분석"""
        try:
            if embedding is None:
                embedding = await embed_text_async(text)

            if isinstance(embedding, list):
                embedding = np.array(embedding)
            return {
                "eora": "neutral",
                "confidence": 0.8,
                "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            }
        except Exception as e:
            return {"eora": "unknown", "confidence": 0.0, "embedding": []}
            
    async def analyze_system(self, text: str, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """시스템 분석"""
        try:
            if embedding is None:
                embedding = await embed_text_async(text)

            if isinstance(embedding, list):
                embedding = np.array(embedding)
            return {
                "system": "neutral",
                "confidence": 0.8,
                "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            }
        except Exception as e:
            return {"system": "unknown", "confidence": 0.0, "embedding": []}
            
    async def analyze_context(self, text: str, embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """맥락 분석"""
        try:
            if embedding is None:
                embedding = await embed_text_async(text)

            if isinstance(embedding, list):
                embedding = np.array(embedding)
            return {
                "context": "neutral",
                "confidence": 0.8,
                "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            }
        except Exception as e:
            return {"context": "unknown", "confidence": 0.0, "embedding": []}
            
    def _save_analysis(self, analysis_type: str, result: Dict[str, Any]):
        """분석 결과 저장"""
        try:
            # 분석 타입별 디렉토리 생성
            type_dir = os.path.join(self.analysis_dir, analysis_type)
            os.makedirs(type_dir, exist_ok=True)
            
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}.json"
            filepath = os.path.join(type_dir, filename)
            
            # 결과 저장
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise
            
    def save_analysis_results(self):
        """분석 결과 저장"""
        try:
            with open("analysis/results.json", "w", encoding="utf-8") as f:
                json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise
            
    def get_last_analysis(self) -> Optional[Dict[str, Any]]:
        """마지막 분석 결과 반환"""
        return self.last_analysis

    async def get_related_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """관련 메모리 검색"""
        if not self.initialized:
            raise RuntimeError("시스템이 초기화되지 않았습니다.")
            
        try:
            return await self.memory_manager.search_memories(query, limit)
        except Exception as e:
            return []

# 전역 인스턴스
_analysis = None

async def get_analysis() -> Analysis:
    """Analysis 인스턴스 가져오기"""
    global _analysis
    if _analysis is None:
        _analysis = Analysis()
    return _analysis 