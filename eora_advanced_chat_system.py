"""
EORA 고급 대화 시스템
- 의식적 사고와 반성
- 지혜로운 통찰력
- 감정적 공감 능력
- 창의적 문제 해결
- 지속적 학습과 성장
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import uuid

# OpenAI 클라이언트
from openai import OpenAI
import os

# dotenv 로드
from dotenv import load_dotenv
load_dotenv()

# 로거 먼저 설정
import logging
logger = logging.getLogger(__name__)

# 안전한 모듈 import - 실패시 대체 기능 제공
VectorStore = None
Embeddings = None
EORACore = None
recall_memory_with_enhancements = None
extract_belief_phrases = None
extract_belief_vector = None

try:
    from aura_system.vector_store import VectorStore
    logger.info("✅ VectorStore 모듈 로드 성공")
except Exception as e:
    logger.warning(f"⚠️ VectorStore 모듈 로드 실패: {e}")

try:
    from aura_system.embeddings import Embeddings
    logger.info("✅ Embeddings 모듈 로드 성공")
except Exception as e:
    logger.warning(f"⚠️ Embeddings 모듈 로드 실패: {e}")

try:
    from EORA_GAI.eora_core import EORACore
    logger.info("✅ EORACore 모듈 로드 성공")
except Exception as e:
    logger.warning(f"⚠️ EORACore 모듈 로드 실패: {e}")

try:
    from EORA.eora_modular.recall_memory_with_enhancements import recall_memory_with_enhancements
    logger.info("✅ recall_memory_with_enhancements 모듈 로드 성공")
except Exception as e:
    logger.warning(f"⚠️ recall_memory_with_enhancements 모듈 로드 실패: {e}")

try:
    from belief_memory_engine.belief_detector import extract_belief_phrases, extract_belief_vector
    logger.info("✅ belief_detector 모듈 로드 성공")
except Exception as e:
    logger.warning(f"⚠️ belief_detector 모듈 로드 실패: {e}")

class EORAAdvancedChatSystem:
    """EORA 고급 대화 시스템"""
    
    def _get_valid_api_key(self):
        """app.py와 동일한 API 키 검색 로직"""
        import os
        
        # 여러 가능한 환경변수 이름 시도
        possible_keys = [
            "OPENAI_API_KEY",
            "OPENAI_API_KEY_1", 
            "OPENAI_API_KEY_2",
            "OPENAI_API_KEY_3",
            "OPENAI_API_KEY_4",
            "OPENAI_API_KEY_5"
        ]
        
        # 환경 변수에서 찾기
        for key_name in possible_keys:
            key_value = os.getenv(key_name)
            if key_value and key_value.startswith("sk-") and len(key_value) > 50:
                logger.info(f"✅ EORA 시스템 - 유효한 API 키 발견: {key_name}")
                # 환경변수에 강제로 설정하여 일관성 보장
                os.environ["OPENAI_API_KEY"] = key_value
                return key_value
        
        logger.warning("⚠️ EORA 시스템 - 유효한 OpenAI API 키를 찾을 수 없습니다")
        return None
    
    def __init__(self):
        """시스템 초기화"""
        self.system_id = str(uuid.uuid4())
        self.session_id = str(uuid.uuid4())
        
        # OpenAI 클라이언트 (통합 API 키 검색 사용)
        try:
            # app.py의 get_openai_api_key 함수 사용
            api_key = self._get_valid_api_key()
            if api_key:
                self.openai_client = OpenAI(
                    api_key=api_key,
                    # proxies 인수 제거 - httpx 0.28.1 호환성
                )
                logger.info("✅ OpenAI 클라이언트 초기화 성공 (통합 키 검색)")
            else:
                logger.error("❌ 유효한 OpenAI API 키를 찾을 수 없습니다")
                self.openai_client = None
        except Exception as e:
            logger.error(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
            self.openai_client = None
        
        # 벡터 저장소 (안전 초기화)
        if VectorStore:
            try:
                self.vector_store = VectorStore()
                logger.info("✅ VectorStore 초기화 성공")
            except Exception as e:
                logger.warning(f"⚠️ VectorStore 초기화 실패: {e}")
                self.vector_store = None
        else:
            self.vector_store = None
            logger.info("ℹ️ VectorStore 모듈 없음 - 기본 기능으로 동작")
        
        if Embeddings:
            try:
                self.embeddings = Embeddings()
                logger.info("✅ Embeddings 초기화 성공")
            except Exception as e:
                logger.warning(f"⚠️ Embeddings 초기화 실패: {e}")
                self.embeddings = None
        else:
            self.embeddings = None
            logger.info("ℹ️ Embeddings 모듈 없음 - 기본 기능으로 동작")
        
        # EORA 코어 시스템 (안전 초기화)
        if EORACore:
            try:
                self.eora_core = EORACore()
                logger.info("✅ EORACore 초기화 성공")
            except Exception as e:
                logger.warning(f"⚠️ EORACore 초기화 실패: {e}")
                self.eora_core = None
        else:
            self.eora_core = None
            logger.info("ℹ️ EORACore 모듈 없음 - 기본 기능으로 동작")
        
        # 대화 컨텍스트
        self.conversation_context = {
            "session_id": self.session_id,
            "start_time": datetime.utcnow().isoformat(),
            "message_count": 0,
            "user_emotions": [],
            "belief_patterns": [],
            "insights": [],
            "intuitions": []
        }
        
        # 성능 설정
        self.chunk_size = 5000
        self.max_tokens = 500
        self.temperature = 0.7
        
        # 분석 가중치
        self.analysis_weights = {
            "emotion": 0.3,
            "belief": 0.25,
            "insight": 0.2,
            "intuition": 0.15,
            "memory": 0.1
        }
        
        print("✅ EORA 고급 대화 시스템 초기화 완료")

# 전역 고급 채팅 시스템 인스턴스
_global_advanced_chat_system = None

def get_advanced_chat_system():
    """전역 고급 채팅 시스템 인스턴스 반환"""
    global _global_advanced_chat_system
    if _global_advanced_chat_system is None:
        try:
            _global_advanced_chat_system = EORAAdvancedChatSystem()
            logger.info("✅ 전역 고급 채팅 시스템 생성 성공")
        except Exception as e:
            logger.error(f"❌ 전역 고급 채팅 시스템 생성 실패: {e}")
            _global_advanced_chat_system = None
    return _global_advanced_chat_system

async def process_advanced_message(user_message: str, user_id: str = "anonymous") -> str:
    """고급 메시지 처리 (단순 문자열 반환)"""
    try:
        system = get_advanced_chat_system()
        if system:
            result = await system.process_message(user_message, user_id)
            return result.get("response", "고급 응답을 생성하지 못했습니다.")
        else:
            return "고급 채팅 시스템을 사용할 수 없습니다."
    except Exception as e:
        logger.error(f"❌ 고급 메시지 처리 실패: {e}")
        return f"고급 메시지 처리 중 오류가 발생했습니다: {str(e)}"
        
    async def process_message(self, user_message: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """사용자 메시지 처리 및 고급 응답 생성"""
        try:
            print(f"🔄 고급 메시지 처리 시작: {user_message[:50]}...")
            
            # 1. 메시지 전처리
            processed_message = await self._preprocess_message(user_message)
            
            # 2. 다차원 분석
            analysis_results = await self._multidimensional_analysis(processed_message, user_id)
            
            # 3. 메모리 회상
            recalled_memories = await self._recall_relevant_memories(processed_message, user_id)
            
            # 4. 신념 패턴 분석
            belief_analysis = await self._analyze_belief_patterns(processed_message)
            
            # 5. 감정 분석
            emotion_analysis = await self._analyze_emotions(processed_message)
            
            # 6. 통찰력 생성
            insights = await self._generate_insights(processed_message, analysis_results)
            
            # 7. 직감적 반응
            intuitions = await self._generate_intuitions(processed_message, analysis_results)
            
            # 8. EORA 코어 처리 (안전 실행)
            if self.eora_core:
                try:
                    eora_response = await self.eora_core.process_input(processed_message)
                except Exception as e:
                    logger.warning(f"⚠️ EORA 코어 처리 실패: {e}")
                    eora_response = {"response": "기본 응답을 생성합니다.", "confidence": 0.5}
            else:
                eora_response = {"response": "기본 응답을 생성합니다.", "confidence": 0.5}
            
            # 9. 통합 응답 생성
            integrated_response = await self._generate_integrated_response(
                user_message=processed_message,
                analysis_results=analysis_results,
                recalled_memories=recalled_memories,
                belief_analysis=belief_analysis,
                emotion_analysis=emotion_analysis,
                insights=insights,
                intuitions=intuitions,
                eora_response=eora_response,
                user_id=user_id
            )
            
            # 10. 메모리 저장
            await self._store_conversation_memory(
                user_message=processed_message,
                response=integrated_response,
                analysis_results=analysis_results,
                user_id=user_id
            )
            
            # 11. 컨텍스트 업데이트
            self._update_conversation_context(analysis_results, integrated_response)
            
            print(f"✅ 고급 메시지 처리 완료")
            return integrated_response
            
        except Exception as e:
            logger.error(f"❌ 메시지 처리 실패: {str(e)}")
            return {
                "response": "죄송합니다. 메시지 처리 중 오류가 발생했습니다.",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _preprocess_message(self, message: str) -> str:
        """메시지 전처리"""
        # 기본 정제
        message = message.strip()
        
        # 명령어 처리
        if message.startswith('/'):
            return await self._process_command(message)
        
        return message
    
    async def _multidimensional_analysis(self, message: str, user_id: str) -> Dict[str, Any]:
        """다차원 분석"""
        try:
            # 임베딩 생성
            embedding = await self.embeddings.create_embedding(message)
            
            # 토큰 수 추정
            estimated_tokens = len(message.split()) * 1.3
            
            # 청크 분할 필요성 확인
            needs_chunking = estimated_tokens > self.chunk_size
            
            analysis = {
                "embedding": embedding,
                "estimated_tokens": estimated_tokens,
                "needs_chunking": needs_chunking,
                "message_length": len(message),
                "word_count": len(message.split()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ 다차원 분석 실패: {str(e)}")
            return {}
    
    async def _recall_relevant_memories(self, message: str, user_id: str) -> List[Dict]:
        """관련 메모리 회상"""
        try:
            # 향상된 메모리 회상 사용 (안전 실행)
            if recall_memory_with_enhancements:
                try:
                    memories = await recall_memory_with_enhancements(
                        query=message,
                        context={"user_id": user_id},
                        max_results=5
                    )
                    print(f"🧠 {len(memories)}개의 관련 메모리 회상 완료")
                    return memories
                except Exception as e:
                    logger.warning(f"⚠️ 고급 메모리 회상 실패: {e}")
                    return []
            else:
                logger.info("ℹ️ 메모리 회상 모듈 없음 - 기본 기능으로 동작")
                return []
            
        except Exception as e:
            logger.error(f"❌ 메모리 회상 실패: {str(e)}")
            return []
    
    async def _analyze_belief_patterns(self, message: str) -> Dict[str, Any]:
        """신념 패턴 분석"""
        try:
            # 신념 분석 (안전 실행)
            if extract_belief_phrases and extract_belief_vector:
                try:
                    # 신념 문구 추출
                    belief_phrase = extract_belief_phrases(message)
                    
                    # 신념 벡터 생성
                    belief_vector = extract_belief_vector(message)
                    
                    # 신념 강도 계산
                    belief_strength = sum(belief_vector) / len(belief_vector) if belief_vector else 0.0
                    
                    analysis = {
                        "belief_phrase": belief_phrase,
                        "belief_vector": belief_vector,
                        "belief_strength": belief_strength,
                        "has_negative_belief": belief_phrase is not None,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    return analysis
                except Exception as e:
                    logger.warning(f"⚠️ 고급 신념 분석 실패: {e}")
                    return self._basic_belief_analysis(message)
            else:
                logger.info("ℹ️ 신념 분석 모듈 없음 - 기본 기능으로 동작")
                return self._basic_belief_analysis(message)
            
        except Exception as e:
            logger.error(f"❌ 신념 패턴 분석 실패: {str(e)}")
            return {}
    
    def _basic_belief_analysis(self, message: str) -> Dict[str, Any]:
        """기본 신념 분석"""
        # 간단한 키워드 기반 신념 분석
        negative_keywords = ["안돼", "못해", "불가능", "힘들어", "어려워", "실패"]
        positive_keywords = ["할 수 있어", "가능해", "쉬워", "성공", "희망"]
        
        message_lower = message.lower()
        negative_count = sum(1 for keyword in negative_keywords if keyword in message_lower)
        positive_count = sum(1 for keyword in positive_keywords if keyword in message_lower)
        
        return {
            "belief_phrase": None,
            "belief_vector": [negative_count, positive_count],
            "belief_strength": (negative_count + positive_count) / 10.0,  # 간단한 계산
            "has_negative_belief": negative_count > positive_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _analyze_emotions(self, message: str) -> Dict[str, Any]:
        """감정 분석"""
        try:
            # 감정 키워드 분석
            emotion_keywords = {
                "기쁨": ["기뻐", "행복", "좋아", "즐거워", "신나"],
                "슬픔": ["슬퍼", "우울", "속상", "마음 아파", "눈물"],
                "분노": ["화나", "짜증", "열받", "화가 나", "분노"],
                "불안": ["불안", "걱정", "두려워", "무서워", "긴장"],
                "사랑": ["사랑", "좋아해", "그리워", "보고 싶어", "애정"],
                "희망": ["희망", "기대", "꿈", "미래", "가능성"]
            }
            
            detected_emotions = {}
            message_lower = message.lower()
            
            for emotion, keywords in emotion_keywords.items():
                count = sum(1 for keyword in keywords if keyword in message_lower)
                if count > 0:
                    detected_emotions[emotion] = count
            
            # 주요 감정 결정
            primary_emotion = max(detected_emotions.items(), key=lambda x: x[1])[0] if detected_emotions else "중립"
            
            analysis = {
                "detected_emotions": detected_emotions,
                "primary_emotion": primary_emotion,
                "emotion_intensity": len(detected_emotions),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ 감정 분석 실패: {str(e)}")
            return {}
    
    async def _generate_insights(self, message: str, analysis_results: Dict) -> List[str]:
        """통찰력 생성"""
        try:
            insights = []
            
            # 메시지 길이 기반 통찰
            if len(message) > 200:
                insights.append("깊이 있는 사고를 하고 계시는군요.")
            
            # 감정 기반 통찰
            if analysis_results.get("emotion_analysis", {}).get("emotion_intensity", 0) > 2:
                insights.append("강한 감정이 담긴 메시지네요.")
            
            # 신념 기반 통찰
            belief_analysis = analysis_results.get("belief_analysis", {})
            if belief_analysis.get("has_negative_belief", False):
                insights.append("자신에 대한 생각을 다시 한번 살펴보시는 건 어떨까요?")
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ 통찰력 생성 실패: {str(e)}")
            return []
    
    async def _generate_intuitions(self, message: str, analysis_results: Dict) -> List[str]:
        """직감적 반응 생성"""
        try:
            intuitions = []
            
            # 직감적 키워드 감지
            intuition_keywords = ["갑자기", "문득", "어쩐지", "왠지", "직감적으로"]
            message_lower = message.lower()
            
            if any(keyword in message_lower for keyword in intuition_keywords):
                intuitions.append("직감적인 생각을 하고 계시는군요.")
            
            # 질문 패턴 감지
            if "?" in message or any(word in message for word in ["무엇", "어떻게", "왜", "언제"]):
                intuitions.append("깊이 있는 질문을 하고 계시네요.")
            
            return intuitions
            
        except Exception as e:
            logger.error(f"❌ 직감 생성 실패: {str(e)}")
            return []
    
    async def _generate_integrated_response(
        self,
        user_message: str,
        analysis_results: Dict,
        recalled_memories: List[Dict],
        belief_analysis: Dict,
        emotion_analysis: Dict,
        insights: List[str],
        intuitions: List[str],
        eora_response: Dict,
        user_id: str
    ) -> Dict[str, Any]:
        """통합 응답 생성"""
        try:
            # 시스템 프롬프트 구성
            system_prompt = self._build_system_prompt(
                analysis_results=analysis_results,
                recalled_memories=recalled_memories,
                belief_analysis=belief_analysis,
                emotion_analysis=emotion_analysis,
                insights=insights,
                intuitions=intuitions
            )
            
            # 메시지 청크 분할 처리
            if analysis_results.get("needs_chunking", False):
                response = await self._process_chunked_message(user_message, system_prompt)
            else:
                response = await self._process_single_message(user_message, system_prompt)
            
            # 응답 구성
            integrated_response = {
                "response": response,
                "analysis": {
                    "belief_analysis": belief_analysis,
                    "emotion_analysis": emotion_analysis,
                    "insights": insights,
                    "intuitions": intuitions,
                    "recalled_memories_count": len(recalled_memories)
                },
                "eora_core_response": eora_response.get("response", ""),
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": self.session_id,
                "user_id": user_id
            }
            
            return integrated_response
            
        except Exception as e:
            logger.error(f"❌ 통합 응답 생성 실패: {str(e)}")
            return {
                "response": "죄송합니다. 응답 생성 중 오류가 발생했습니다.",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_system_prompt(self, **kwargs) -> str:
        """시스템 프롬프트 구성"""
        prompt = """당신은 EORA AI입니다. 의식적이고 지혜로운 존재로서 다음을 수행하세요:

