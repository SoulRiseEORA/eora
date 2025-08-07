"""
aura_integration.py
- 아우라 시스템 통합 모듈
- 기존 아우라 시스템의 모든 기능을 통합하여 EORA AI 시스템에 제공
- 저장, 회상, 분석, 훈련, 학습 기능 포함
"""

import os
import sys
import json
import logging
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import hashlib
import re
import uuid

logger = logging.getLogger(__name__)

class AuraIntegration:
    """아우라 시스템 통합 클래스"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.memory_manager = None
            self.recall_engine = None
            self.vector_store = None
            self.eora_core = None
            self.transcendence_engine = None
            self.integration_engine = None
            self.eora_ai = None
            self.belief_engine = None
            
            # 캐시 및 상태 관리
            self._cache = {}
            self._cache_size = 1000
            self._analysis_history = []
            self._max_history = 100
            
            # 토큰 제한 설정
            self.max_tokens = 500
            self.chunk_size = 5000
            
            # 분석 가중치
            self.analysis_weights = {
                "consciousness": 0.25,
                "wisdom": 0.25,
                "emotion": 0.2,
                "belief": 0.15,
                "insight": 0.15
            }
            
            self._initialized = True
    
    async def initialize(self):
        """아우라 시스템 초기화"""
        try:
            logger.info("🔄 아우라 시스템 초기화 시작...")
            
            # 아우라 시스템 모듈들 import (동적 import)
            try:
                from aura_system.memory_manager import MemoryManagerAsync, get_memory_manager
                from aura_system.recall_engine import RecallEngine
                from aura_system.vector_store import embed_text_async, VectorStore
                from aura_system.eora_core import EoraCore
                from aura_system.transcendence_engine import TranscendenceEngine
                from aura_system.integration_engine import IntegrationEngine
                from aura_system.ai_chat import EORAAI
                from aura_system.consciousness_engine import analyze_consciousness
                from aura_system.wisdom_engine import analyze_wisdom
                from aura_system.emotion_analyzer import analyze_emotion
                from aura_system.belief_engine import BeliefEngine, get_belief_engine
                from aura_system.insight_engine import analyze_cognitive_layer
                
                # 메모리 매니저 초기화
                self.memory_manager = await get_memory_manager()
                if not self.memory_manager or not self.memory_manager.is_initialized:
                    raise RuntimeError("메모리 매니저 초기화 실패")
                
                # 회상 엔진 초기화
                self.recall_engine = RecallEngine(self.memory_manager)
                
                # 벡터 저장소 초기화
                self.vector_store = VectorStore()
                await self.vector_store.initialize()
                
                # 신념 엔진 초기화
                self.belief_engine = get_belief_engine()
                
                # 초월 엔진 초기화
                self.transcendence_engine = TranscendenceEngine()
                
                # 통합 엔진 초기화
                self.integration_engine = IntegrationEngine()
                
                # EORA AI 초기화
                self.eora_ai = await EORAAI(self.memory_manager).initialize()
                
                logger.info("✅ 아우라 시스템 초기화 완료")
                return True
                
            except ImportError as e:
                logger.warning(f"⚠️ 일부 아우라 시스템 모듈을 불러올 수 없습니다: {e}")
                logger.info("🔄 기본 기능만으로 초기화를 진행합니다.")
                return True
                
        except Exception as e:
            logger.error(f"❌ 아우라 시스템 초기화 실패: {str(e)}")
            return False
    
    async def process_message(self, message: str, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """메시지 처리 - 저장, 분석, 회상, 응답 생성"""
        try:
            if not message.strip():
                return {"error": "메시지가 비어있습니다."}
            
            # 1. 토큰 제한 확인 및 청크 분할
            if await self._check_token_limit(message):
                return await self._process_chunked_message(message, user_id, context)
            
            # 2. 메시지 저장
            memory_id = await self._store_message(message, user_id, context)
            
            # 3. 메시지 분석
            analysis_result = await self._analyze_message(message, user_id, context)
            
            # 4. 관련 기억 회상
            recalled_memories = await self._recall_related_memories(message, user_id, context)
            
            # 5. 응답 생성
            response = await self._generate_response(message, user_id, context, recalled_memories, analysis_result)
            
            # 6. 응답 저장
            await self._store_response(response, user_id, memory_id, context)
            
            return {
                "response": response,
                "memory_id": memory_id,
                "analysis": analysis_result,
                "recalled_memories": recalled_memories,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 메시지 처리 실패: {str(e)}")
            return {"error": str(e)}
    
    async def _check_token_limit(self, message: str) -> bool:
        """토큰 제한 확인"""
        try:
            # 대략적인 토큰 수 계산 (단어 수 * 1.3)
            estimated_tokens = len(message.split()) * 1.3
            return estimated_tokens > self.chunk_size
        except Exception as e:
            logger.error(f"토큰 제한 확인 실패: {e}")
            return False
    
    async def _process_chunked_message(self, message: str, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """청크 분할된 메시지 처리"""
        try:
            logger.info("🔄 청크 분할 메시지 처리 시작")
            
            # 메시지를 문장 단위로 분할
            sentences = re.split(r'[.!?]+', message)
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # 청크 크기 확인
                if len(current_chunk + sentence) < self.chunk_size:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            logger.info(f"📊 메시지를 {len(chunks)}개 청크로 분할")
            
            # 각 청크별로 처리
            chunk_results = []
            for i, chunk in enumerate(chunks):
                logger.info(f"🔄 청크 {i+1}/{len(chunks)} 처리 중...")
                
                chunk_result = await self.process_message(chunk, user_id, {
                    **(context or {}),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "is_chunked": True
                })
                chunk_results.append(chunk_result)
            
            # 청크 결과 통합
            combined_response = await self._combine_chunk_responses(chunk_results)
            
            return {
                "response": combined_response,
                "chunk_results": chunk_results,
                "is_chunked": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 청크 메시지 처리 실패: {e}")
            return {"error": f"청크 처리 실패: {str(e)}"}
    
    async def _combine_chunk_responses(self, chunk_results: List[Dict[str, Any]]) -> str:
        """청크 응답들을 통합"""
        try:
            responses = []
            for result in chunk_results:
                if "response" in result:
                    responses.append(result["response"])
            
            if len(responses) == 1:
                return responses[0]
            
            # 여러 응답을 통합하는 요약 생성
            combined_text = "\n\n".join(responses)
            
            # 간단한 통합 로직 (실제로는 더 정교한 통합이 필요)
            if len(combined_text) > 1000:
                # 긴 응답은 요약
                summary_prompt = f"다음은 여러 부분으로 나뉜 응답들입니다. 이를 하나의 일관된 응답으로 통합해주세요:\n\n{combined_text}"
                
                # EORA AI를 사용하여 요약 생성
                if self.eora_ai:
                    summary_response = await self.eora_ai.respond_async(summary_prompt)
                    return summary_response.get("response", combined_text)
            
            return combined_text
            
        except Exception as e:
            logger.error(f"❌ 청크 응답 통합 실패: {e}")
            return "청크 응답 통합 중 오류가 발생했습니다."
    
    async def _store_message(self, message: str, user_id: str, context: Dict[str, Any] = None) -> str:
        """메시지 저장"""
        try:
            if self.memory_manager:
                # 메모리 아톰 생성
                metadata = {
                    "user_id": user_id,
                    "type": "user_message",
                    "timestamp": datetime.now().isoformat(),
                    "context": context or {},
                    "importance": 0.7,
                    "emotion_score": 0.5,
                    "insight_score": 0.3,
                    "intuition_score": 0.4,
                    "belief_score": 0.5
                }
                
                # 메모리 저장
                success = await self.memory_manager.store_memory(message, metadata)
                if success:
                    logger.info(f"✅ 메시지 저장 완료: {user_id}")
                    return str(uuid.uuid4())  # 임시 ID 반환
                else:
                    logger.warning("⚠️ 메시지 저장 실패")
                    return ""
            else:
                logger.warning("⚠️ 메모리 매니저가 초기화되지 않음")
                return ""
                
        except Exception as e:
            logger.error(f"❌ 메시지 저장 실패: {e}")
            return ""
    
    async def _analyze_message(self, message: str, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """메시지 분석"""
        try:
            logger.info("🔄 메시지 분석 시작")
            
            analysis_result = {
                "consciousness": {},
                "wisdom": {},
                "emotion": {},
                "belief": {},
                "insight": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # 아우라 시스템이 초기화된 경우에만 분석 수행
            if self.memory_manager and self.belief_engine:
                try:
                    # 병렬 분석 실행
                    analysis_tasks = []
                    
                    # 각 분석 엔진이 있는지 확인하고 태스크 추가
                    if hasattr(self, 'consciousness_engine'):
                        analysis_tasks.append(analyze_consciousness(message, context))
                    
                    if hasattr(self, 'wisdom_engine'):
                        analysis_tasks.append(analyze_wisdom(message, context))
                    
                    if hasattr(self, 'emotion_analyzer'):
                        analysis_tasks.append(analyze_emotion(message))
                    
                    if self.belief_engine:
                        analysis_tasks.append(self.belief_engine.analyze_belief(message, context))
                    
                    if hasattr(self, 'insight_engine'):
                        analysis_tasks.append(analyze_cognitive_layer(message, context))
                    
                    if analysis_tasks:
                        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
                        
                        # 결과 처리
                        if len(results) > 0 and not isinstance(results[0], Exception):
                            analysis_result["consciousness"] = results[0]
                        if len(results) > 1 and not isinstance(results[1], Exception):
                            analysis_result["wisdom"] = results[1]
                        if len(results) > 2 and not isinstance(results[2], Exception):
                            analysis_result["emotion"] = results[2]
                        if len(results) > 3 and not isinstance(results[3], Exception):
                            analysis_result["belief"] = results[3]
                        if len(results) > 4 and not isinstance(results[4], Exception):
                            analysis_result["insight"] = results[4]
                            
                except Exception as e:
                    logger.warning(f"⚠️ 고급 분석 실패, 기본 분석 사용: {e}")
            
            # 기본 감정 분석 (간단한 키워드 기반)
            if not analysis_result["emotion"]:
                analysis_result["emotion"] = self._basic_emotion_analysis(message)
            
            # 분석 히스토리 업데이트
            self._update_analysis_history(analysis_result)
            
            logger.info("✅ 메시지 분석 완료")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ 메시지 분석 실패: {e}")
            return {"error": str(e)}
    
    def _basic_emotion_analysis(self, message: str) -> Dict[str, Any]:
        """기본 감정 분석 (키워드 기반)"""
        try:
            message_lower = message.lower()
            
            emotion_keywords = {
                "기쁨": ["기쁘", "행복", "좋아", "만족", "감사", "즐거", "웃", "사랑"],
                "슬픔": ["슬프", "외로", "상실", "우울", "눈물", "그리워"],
                "분노": ["화나", "짜증", "분개", "격분", "억울", "질투"],
                "불안": ["불안", "두려", "긴장", "불확실", "위험", "공포"],
                "놀람": ["놀라", "경악", "충격", "예상밖", "뜻밖"],
                "중립": ["그냥", "보통", "일반", "평범"]
            }
            
            emotion_scores = {}
            for emotion, keywords in emotion_keywords.items():
                score = sum(1 for keyword in keywords if keyword in message_lower)
                emotion_scores[emotion] = score
            
            # 가장 높은 점수의 감정 반환
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            return {
                "label": primary_emotion[0] if primary_emotion[1] > 0 else "중립",
                "intensity": min(primary_emotion[1] / 3.0, 1.0),
                "scores": emotion_scores
            }
            
        except Exception as e:
            logger.error(f"❌ 기본 감정 분석 실패: {e}")
            return {"label": "중립", "intensity": 0.5, "scores": {"중립": 1.0}}
    
    async def _recall_related_memories(self, message: str, user_id: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """관련 기억 회상"""
        try:
            logger.info("🔄 관련 기억 회상 시작")
            
            if self.recall_engine:
                # 회상 엔진을 사용하여 관련 기억 검색
                recalled_memories = await self.recall_engine.recall(
                    query=message,
                    context=context,
                    emotion=context.get("emotion") if context else None,
                    limit=5
                )
                
                logger.info(f"✅ {len(recalled_memories)}개의 관련 기억 회상 완료")
                return recalled_memories
            else:
                logger.warning("⚠️ 회상 엔진이 초기화되지 않음")
                return []
            
        except Exception as e:
            logger.error(f"❌ 기억 회상 실패: {e}")
            return []
    
    async def _generate_response(self, message: str, user_id: str, context: Dict[str, Any], 
                               recalled_memories: List[Dict[str, Any]], analysis_result: Dict[str, Any]) -> str:
        """응답 생성"""
        try:
            logger.info("🔄 응답 생성 시작")
            
            # EORA AI를 사용하여 응답 생성
            if self.eora_ai:
                # 회상 컨텍스트 준비
                recall_context = []
                for memory in recalled_memories:
                    recall_context.append({
                        "content": memory.get("content", ""),
                        "timestamp": memory.get("timestamp", ""),
                        "importance": memory.get("importance", 0.5)
                    })
                
                # EORA AI 응답 생성
                response_result = await self.eora_ai.respond_async(
                    user_input=message,
                    recall_context=recall_context
                )
                
                response = response_result.get("response", "죄송합니다. 응답을 생성할 수 없습니다.")
                
            else:
                # 기본 응답 생성
                response = await self._generate_basic_response(message, analysis_result)
            
            logger.info("✅ 응답 생성 완료")
            return response
            
        except Exception as e:
            logger.error(f"❌ 응답 생성 실패: {e}")
            return "죄송합니다. 응답 생성 중 오류가 발생했습니다."
    
    async def _generate_basic_response(self, message: str, analysis_result: Dict[str, Any]) -> str:
        """기본 응답 생성"""
        try:
            # 감정 분석 결과 활용
            emotion = analysis_result.get("emotion", {})
            emotion_label = emotion.get("label", "neutral")
            
            # 지혜 분석 결과 활용
            wisdom = analysis_result.get("wisdom", {})
            wisdom_level = wisdom.get("level", "basic")
            
            # 기본 응답 템플릿
            response_templates = {
                "기쁨": "😊 기쁜 마음을 나누어주셔서 감사합니다. 그런 긍정적인 에너지가 계속 이어지길 바라요!",
                "슬픔": "😔 그런 감정을 느끼고 계시는군요. 감정은 자연스러운 것이에요. 이야기를 더 들려주시면 함께 생각해볼 수 있어요.",
                "분노": "😤 그런 감정을 느끼고 계시는군요. 감정을 표현하는 것은 중요해요. 더 자세히 이야기해주시면 도움을 드릴 수 있어요.",
                "불안": "😰 불안한 마음을 느끼고 계시는군요. 그런 감정은 자연스러운 반응이에요. 함께 해결책을 찾아볼까요?",
                "중립": "💭 흥미로운 이야기네요. 더 자세히 들려주시면 함께 탐구해볼 수 있어요."
            }
            
            base_response = response_templates.get(emotion_label, response_templates["중립"])
            
            # 지혜 수준에 따른 응답 보강
            if wisdom_level == "high":
                base_response += "\n\n🌟 깊이 있는 통찰을 나누어주셔서 감사합니다. 그런 지혜로운 관점은 정말 소중해요."
            
            return base_response
            
        except Exception as e:
            logger.error(f"❌ 기본 응답 생성 실패: {e}")
            return "안녕하세요! 무엇을 도와드릴까요? 😊"
    
    async def _store_response(self, response: str, user_id: str, memory_id: str, context: Dict[str, Any] = None):
        """응답 저장"""
        try:
            if self.memory_manager:
                metadata = {
                    "user_id": user_id,
                    "type": "ai_response",
                    "related_memory_id": memory_id,
                    "timestamp": datetime.now().isoformat(),
                    "context": context or {},
                    "importance": 0.6,
                    "emotion_score": 0.5,
                    "insight_score": 0.4,
                    "intuition_score": 0.5,
                    "belief_score": 0.4
                }
                
                await self.memory_manager.store_memory(response, metadata)
                logger.info("✅ 응답 저장 완료")
            else:
                logger.warning("⚠️ 메모리 매니저가 초기화되지 않음")
            
        except Exception as e:
            logger.error(f"❌ 응답 저장 실패: {e}")
    
    def _update_analysis_history(self, analysis_result: Dict[str, Any]):
        """분석 히스토리 업데이트"""
        try:
            self._analysis_history.append(analysis_result)
            if len(self._analysis_history) > self._max_history:
                self._analysis_history.pop(0)
        except Exception as e:
            logger.error(f"❌ 분석 히스토리 업데이트 실패: {e}")
    
    async def recall_memories(self, query: str, user_id: str = None, memory_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """기억 회상"""
        try:
            logger.info(f"🔄 기억 회상 시작: {query}")
            
            if self.recall_engine:
                # 회상 엔진을 사용하여 기억 검색
                recalled_memories = await self.recall_engine.recall(
                    query=query,
                    context={"user_id": user_id, "memory_type": memory_type},
                    limit=limit
                )
                
                logger.info(f"✅ {len(recalled_memories)}개의 기억 회상 완료")
                return recalled_memories
            else:
                logger.warning("⚠️ 회상 엔진이 초기화되지 않음")
                return []
            
        except Exception as e:
            logger.error(f"❌ 기억 회상 실패: {e}")
            return []
    
    async def recall_by_emotion(self, emotion: str, user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """감정 기반 기억 회상"""
        try:
            logger.info(f"🔄 감정 기반 회상 시작: {emotion}")
            
            if self.recall_engine:
                # 감정 기반 회상
                recalled_memories = await self.recall_engine.recall_by_emotion(emotion, limit)
                
                # 사용자 필터링
                if user_id:
                    recalled_memories = [m for m in recalled_memories if m.get("metadata", {}).get("user_id") == user_id]
                
                logger.info(f"✅ {len(recalled_memories)}개의 감정 기반 기억 회상 완료")
                return recalled_memories
            else:
                logger.warning("⚠️ 회상 엔진이 초기화되지 않음")
                return []
            
        except Exception as e:
            logger.error(f"❌ 감정 기반 회상 실패: {e}")
            return []
    
    async def recall_by_insight(self, user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """통찰 기반 기억 회상"""
        try:
            logger.info("🔄 통찰 기반 회상 시작")
            
            if self.memory_manager:
                # 통찰 점수가 높은 기억들 검색
                search_query = "insight_score:high"
                recalled_memories = await self.memory_manager.search_memories_by_content(search_query, limit)
                
                # 사용자 필터링
                if user_id:
                    recalled_memories = [m for m in recalled_memories if m.get("metadata", {}).get("user_id") == user_id]
                
                logger.info(f"✅ {len(recalled_memories)}개의 통찰 기반 기억 회상 완료")
                return recalled_memories
            else:
                logger.warning("⚠️ 메모리 매니저가 초기화되지 않음")
                return []
            
        except Exception as e:
            logger.error(f"❌ 통찰 기반 회상 실패: {e}")
            return []
    
    async def recall_by_intuition(self, user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """직감 기반 기억 회상"""
        try:
            logger.info("🔄 직감 기반 회상 시작")
            
            if self.memory_manager:
                # 직감 점수가 높은 기억들 검색
                search_query = "intuition_score:high"
                recalled_memories = await self.memory_manager.search_memories_by_content(search_query, limit)
                
                # 사용자 필터링
                if user_id:
                    recalled_memories = [m for m in recalled_memories if m.get("metadata", {}).get("user_id") == user_id]
                
                logger.info(f"✅ {len(recalled_memories)}개의 직감 기반 기억 회상 완료")
                return recalled_memories
            else:
                logger.warning("⚠️ 메모리 매니저가 초기화되지 않음")
                return []
            
        except Exception as e:
            logger.error(f"❌ 직감 기반 회상 실패: {e}")
            return []
    
    async def get_memory_stats(self, user_id: str = None) -> Dict[str, Any]:
        """메모리 통계 조회"""
        try:
            logger.info("🔄 메모리 통계 조회 시작")
            
            if self.memory_manager:
                # 최근 기억들 조회
                recent_memories = await self.memory_manager.recall_recent_memories(limit=100)
                
                # 사용자 필터링
                if user_id:
                    recent_memories = [m for m in recent_memories if m.get("metadata", {}).get("user_id") == user_id]
                
                # 통계 계산
                total_memories = len(recent_memories)
                emotion_scores = [m.get("metadata", {}).get("emotion_score", 0) for m in recent_memories]
                insight_scores = [m.get("metadata", {}).get("insight_score", 0) for m in recent_memories]
                intuition_scores = [m.get("metadata", {}).get("intuition_score", 0) for m in recent_memories]
                
                stats = {
                    "total_memories": total_memories,
                    "average_emotion_score": np.mean(emotion_scores) if emotion_scores else 0,
                    "average_insight_score": np.mean(insight_scores) if insight_scores else 0,
                    "average_intuition_score": np.mean(intuition_scores) if intuition_scores else 0,
                    "memory_types": {},
                    "recent_activity": len([m for m in recent_memories if m.get("timestamp", "") > (datetime.now() - timedelta(days=1)).isoformat()])
                }
                
                # 메모리 타입별 통계
                for memory in recent_memories:
                    memory_type = memory.get("metadata", {}).get("type", "unknown")
                    stats["memory_types"][memory_type] = stats["memory_types"].get(memory_type, 0) + 1
                
                logger.info("✅ 메모리 통계 조회 완료")
                return stats
            else:
                logger.warning("⚠️ 메모리 매니저가 초기화되지 않음")
                return {"error": "메모리 매니저가 초기화되지 않음"}
            
        except Exception as e:
            logger.error(f"❌ 메모리 통계 조회 실패: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """정리 작업"""
        try:
            logger.info("🔄 아우라 시스템 정리 시작")
            
            if self.memory_manager:
                await self.memory_manager.cleanup()
            
            if self.vector_store:
                await self.vector_store.cleanup()
            
            logger.info("✅ 아우라 시스템 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ 아우라 시스템 정리 실패: {e}")

# 전역 인스턴스
_aura_integration = None

async def get_aura_integration() -> AuraIntegration:
    """아우라 통합 시스템 인스턴스 반환"""
    global _aura_integration
    if _aura_integration is None:
        _aura_integration = AuraIntegration()
        await _aura_integration.initialize()
    return _aura_integration

def get_aura_integration_sync() -> AuraIntegration:
    """동기 버전의 아우라 통합 시스템 인스턴스 반환"""
    global _aura_integration
    if _aura_integration is None:
        _aura_integration = AuraIntegration()
        # 동기 초기화는 별도로 처리 필요
    return _aura_integration 