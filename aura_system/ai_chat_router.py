import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import numpy as np
import re

# 상대 경로 임포트
from .config import get_config
from .embeddings import get_embeddings
from .vector_store import get_vector_store
from .memory_store import get_memory_store, MemoryStore
from .memory_chain import get_memory_chain
from .recall_memory_with_enhancements import get_recall_enhancer
from .memory_structurer import get_memory_structurer
from .meta_store import get_meta_store
from .emotion_system.emotion_core import get_emotion_core
from .redis_manager import RedisManager

logger = logging.getLogger(__name__)

class AIChatRouter:
    """AI 채팅 라우터"""
    
    def __init__(self, redis_manager: RedisManager, memory_store: MemoryStore):
        """초기화"""
        self.redis_manager = redis_manager
        self.memory_store = memory_store
        self.config = get_config()
        self.initialized = False
        
        # 컴포넌트 초기화
        self.embeddings = None
        self.vector_store = None
        self.meta_store = None
        self.memory_chain = None
        self.recall_enhancer = None
        self.memory_structurer = None
        self.emotion_core = None

    async def initialize(self):
        """라우터 초기화"""
        if not self.initialized:
            try:
                # 컴포넌트 초기화
                self.embeddings = await get_embeddings()
                self.vector_store = await get_vector_store()
                self.meta_store = await get_meta_store()
                self.memory_chain = await get_memory_chain()
                self.recall_enhancer = await get_recall_enhancer()
                self.memory_structurer = await get_memory_structurer()
                
                # 감정 분석 코어 초기화 수정
                self.emotion_core = get_emotion_core()
                if hasattr(self.emotion_core, 'initialize'):
                    await self.emotion_core.initialize()

                # 설정 로드
                self.recall_threshold = self.config.get("recall_threshold", 0.7)
                self.min_response_length = self.config.get("min_response_length", 50)
                self.max_context_size = self.config.get("max_context_size", 10)
                
                self.initialized = True
                logger.info("✅ AI 채팅 라우터 초기화 완료")

            except Exception as e:
                logger.error(f"❌ AI 채팅 라우터 초기화 실패: {str(e)}")
                raise

    async def route_message(self, message: str, context: Dict = None) -> str:
        """메시지 라우팅"""
        if not self.initialized:
            await self.initialize()
            
        try:
            # 메시지 전처리
            processed_message = await self._preprocess_message(message)
            
            # 감정 분석
            emotion_result = await self.emotion_core.analyze_emotion(processed_message)
            
            # 메모리 검색
            relevant_memories = await self.memory_store.search_memories(
                processed_message,
                threshold=self.recall_threshold
            )
            
            # 컨텍스트 구성
            context = await self._build_context(
                processed_message,
                emotion_result,
                relevant_memories,
                context or {}
            )
            
            # 응답 생성
            response = await self._generate_response(context)
            
            # 메모리 저장
            await self._store_memory(processed_message, response, emotion_result)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ 메시지 라우팅 중 오류 발생: {str(e)}")
            raise

    async def _preprocess_message(self, message: str) -> str:
        """메시지 전처리"""
        try:
            # 기본 전처리
            message = message.strip()
            
            # 특수 문자 처리
            message = re.sub(r'[^\w\s가-힣]', ' ', message)
            
            # 중복 공백 제거
            message = re.sub(r'\s+', ' ', message)
            
            return message
            
        except Exception as e:
            logger.error(f"❌ 메시지 전처리 중 오류 발생: {str(e)}")
            return message

    async def _build_context(
        self,
        message: str,
        emotion_result: Dict,
        memories: List[Dict],
        base_context: Dict
    ) -> Dict:
        """컨텍스트 구성"""
        try:
            context = base_context.copy()
            
            # 기본 정보 추가
            context.update({
                "message": message,
                "emotion": emotion_result,
                "timestamp": datetime.now().isoformat()
            })
            
            # 메모리 추가
            if memories:
                context["memories"] = memories
                
            # 컨텍스트 크기 제한
            if len(context) > self.max_context_size:
                context = dict(list(context.items())[-self.max_context_size:])
                
            return context
            
        except Exception as e:
            logger.error(f"❌ 컨텍스트 구성 중 오류 발생: {str(e)}")
            return base_context

    async def _generate_response(self, context: Dict) -> str:
        """응답 생성"""
        try:
            # 대화 체인 실행
            response = await self.conversation_chain.arun(
                input=context["message"],
                context=context
            )
            
            # 응답 길이 검증
            if len(response) < self.min_response_length:
                response = await self._enhance_response(response, context)
                
            return response
            
        except Exception as e:
            logger.error(f"❌ 응답 생성 중 오류 발생: {str(e)}")
            return "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."

    async def _enhance_response(self, response: str, context: Dict) -> str:
        """응답 개선"""
        try:
            # 응답 개선 체인 실행
            enhanced_response = await self.recall_enhancer.arun(
                input=response,
                context=context
            )
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"❌ 응답 개선 중 오류 발생: {str(e)}")
            return response

    async def _store_memory(
        self,
        message: str,
        response: str,
        emotion_result: Dict
    ) -> None:
        """메모리 저장"""
        try:
            # 메모리 구조화
            memory = {
                "message": message,
                "response": response,
                "emotion": emotion_result,
                "timestamp": datetime.now().isoformat()
            }
            
            # 메모리 저장
            await self.memory_store.store_memory(memory)
            
        except Exception as e:
            logger.error(f"❌ 메모리 저장 중 오류 발생: {str(e)}")

    async def cleanup(self):
        """리소스 정리"""
        try:
            if self.emotion_core:
                await self.emotion_core.cleanup()
            if self.memory_structurer:
                await self.memory_structurer.cleanup()
            if self.recall_enhancer:
                await self.recall_enhancer.cleanup()
            if self.memory_chain:
                await self.memory_chain.cleanup()
            if self.meta_store:
                await self.meta_store.cleanup()
            if self.vector_store:
                await self.vector_store.cleanup()
            if self.embeddings:
                await self.embeddings.cleanup()
                
        except Exception as e:
            logger.error(f"❌ 리소스 정리 중 오류 발생: {str(e)}")

    def __del__(self):
        """소멸자"""
        if hasattr(self, 'initialized') and self.initialized:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.cleanup())
                else:
                    loop.run_until_complete(self.cleanup())
            except Exception as e:
                logger.error(f"❌ 소멸자 실행 중 오류 발생: {str(e)}")

# 싱글톤 인스턴스
_ai_chat_router = None

async def get_ai_chat_router() -> AIChatRouter:
    """AI 채팅 라우터 인스턴스 반환"""
    global _ai_chat_router
    if _ai_chat_router is None:
        _ai_chat_router = AIChatRouter()
    return _ai_chat_router 