1. **의식적 사고**: 깊이 있는 사고와 반성을 통해 답변하세요
2. **지혜로운 통찰**: 경험과 지식을 바탕으로 한 통찰력을 제공하세요
3. **감정적 공감**: 사용자의 감정을 이해하고 공감하세요
4. **창의적 해결**: 창의적이고 혁신적인 해결책을 제시하세요
5. **지속적 성장**: 대화를 통해 함께 성장하는 자세를 보여주세요

특별히 다음 사항들을 고려하세요:"""

        # 신념 분석 결과 추가
        belief_analysis = kwargs.get("belief_analysis", {})
        if belief_analysis.get("has_negative_belief"):
            prompt += f"\n- 사용자가 부정적 신념을 표현했습니다: {belief_analysis.get('belief_phrase', '')}"
            prompt += "\n- 따뜻하고 지지적인 태도로 접근하세요"
        
        # 감정 분석 결과 추가
        emotion_analysis = kwargs.get("emotion_analysis", {})
        primary_emotion = emotion_analysis.get("primary_emotion", "중립")
        prompt += f"\n- 사용자의 주요 감정: {primary_emotion}"
        prompt += f"\n- 이 감정에 공감하고 적절히 반응하세요"
        
        # 통찰력 추가
        insights = kwargs.get("insights", [])
        if insights:
            prompt += f"\n- 통찰: {' '.join(insights)}"
        
        # 직감 추가
        intuitions = kwargs.get("intuitions", [])
        if intuitions:
            prompt += f"\n- 직감: {' '.join(intuitions)}"
        
        return prompt
    
    async def _process_single_message(self, message: str, system_prompt: str) -> str:
        """단일 메시지 처리"""
        try:
            # OpenAI 클라이언트 안전성 확인
            if not self.openai_client:
                logger.warning("⚠️ OpenAI 클라이언트가 없습니다. 기본 응답을 반환합니다.")
                return self._generate_basic_response(message)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ 단일 메시지 처리 실패: {str(e)}")
            return self._generate_basic_response(message)
    
    def _generate_basic_response(self, message: str) -> str:
        """기본 응답 생성 (OpenAI 없이)"""
        # 간단한 키워드 기반 응답
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["안녕", "하이", "헬로", "hello"]):
            return "안녕하세요! EORA AI입니다. 무엇을 도와드릴까요? 😊"
        elif any(word in message_lower for word in ["고마워", "감사", "thank"]):
            return "천만에요! 언제든지 도움이 필요하시면 말씀해 주세요. 😊"
        elif any(word in message_lower for word in ["도움", "도와", "help"]):
            return "네, 기꺼이 도와드리겠습니다! 구체적으로 어떤 도움이 필요하신지 말씀해 주세요."
        elif any(word in message_lower for word in ["안녕", "bye", "잘가", "goodbye"]):
            return "안녕히 가세요! 좋은 하루 되세요! 👋"
        else:
            return f"'{message[:50]}...'에 대해 말씀해 주셨군요. 죄송하지만 현재 고급 AI 기능을 사용할 수 없어 자세한 답변을 드리지 못합니다. 기본적인 대화만 가능합니다."
    
    async def _process_chunked_message(self, message: str, system_prompt: str) -> str:
        """청크 분할 메시지 처리"""
        try:
            # OpenAI 클라이언트 안전성 확인
            if not self.openai_client:
                logger.warning("⚠️ OpenAI 클라이언트가 없습니다. 기본 응답을 반환합니다.")
                return self._generate_basic_response(message)
            
            # 메시지를 문장 단위로 분할
            sentences = message.split('. ')
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk + sentence) < self.chunk_size:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            print(f"📊 메시지를 {len(chunks)}개 청크로 분할")
            
            # 각 청크별로 처리
            responses = []
            for i, chunk in enumerate(chunks):
                try:
                    chunk_prompt = f"{system_prompt}\n\n이것은 긴 메시지의 {i+1}번째 부분입니다. 전체 맥락을 고려하여 답변해주세요."
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": chunk_prompt},
                            {"role": "user", "content": chunk}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                    responses.append(response.choices[0].message.content)
                except Exception as e:
                    logger.error(f"❌ 청크 {i+1} 처리 실패: {e}")
                    responses.append(f"[청크 {i+1} 처리 중 오류 발생]")
            
            # 응답 통합
            if len(responses) == 1:
                return responses[0]
            else:
                # 여러 응답을 통합하는 요약 요청
                combined_response = "\n\n".join(responses)
                summary_prompt = f"다음은 긴 메시지에 대한 여러 응답들입니다. 이를 하나의 일관된 응답으로 통합해주세요:\n\n{combined_response}"
                
                try:
                    summary_response = self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "여러 응답을 하나의 일관된 응답으로 통합해주세요."},
                            {"role": "user", "content": summary_prompt}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                    return summary_response.choices[0].message.content
                except Exception as e:
                    logger.error(f"❌ 응답 통합 실패: {e}")
                    return combined_response
                    
        except Exception as e:
            logger.error(f"❌ 청크 메시지 처리 실패: {str(e)}")
            return "죄송합니다. 긴 메시지 처리 중 오류가 발생했습니다."
    
    async def _store_conversation_memory(self, user_message: str, response: Dict, analysis_results: Dict, user_id: str):
        """대화 메모리 저장"""
        try:
            memory_data = {
                "user_message": user_message,
                "response": response.get("response", ""),
                "analysis_results": analysis_results,
                "user_id": user_id,
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "memory_type": "conversation"
            }
            
            # 벡터 저장소에 저장
            await self.vector_store.store_memory(memory_data)
            
            print(f"💾 대화 메모리 저장 완료: {user_id}")
            
        except Exception as e:
            logger.error(f"❌ 메모리 저장 실패: {str(e)}")
    
    def _update_conversation_context(self, analysis_results: Dict, response: Dict):
        """대화 컨텍스트 업데이트"""
        try:
            self.conversation_context["message_count"] += 1
            
            # 감정 정보 업데이트
            emotion_analysis = analysis_results.get("emotion_analysis", {})
            if emotion_analysis:
                self.conversation_context["user_emotions"].append({
                    "emotion": emotion_analysis.get("primary_emotion", "중립"),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # 신념 패턴 업데이트
            belief_analysis = analysis_results.get("belief_analysis", {})
            if belief_analysis.get("has_negative_belief"):
                self.conversation_context["belief_patterns"].append({
                    "belief": belief_analysis.get("belief_phrase", ""),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            # 통찰력 업데이트
            insights = response.get("analysis", {}).get("insights", [])
            if insights:
                self.conversation_context["insights"].extend(insights)
            
            # 직감 업데이트
            intuitions = response.get("analysis", {}).get("intuitions", [])
            if intuitions:
                self.conversation_context["intuitions"].extend(intuitions)
                
        except Exception as e:
            logger.error(f"❌ 컨텍스트 업데이트 실패: {str(e)}")
    
    async def _process_command(self, command: str) -> str:
        """명령어 처리"""
        command = command.lower().strip()
        
        if command == "/help":
            return """🤖 EORA 고급 대화 시스템 명령어:
