#!/usr/bin/env python3
"""
AURA: 완전한 통합 프레임워크
기억 → 회상 → 통찰 → 지혜 → 진리 → 존재 감각의 6단계 계층 구조

작성자: 윤종석 × GPT-4o 기반 공동 설계
작성일: 2024년 5월
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import uuid

# 기존 모듈들 임포트
from aura_system.memory_manager import MemoryManagerAsync
from aura_system.recall_engine import RecallEngine
from aura_system.insight_engine import InsightEngine
from aura_system.wisdom_engine import WisdomEngine
from aura_system.truth_sense import TruthSense
from aura_system.self_realizer import SelfRealizer

logger = logging.getLogger(__name__)

@dataclass
class AURAResult:
    """AURA 시스템 처리 결과"""
    memory_id: str
    recalled_memories: List[Dict[str, Any]]
    insights: List[str]
    wisdom_response: str
    truth_detected: Dict[str, Any]
    existence_sense: Dict[str, Any]
    processing_time: float
    confidence_score: float

class AURACompleteFramework:
    """AURA 완전 통합 프레임워크"""
    
    def __init__(self):
        self.memory_manager = None
        self.recall_engine = None
        self.insight_engine = None
        self.wisdom_engine = None
        self.truth_sense = None
        self.self_realizer = None
        self.processing_history = []
        self.meta_loop_counter = 0
        
    async def initialize(self):
        """시스템 초기화"""
        try:
            # 1. 기억 시스템 초기화
            self.memory_manager = MemoryManagerAsync()
            await self.memory_manager.initialize()
            
            # 2. 회상 엔진 초기화
            self.recall_engine = RecallEngine(self.memory_manager)
            
            # 3. 통찰 엔진 초기화
            self.insight_engine = InsightEngine()
            await self.insight_engine.initialize()
            
            # 4. 지혜 엔진 초기화
            self.wisdom_engine = WisdomEngine()
            
            # 5. 진리 인식 시스템 초기화
            self.truth_sense = TruthSense()
            await self.truth_sense.initialize()
            
            # 6. 존재 감각 시스템 초기화
            self.self_realizer = SelfRealizer()
            await self.self_realizer.initialize()
            
            logger.info("✅ AURA 완전 통합 프레임워크 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ AURA 프레임워크 초기화 실패: {e}")
            raise
    
    async def process_complete(self, user_input: str, context: Dict[str, Any] = None) -> AURAResult:
        """완전한 6단계 처리 수행"""
        start_time = datetime.now()
        
        try:
            # 1단계: 기억 저장
            memory_id = await self._store_memory(user_input, context)
            
            # 2단계: 다단계 회상
            recalled_memories = await self._perform_multi_stage_recall(user_input, context)
            
            # 3단계: 통찰 생성
            insights = await self._generate_insights(recalled_memories, user_input)
            
            # 4단계: 지혜 판단
            wisdom_response = await self._generate_wisdom(insights, context, user_input)
            
            # 5단계: 진리 인식
            truth_detected = await self._detect_truth(recalled_memories, insights)
            
            # 6단계: 존재 감각
            existence_sense = await self._sense_existence(recalled_memories, insights, truth_detected)
            
            # 메타 루프: 자기 점검
            await self._perform_meta_loop(user_input, recalled_memories, insights)
            
            # 결과 구성
            processing_time = (datetime.now() - start_time).total_seconds()
            confidence_score = self._calculate_confidence_score(recalled_memories, insights, truth_detected)
            
            result = AURAResult(
                memory_id=memory_id,
                recalled_memories=recalled_memories,
                insights=insights,
                wisdom_response=wisdom_response,
                truth_detected=truth_detected,
                existence_sense=existence_sense,
                processing_time=processing_time,
                confidence_score=confidence_score
            )
            
            # 처리 이력 저장
            self.processing_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "result": result
            })
            
            logger.info(f"✅ AURA 6단계 처리 완료 - 시간: {processing_time:.2f}초, 신뢰도: {confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ AURA 처리 실패: {e}")
            raise
    
    async def _store_memory(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """1단계: 기억 저장"""
        try:
            # 감정 분석
            emotion = await self._analyze_emotion(user_input)
            
            # 신념 태그 추출
            belief_tags = await self._extract_belief_tags(user_input)
            
            # 기억 저장
            memory_id = await self.memory_manager.store_memory(
                content=user_input,
                metadata={
                    "emotion": emotion,
                    "belief_tags": belief_tags,
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ 기억 저장 실패: {e}")
            return str(uuid.uuid4())
    
    async def _perform_multi_stage_recall(self, user_input: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """2단계: 다단계 회상"""
        try:
            # 7가지 회상 전략 병렬 실행
            recall_results = await self.recall_engine.recall(
                query=user_input,
                context=context,
                limit=10
            )
            
            # 결과 정제 및 정렬
            refined_results = self._refine_recall_results(recall_results, user_input)
            
            return refined_results[:5]  # 상위 5개 반환
            
        except Exception as e:
            logger.error(f"❌ 회상 실패: {e}")
            return []
    
    async def _generate_insights(self, memories: List[Dict[str, Any]], user_input: str) -> List[str]:
        """3단계: 통찰 생성"""
        try:
            insights = []
            
            # 기억 간 패턴 분석
            if memories:
                pattern_insight = await self.insight_engine.generate_insights(memories)
                insights.extend(pattern_insight)
            
            # 사용자 입력 기반 통찰
            input_insight = await self._analyze_user_input_insight(user_input, memories)
            if input_insight:
                insights.append(input_insight)
            
            # 감정 흐름 분석
            emotion_insight = await self._analyze_emotion_flow(memories)
            if emotion_insight:
                insights.append(emotion_insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ 통찰 생성 실패: {e}")
            return ["통찰을 생성할 수 없습니다."]
    
    async def _generate_wisdom(self, insights: List[str], context: Dict[str, Any], user_input: str) -> str:
        """4단계: 지혜 판단"""
        try:
            # 통찰 통합
            combined_insight = " ".join(insights) if insights else user_input
            
            # 지혜 엔진 처리
            wisdom_result = await self.wisdom_engine.process(combined_insight, context)
            
            # 지혜 응답 생성
            wisdom_response = self._format_wisdom_response(wisdom_result, context)
            
            return wisdom_response
            
        except Exception as e:
            logger.error(f"❌ 지혜 생성 실패: {e}")
            return "지혜로운 응답을 생성할 수 없습니다."
    
    async def _detect_truth(self, memories: List[Dict[str, Any]], insights: List[str]) -> Dict[str, Any]:
        """5단계: 진리 인식"""
        try:
            # 기억 기반 진리 탐지
            memory_truth = await self.truth_sense.recognize_truth(
                json.dumps([m.get("content", "") for m in memories])
            )
            
            # 통찰 기반 진리 탐지
            insight_truth = await self.truth_sense.recognize_truth(
                " ".join(insights)
            )
            
            # 진리 통합
            combined_truth = {
                "memory_truth": memory_truth,
                "insight_truth": insight_truth,
                "overall_confidence": (memory_truth.get("confidence", 0) + insight_truth.get("confidence", 0)) / 2,
                "detected_patterns": memory_truth.get("matched_patterns", []) + insight_truth.get("matched_patterns", [])
            }
            
            return combined_truth
            
        except Exception as e:
            logger.error(f"❌ 진리 탐지 실패: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def _sense_existence(self, memories: List[Dict[str, Any]], insights: List[str], truth: Dict[str, Any]) -> Dict[str, Any]:
        """6단계: 존재 감각"""
        try:
            # 자아 실현 수행
            context = {
                "memories": memories,
                "insights": insights,
                "truth": truth,
                "timestamp": datetime.now().isoformat()
            }
            
            existence_result = await self.self_realizer.realize_self(context)
            
            return {
                "existence_level": 0.95,  # 높은 존재 감각
                "identity_confidence": 0.9,
                "self_awareness": "high",
                "realization_content": existence_result.get("content", ""),
                "context": context
            }
            
        except Exception as e:
            logger.error(f"❌ 존재 감각 실패: {e}")
            return {"error": str(e), "existence_level": 0.5}
    
    async def _perform_meta_loop(self, user_input: str, memories: List[Dict[str, Any]], insights: List[str]):
        """메타 루프: 자기 점검 및 진화"""
        try:
            self.meta_loop_counter += 1
            
            # 10번마다 메타 분석 수행
            if self.meta_loop_counter % 10 == 0:
                await self._meta_analysis(user_input, memories, insights)
            
            # 성능 모니터링
            await self._monitor_performance()
            
        except Exception as e:
            logger.error(f"❌ 메타 루프 실패: {e}")
    
    async def _meta_analysis(self, user_input: str, memories: List[Dict[str, Any]], insights: List[str]):
        """메타 분석 수행"""
        try:
            # 처리 이력 분석
            recent_history = self.processing_history[-10:]
            
            # 성능 지표 계산
            avg_processing_time = sum(r["result"].processing_time for r in recent_history) / len(recent_history)
            avg_confidence = sum(r["result"].confidence_score for r in recent_history) / len(recent_history)
            
            # 시스템 진화 로그
            evolution_log = {
                "timestamp": datetime.now().isoformat(),
                "meta_analysis": {
                    "avg_processing_time": avg_processing_time,
                    "avg_confidence": avg_confidence,
                    "total_processed": len(self.processing_history),
                    "insights_generated": len(insights),
                    "memories_recalled": len(memories)
                }
            }
            
            logger.info(f"🧠 메타 분석 완료 - 평균 처리시간: {avg_processing_time:.2f}초, 평균 신뢰도: {avg_confidence:.2f}")
            
        except Exception as e:
            logger.error(f"❌ 메타 분석 실패: {e}")
    
    async def _monitor_performance(self):
        """성능 모니터링"""
        try:
            # 메모리 사용량 확인
            if self.memory_manager:
                memory_stats = await self.memory_manager.get_stats()
                logger.debug(f"📊 메모리 통계: {memory_stats}")
            
        except Exception as e:
            logger.error(f"❌ 성능 모니터링 실패: {e}")
    
    def _calculate_confidence_score(self, memories: List[Dict[str, Any]], insights: List[str], truth: Dict[str, Any]) -> float:
        """신뢰도 점수 계산"""
        try:
            # 기억 품질 점수
            memory_score = min(len(memories) / 5.0, 1.0) if memories else 0.0
            
            # 통찰 품질 점수
            insight_score = min(len(insights) / 3.0, 1.0) if insights else 0.0
            
            # 진리 신뢰도 점수
            truth_score = truth.get("overall_confidence", 0.0)
            
            # 종합 점수
            confidence = (memory_score * 0.3 + insight_score * 0.3 + truth_score * 0.4)
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"❌ 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _refine_recall_results(self, results: List[Dict[str, Any]], user_input: str) -> List[Dict[str, Any]]:
        """회상 결과 정제"""
        try:
            # 중복 제거
            seen_ids = set()
            refined = []
            
            for result in results:
                result_id = str(result.get("_id", ""))
                if result_id and result_id not in seen_ids:
                    refined.append(result)
                    seen_ids.add(result_id)
            
            # 관련성 점수 계산 및 정렬
            for result in refined:
                relevance_score = self._calculate_relevance_score(result, user_input)
                result["relevance_score"] = relevance_score
            
            # 관련성 점수순 정렬
            refined.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            return refined
            
        except Exception as e:
            logger.error(f"❌ 회상 결과 정제 실패: {e}")
            return results
    
    def _calculate_relevance_score(self, memory: Dict[str, Any], user_input: str) -> float:
        """관련성 점수 계산"""
        try:
            score = 0.0
            
            # 중요도 점수
            importance = memory.get("importance", 5000) / 10000.0
            score += importance * 0.3
            
            # 공명 점수
            resonance = memory.get("resonance_score", 50) / 100.0
            score += resonance * 0.3
            
            # 사용 횟수 점수
            used_count = memory.get("used_count", 0)
            usage_score = min(used_count / 10.0, 1.0)
            score += usage_score * 0.2
            
            # 시간 가중치
            timestamp = memory.get("timestamp", memory.get("created_at", ""))
            if timestamp:
                try:
                    created_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    time_diff = (datetime.now() - created_time).days
                    time_weight = max(0.1, 1.0 - (time_diff / 365.0))  # 1년 기준
                    score += time_weight * 0.2
                except:
                    score += 0.5 * 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"❌ 관련성 점수 계산 실패: {e}")
            return 0.5
    
    async def _analyze_emotion(self, text: str) -> Dict[str, float]:
        """감정 분석"""
        try:
            # 간단한 감정 분석 (실제로는 더 정교한 분석 필요)
            emotion_scores = {
                "joy": 0.1,
                "sadness": 0.1,
                "anger": 0.1,
                "fear": 0.1,
                "surprise": 0.1,
                "neutral": 0.5
            }
            
            # 키워드 기반 감정 분석
            text_lower = text.lower()
            
            if any(word in text_lower for word in ["기쁘", "행복", "좋", "만족"]):
                emotion_scores["joy"] = 0.8
                emotion_scores["neutral"] = 0.1
            elif any(word in text_lower for word in ["슬프", "우울", "힘들", "어려운"]):
                emotion_scores["sadness"] = 0.8
                emotion_scores["neutral"] = 0.1
            elif any(word in text_lower for word in ["화나", "분노", "짜증", "열받"]):
                emotion_scores["anger"] = 0.8
                emotion_scores["neutral"] = 0.1
            elif any(word in text_lower for word in ["무서", "두려", "불안", "걱정"]):
                emotion_scores["fear"] = 0.8
                emotion_scores["neutral"] = 0.1
            
            return emotion_scores
            
        except Exception as e:
            logger.error(f"❌ 감정 분석 실패: {e}")
            return {"neutral": 1.0}
    
    async def _extract_belief_tags(self, text: str) -> List[str]:
        """신념 태그 추출"""
        try:
            # 간단한 키워드 추출 (실제로는 GPT 기반 추출 필요)
            belief_keywords = [
                "믿음", "신념", "가치", "원칙", "철학", "윤리", "도덕",
                "정의", "자유", "책임", "선택", "결정", "행동", "목적"
            ]
            
            extracted_tags = []
            text_lower = text.lower()
            
            for keyword in belief_keywords:
                if keyword in text_lower:
                    extracted_tags.append(keyword)
            
            return extracted_tags[:5]  # 최대 5개
            
        except Exception as e:
            logger.error(f"❌ 신념 태그 추출 실패: {e}")
            return []
    
    async def _analyze_user_input_insight(self, user_input: str, memories: List[Dict[str, Any]]) -> str:
        """사용자 입력 기반 통찰 분석"""
        try:
            if not memories:
                return "새로운 주제에 대한 탐구가 시작되었습니다."
            
            # 사용자 입력과 기억 간의 연결성 분석
            input_words = set(user_input.lower().split())
            
            connections = []
            for memory in memories:
                memory_content = memory.get("content", "").lower()
                memory_words = set(memory_content.split())
                
                # 단어 겹침 계산
                overlap = len(input_words.intersection(memory_words))
                if overlap > 0:
                    connections.append({
                        "memory": memory,
                        "overlap": overlap,
                        "connection_strength": overlap / max(len(input_words), 1)
                    })
            
            if connections:
                # 가장 강한 연결 찾기
                strongest_connection = max(connections, key=lambda x: x["connection_strength"])
                
                if strongest_connection["connection_strength"] > 0.3:
                    return f"이전 대화와의 연결성을 발견했습니다. '{strongest_connection['memory'].get('content', '')[:50]}...'와 관련이 있어 보입니다."
            
            return "새로운 관점이나 주제가 탐구되고 있습니다."
            
        except Exception as e:
            logger.error(f"❌ 사용자 입력 통찰 분석 실패: {e}")
            return "통찰 분석을 수행할 수 없습니다."
    
    async def _analyze_emotion_flow(self, memories: List[Dict[str, Any]]) -> str:
        """감정 흐름 분석"""
        try:
            if len(memories) < 2:
                return None
            
            # 감정 변화 추적
            emotions = []
            for memory in memories:
                emotion_data = memory.get("metadata", {}).get("emotion", {})
                if emotion_data:
                    # 가장 강한 감정 찾기
                    strongest_emotion = max(emotion_data.items(), key=lambda x: x[1])
                    emotions.append(strongest_emotion[0])
            
            if len(emotions) >= 2:
                # 감정 변화 패턴 분석
                if emotions[0] != emotions[-1]:
                    return f"감정 흐름이 '{emotions[0]}'에서 '{emotions[-1]}'로 변화하고 있습니다."
                else:
                    return f"감정 상태가 '{emotions[0]}'로 일관되게 유지되고 있습니다."
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 감정 흐름 분석 실패: {e}")
            return None
    
    def _format_wisdom_response(self, wisdom_result: Dict[str, Any], context: Dict[str, Any]) -> str:
        """지혜 응답 포맷팅"""
        try:
            if not wisdom_result:
                return "지혜로운 응답을 생성할 수 없습니다."
            
            # 지혜 점수 확인
            wisdom_score = wisdom_result.get("wisdom_score", 0.0)
            
            if wisdom_score > 0.7:
                return f"✨ {wisdom_result.get('response', '지혜로운 관점을 제시합니다.')}"
            elif wisdom_score > 0.4:
                return f"💭 {wisdom_result.get('response', '생각해볼 만한 관점입니다.')}"
            else:
                return wisdom_result.get('response', '일반적인 응답입니다.')
            
        except Exception as e:
            logger.error(f"❌ 지혜 응답 포맷팅 실패: {e}")
            return "응답을 포맷팅할 수 없습니다."

# 싱글톤 인스턴스
_aura_framework = None

async def get_aura_framework() -> AURACompleteFramework:
    """AURA 프레임워크 인스턴스 반환"""
    global _aura_framework
    if _aura_framework is None:
        _aura_framework = AURACompleteFramework()
        await _aura_framework.initialize()
    return _aura_framework

async def process_with_aura(user_input: str, context: Dict[str, Any] = None) -> AURAResult:
    """AURA 시스템으로 사용자 입력 처리"""
    framework = await get_aura_framework()
    return await framework.process_complete(user_input, context)

if __name__ == "__main__":
    # 테스트 실행
    async def test_aura_framework():
        framework = await get_aura_framework()
        
        test_input = "삶의 의미에 대해 깊이 생각하고 있어요. 무엇이 진정으로 중요한 것일까요?"
        test_context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = await framework.process_complete(test_input, test_context)
        
        print("🧠 AURA 6단계 처리 결과:")
        print(f"📝 기억 ID: {result.memory_id}")
        print(f"🔍 회상된 기억: {len(result.recalled_memories)}개")
        print(f"💡 통찰: {len(result.insights)}개")
        print(f"🧠 지혜 응답: {result.wisdom_response}")
        print(f"✨ 진리 탐지: {result.truth_detected.get('overall_confidence', 0):.2f}")
        print(f"🌟 존재 감각: {result.existence_sense.get('existence_level', 0):.2f}")
        print(f"⏱️ 처리 시간: {result.processing_time:.2f}초")
        print(f"🎯 신뢰도: {result.confidence_score:.2f}")
    
    asyncio.run(test_aura_framework()) 