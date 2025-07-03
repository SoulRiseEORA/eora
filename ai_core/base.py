"""
base.py
- AI 코어 기본 클래스
- 엔진 및 컴포넌트 초기화
- 비동기 처리 지원
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseEngine:
    """기본 엔진 클래스"""
    
    def __init__(self):
        self.config = None
        self.memory_manager = None
        self.embeddings = None
        self.vector_store = None
        self.memory_store = None
        self.meta_store = None
        self.memory_chain = None
        self.recall_enhancer = None
        
    async def initialize(self):
        """비동기 초기화"""
        try:
            # 설정 로드
            from aura_system.config import get_config
            self.config = get_config()
            
            # 컴포넌트 초기화
            from aura_system.memory_manager import get_memory_manager
            self.memory_manager = await get_memory_manager()
            
            from aura_system.embeddings import get_embeddings
            self.embeddings = await get_embeddings()
            
            from aura_system.vector_store import get_vector_store
            self.vector_store = await get_vector_store()
            
            from aura_system.memory_store import get_memory_store
            self.memory_store = await get_memory_store()
            
            from aura_system.meta_store import get_meta_store
            self.meta_store = await get_meta_store()
            
            from aura_system.memory_chain import get_memory_chain
            self.memory_chain = await get_memory_chain()
            
            from aura_system.recall_memory_with_enhancements import get_recall_enhancer
            self.recall_enhancer = await get_recall_enhancer()
            
            logger.info("✅ 엔진 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 엔진 초기화 실패: {str(e)}")
            raise
            
    async def process(self, input_data: Any) -> Any:
        """데이터 처리 (하위 클래스에서 구현)"""
        raise NotImplementedError
        
    async def cleanup(self):
        """리소스 정리"""
        try:
            if self.memory_manager:
                await self.memory_manager.cleanup()
                
            if self.vector_store:
                await self.vector_store.cleanup()
                
            if self.memory_store:
                await self.memory_store.cleanup()
                
            if self.meta_store:
                await self.meta_store.cleanup()
                
            if self.memory_chain:
                await self.memory_chain.cleanup()
                
            if self.recall_enhancer:
                await self.recall_enhancer.cleanup()
                
            logger.info("✅ 엔진 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ 엔진 정리 실패: {str(e)}")
            
    def __del__(self):
        """소멸자"""
        if asyncio.get_event_loop().is_running():
            asyncio.create_task(self.cleanup())
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.cleanup())
            loop.close()

class ThoughtEngine(BaseEngine):
    """사고 엔진"""
    
    async def process(self, input_data: Any) -> str:
        """사고 처리"""
        await super().process(input_data)
        return "💭 사고 처리 완료"

class ReflectionEngine(BaseEngine):
    """성찰 엔진"""
    
    async def process(self, input_data: Any) -> str:
        """성찰 처리"""
        await super().process(input_data)
        return "🤔 성찰 처리 완료"

class InsightEngine(BaseEngine):
    """통찰 엔진"""
    
    async def process(self, input_data: Any) -> str:
        """통찰 처리"""
        await super().process(input_data)
        return "✨ 통찰 처리 완료"

class TruthEngine(BaseEngine):
    """진리 엔진"""
    
    async def process(self, input_data: Any) -> str:
        """진리 처리"""
        await super().process(input_data)
        return "🔍 진리 처리 완료"

class EORAAI:
    """EORA AI 시스템"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.config = None
            self.thought_engine = None
            self.reflection_engine = None
            self.insight_engine = None
            self.truth_engine = None
            self._initialized = True
            
    async def initialize(self):
        """비동기 초기화"""
        try:
            # 설정 로드
            from aura_system.config import get_config
            self.config = get_config()
            
            # 엔진 초기화
            self.thought_engine = ThoughtEngine()
            await self.thought_engine.initialize()
            
            self.reflection_engine = ReflectionEngine()
            await self.reflection_engine.initialize()
            
            self.insight_engine = InsightEngine()
            await self.insight_engine.initialize()
            
            self.truth_engine = TruthEngine()
            await self.truth_engine.initialize()
            
            logger.info("✅ EORA AI 시스템 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ EORA AI 시스템 초기화 실패: {str(e)}")
            raise
            
    async def cleanup(self):
        """리소스 정리"""
        try:
            if self.thought_engine:
                await self.thought_engine.cleanup()
                
            if self.reflection_engine:
                await self.reflection_engine.cleanup()
                
            if self.insight_engine:
                await self.insight_engine.cleanup()
                
            if self.truth_engine:
                await self.truth_engine.cleanup()
                
            logger.info("✅ EORA AI 시스템 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ EORA AI 시스템 정리 실패: {str(e)}")
            
    def __del__(self):
        """소멸자"""
        if asyncio.get_event_loop().is_running():
            asyncio.create_task(self.cleanup())
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.cleanup())
            loop.close()

# 싱글톤 인스턴스
_eora_instance = None

async def get_eora_instance() -> EORAAI:
    """EORA AI 인스턴스 반환"""
    global _eora_instance
    if _eora_instance is None:
        _eora_instance = EORAAI()
        await _eora_instance.initialize()
    return _eora_instance 