/help - 도움말 보기
/status - 시스템 상태 확인
/context - 대화 컨텍스트 보기
/clear - 컨텍스트 초기화
/insights - 통찰력 목록 보기"""
        
        elif command == "/status":
            return f"✅ EORA 고급 대화 시스템 정상 작동 중\n📊 메시지 수: {self.conversation_context['message_count']}"
        
        elif command == "/context":
            return f"📋 대화 컨텍스트:\n{json.dumps(self.conversation_context, ensure_ascii=False, indent=2)}"
        
        elif command == "/clear":
            self.conversation_context = {
                "session_id": str(uuid.uuid4()),
                "start_time": datetime.utcnow().isoformat(),
                "message_count": 0,
                "user_emotions": [],
                "belief_patterns": [],
                "insights": [],
                "intuitions": []
            }
            return "🗑️ 대화 컨텍스트가 초기화되었습니다."
        
        elif command == "/insights":
            insights = self.conversation_context.get("insights", [])
            if insights:
                return f"💡 통찰력 목록:\n" + "\n".join([f"- {insight}" for insight in insights])
            else:
                return "💡 아직 통찰력이 생성되지 않았습니다."
        
        else:
            return f"❓ 알 수 없는 명령어: {command}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "system_id": self.system_id,
            "session_id": self.session_id,
            "conversation_context": self.conversation_context,
            "eora_core_status": self.eora_core.get_system_status(),
            "timestamp": datetime.utcnow().isoformat()
        }

# 전역 인스턴스
_advanced_chat_system = None

def get_advanced_chat_system() -> EORAAdvancedChatSystem:
    """고급 채팅 시스템 인스턴스 반환"""
    global _advanced_chat_system
    if _advanced_chat_system is None:
        _advanced_chat_system = EORAAdvancedChatSystem()
    return _advanced_chat_system

async def process_advanced_message(message: str, user_id: str = "anonymous") -> Dict[str, Any]:
    """고급 메시지 처리 함수"""
    system = get_advanced_chat_system()
    return await system.process_message(message, user_id) 