import numpy as np
from typing import Dict, List, Any, Tuple
import asyncio
from datetime import datetime
from aura_system.vector_store import embed_text_async
from aura_system.emotion_analyzer import analyze_emotion
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

# 싱글톤 인스턴스
_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = ContextAnalyzer()
    return _analyzer

class ContextAnalyzer:
    def __init__(self):
        self._cache = {}
        self._cache_size = 1000
        self._context_history = []
        self._max_history = 20
        
        # 문맥 분석 가중치
        self.context_weights = {
            "topic": 0.3,
            "emotion": 0.2,
            "temporal": 0.2,
            "semantic": 0.2,
            "interaction": 0.1
        }
        
        # 주제 분류기
        self.topic_classifier = {
            "일상": ["일상", "생활", "습관", "루틴", "일과"],
            "감정": ["감정", "기분", "마음", "심리", "정서"],
            "관계": ["관계", "친구", "가족", "연인", "동료"],
            "일": ["일", "업무", "직장", "프로젝트", "과제"],
            "취미": ["취미", "관심사", "취향", "즐거움", "여가"],
            "건강": ["건강", "운동", "식사", "수면", "스트레스"],
            "학습": ["학습", "공부", "지식", "교육", "성장"],
            "목표": ["목표", "계획", "미래", "희망", "꿈"]
        }
        
        # 상호작용 패턴
        self.interaction_patterns = {
            "질문": ["?", "무엇", "어떻게", "왜", "언제", "어디서", "누가"],
            "요청": ["해주", "부탁", "원해", "바래", "필요해"],
            "공유": ["생각", "느낌", "경험", "이야기", "알려"],
            "동의": ["맞아", "그래", "좋아", "응", "네"],
            "반대": ["아니", "그렇지 않아", "다르게", "반대"],
            "감사": ["고마워", "감사", "덕분", "좋았어"]
        }

        self.client = OpenAI()

    async def analyze(self, text: str) -> str:
        """컨텍스트 분석
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            str: 분석 결과
        """
        try:
            # 동기 함수를 비동기로 실행
            def analyze_context():
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system", "content": "다음 텍스트의 컨텍스트를 분석해주세요. 주제, 의도, 배경 등을 파악해주세요."},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.3,
                        max_tokens=200
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"⚠️ 컨텍스트 분석 실패: {str(e)}")
                    return None
                    
            return await asyncio.to_thread(analyze_context)
        except Exception as e:
            logger.error(f"⚠️ 컨텍스트 분석 실패: {str(e)}")
            return None

    def _analyze_topic(self, text: str) -> Tuple[str, float]:
        """주제 분석"""
        try:
            max_score = 0.0
            best_topic = "일상"
            
            for topic, keywords in self.topic_classifier.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > max_score:
                    max_score = score
                    best_topic = topic
            
            # 점수 정규화
            normalized_score = min(max_score / 5, 1.0)
            
            return best_topic, normalized_score
            
        except Exception:
            return "일상", 0.5

    def _analyze_temporal_context(self, text: str) -> Dict[str, Any]:
        """시간적 문맥 분석"""
        try:
            temporal_context = {
                "type": "present",
                "specificity": 0.5,
                "time_reference": None
            }
            
            # 시간 표현 패턴
            time_patterns = {
                "past": ["어제", "지난", "이전", "과거", "했었"],
                "present": ["지금", "현재", "이제", "오늘", "지금"],
                "future": ["내일", "다음", "앞으로", "향후", "할 예정"]
            }
            
            # 시간 표현 검색
            for time_type, patterns in time_patterns.items():
                if any(pattern in text for pattern in patterns):
                    temporal_context["type"] = time_type
                    temporal_context["specificity"] = 0.8
                    break
            
            # 구체적인 시간 참조
            if "시" in text or "분" in text or "일" in text:
                temporal_context["specificity"] = 1.0
                temporal_context["time_reference"] = "specific"
            
            return temporal_context
            
        except Exception:
            return {"type": "present", "specificity": 0.5, "time_reference": None}

    async def _analyze_semantic_context(self, text: str, embedding: List[float]) -> Dict[str, Any]:
        """의미적 문맥 분석"""
        try:
            semantic_context = {
                "complexity": 0.5,
                "formality": 0.5,
                "specificity": 0.5
            }
            
            # 문장 복잡도 계산
            sentences = text.split(".")
            words = text.split()
            semantic_context["complexity"] = min(len(sentences) * 0.2, 1.0)
            
            # 격식체 여부
            formal_markers = ["습니다", "니다", "습니다", "입니다", "하겠습니다"]
            informal_markers = ["야", "아", "어", "해", "해요"]
            
            formal_count = sum(1 for marker in formal_markers if marker in text)
            informal_count = sum(1 for marker in informal_markers if marker in text)
            
            if formal_count + informal_count > 0:
                semantic_context["formality"] = formal_count / (formal_count + informal_count)
            
            # 구체성 계산
            specific_markers = ["이", "그", "저", "이런", "그런", "저런"]
            semantic_context["specificity"] = min(
                sum(1 for marker in specific_markers if marker in text) * 0.2,
                1.0
            )
            
            return semantic_context
            
        except Exception:
            return {"complexity": 0.5, "formality": 0.5, "specificity": 0.5}

    def _analyze_interaction_pattern(self, text: str) -> Dict[str, Any]:
        """상호작용 패턴 분석"""
        try:
            pattern_scores = {}
            
            for pattern, markers in self.interaction_patterns.items():
                score = sum(1 for marker in markers if marker in text)
                if score > 0:
                    pattern_scores[pattern] = min(score * 0.2, 1.0)
            
            if not pattern_scores:
                return {"type": "statement", "confidence": 0.5}
            
            # 가장 높은 점수의 패턴 선택
            best_pattern = max(pattern_scores.items(), key=lambda x: x[1])
            
            return {
                "type": best_pattern[0],
                "confidence": best_pattern[1]
            }
            
        except Exception:
            return {"type": "statement", "confidence": 0.5}

    def _update_context_history(self, context: Dict[str, Any]):
        """문맥 이력 업데이트"""
        try:
            self._context_history.append(context)
            if len(self._context_history) > self._max_history:
                self._context_history.pop(0)
        except Exception as e:
            print(f"문맥 이력 업데이트 중 오류: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
        except Exception as e:
            print(f"캐시 업데이트 중 오류: {str(e)}")

    def _create_default_context(self) -> Dict[str, Any]:
        """기본 문맥 생성"""
        return {
            "topic": {"name": "일상", "score": 0.5},
            "emotion": {
                "primary": "neutral",
                "intensity": 0.5,
                "scores": {"neutral": 1.0}
            },
            "temporal": {"type": "present", "specificity": 0.5, "time_reference": None},
            "semantic": {"complexity": 0.5, "formality": 0.5, "specificity": 0.5},
            "interaction": {"type": "statement", "confidence": 0.5},
            "timestamp": datetime.now().isoformat()
        } 

async def analyze_context(text: str,
                         context: Dict[str, Any] = None,
                         emotion: Dict[str, Any] = None,
                         belief: Dict[str, Any] = None,
                         wisdom: Dict[str, Any] = None,
                         eora: Dict[str, Any] = None,
                         system: Dict[str, Any] = None,
                         history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """문맥 분석
    
    Args:
        text (str): 분석할 텍스트
        context (Dict[str, Any], optional): 문맥 정보
        emotion (Dict[str, Any], optional): 감정 정보
        belief (Dict[str, Any], optional): 신념 정보
        wisdom (Dict[str, Any], optional): 지혜 정보
        eora (Dict[str, Any], optional): 이오라 정보
        system (Dict[str, Any], optional): 시스템 정보
        history (List[Dict[str, Any]], optional): 대화 이력
        
    Returns:
        Dict[str, Any]: 분석된 문맥 정보
    """
    try:
        analyzer = get_analyzer()
        
        # 1. 기본 문맥 분석
        base_context = await analyzer.analyze(text)
        
        # 2. 텍스트 임베딩
        embedding = await embed_text_async(text)
        
        # 3. 세부 문맥 분석
        topic, topic_score = analyzer._analyze_topic(text)
        temporal = analyzer._analyze_temporal_context(text)
        semantic = await analyzer._analyze_semantic_context(text, embedding)
        interaction = analyzer._analyze_interaction_pattern(text)
        
        # 4. 결과 구성
        result = {
            "base_context": base_context,
            "topic": {
                "name": topic,
                "score": topic_score
            },
            "temporal": temporal,
            "semantic": semantic,
            "interaction": interaction,
            "metadata": {
                "context": context,
                "emotion": emotion,
                "belief": belief,
                "wisdom": wisdom,
                "eora": eora,
                "system": system
            }
        }
        
        # 5. 이력 업데이트
        if history:
            analyzer._update_context_history(result)
            
        return result
        
    except Exception as e:
        logger.error(f"⚠️ 문맥 분석 실패: {str(e)}")
        return {
            "base_context": None,
            "topic": {"name": "일상", "score": 0.5},
            "temporal": {"type": "present", "specificity": 0.5},
            "semantic": {"complexity": 0.5, "formality": 0.5, "specificity": 0.5},
            "interaction": {"type": "statement", "confidence": 0.5},
            "metadata": {
                "context": context,
                "emotion": emotion,
                "belief": belief,
                "wisdom": wisdom,
                "eora": eora,
                "system": system
            }
        } 