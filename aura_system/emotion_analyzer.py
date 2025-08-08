import numpy as np
from typing import Dict, List, Tuple, Any
import asyncio
from datetime import datetime
from aura_system.vector_store import embed_text_async
import logging

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    def __init__(self):
        self.emotion_weights = {
            "joy": {"weight": 1.2, "threshold": 0.6},
            "sadness": {"weight": 0.8, "threshold": 0.5},
            "anger": {"weight": 1.1, "threshold": 0.55},
            "fear": {"weight": 0.9, "threshold": 0.5},
            "surprise": {"weight": 1.0, "threshold": 0.6},
            "neutral": {"weight": 1.0, "threshold": 0.4}
        }
        
        self.emotion_keywords = {
            "joy": ["행복", "기쁨", "즐거움", "웃음", "감사", "사랑", "희망", "기대", "만족", "즐겁다", 
                   "기쁘다", "행복하다", "감사하다", "사랑스럽다", "희망적이다", "기대된다", "만족스럽다"],
            "sadness": ["슬픔", "우울", "외로움", "상실", "후회", "비통", "허탈", "공허", "절망", "낙담",
                       "슬프다", "우울하다", "외롭다", "상실감", "후회된다", "비통하다", "허탈하다"],
            "anger": ["분노", "화남", "짜증", "불만", "억울", "불공평", "질투", "반항", "격분", "분개",
                     "화가나다", "짜증나다", "불만스럽다", "억울하다", "불공평하다", "질투나다"],
            "fear": ["두려움", "불안", "걱정", "공포", "긴장", "불편", "위기", "혼란", "떨림", "망설임",
                    "두렵다", "불안하다", "걱정된다", "공포스럽다", "긴장된다", "불편하다"],
            "surprise": ["놀람", "경악", "충격", "당황", "의외", "예상치못", "갑작스러움", "충격적", "놀랍다",
                        "경악스럽다", "충격적이다", "당황스럽다", "의외다", "예상치못했다"]
        }
        
        self._cache = {}
        self._cache_size = 1000
        self._emotion_history = []
        self._max_history = 10

    async def analyze_emotion(self,
                             text: str,
                             context: Dict[str, Any] = None,
                             emotion: Dict[str, Any] = None,
                             belief: Dict[str, Any] = None,
                             wisdom: Dict[str, Any] = None,
                             eora: Dict[str, Any] = None,
                             system: Dict[str, Any] = None) -> Tuple[str, float, Dict[str, float]]:
        """감정 분석 수행
        
        Args:
            text (str): 분석할 텍스트
            context (Dict[str, Any], optional): 문맥 정보
            emotion (Dict[str, Any], optional): 감정 정보
            belief (Dict[str, Any], optional): 신념 정보
            wisdom (Dict[str, Any], optional): 지혜 정보
            eora (Dict[str, Any], optional): 이오라 정보
            system (Dict[str, Any], optional): 시스템 정보
            
        Returns:
            Tuple[str, float, Dict[str, float]]: (주요 감정, 강도, 감정 점수)
        """
        try:
            # 1. 캐시 확인
            cache_key = hash(text)
            if cache_key in self._cache:
                return self._cache[cache_key]

            # 2. 텍스트 임베딩
            embedding = await embed_text_async(text)
            
            # 3. 감정 점수 계산
            emotion_scores = await self._calculate_emotion_scores(
                text=text,
                embedding=embedding,
                context=context,
                emotion=emotion,
                belief=belief,
                wisdom=wisdom,
                eora=eora,
                system=system
            )
            
            # 4. 감정 강도 계산
            intensity = self._calculate_emotion_intensity(emotion_scores)
            
            # 5. 최종 감정 결정
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            # 6. 감정 이력 업데이트
            self._update_emotion_history(primary_emotion[0], intensity)
            
            # 7. 결과 캐싱
            result = (primary_emotion[0], intensity, emotion_scores)
            self._update_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"⚠️ 감정 분석 실패: {str(e)}")
            return "neutral", 0.5, {"neutral": 1.0}

    async def _calculate_emotion_scores(self,
                                        text: str,
                                        embedding: List[float],
                                        context: Dict[str, Any] = None,
                                        emotion: Dict[str, Any] = None,
                                        belief: Dict[str, Any] = None,
                                        wisdom: Dict[str, Any] = None,
                                        eora: Dict[str, Any] = None,
                                        system: Dict[str, Any] = None) -> Dict[str, float]:
        """감정 점수 계산"""
        try:
            # 1. 키워드 기반 점수
            keyword_scores = self._calculate_keyword_scores(text)
            
            # 2. 임베딩 기반 점수
            embedding_scores = self._calculate_embedding_scores(embedding)
            
            # 3. 문맥 기반 점수
            context_scores = self._calculate_context_scores(context) if context else {}
            
            # 4. 감정 이력 기반 점수
            history_scores = self._calculate_history_scores()
            
            # 5. 점수 통합
            final_scores = {}
            for emotion in self.emotion_weights.keys():
                scores = [
                    keyword_scores.get(emotion, 0.0),
                    embedding_scores.get(emotion, 0.0),
                    context_scores.get(emotion, 0.0),
                    history_scores.get(emotion, 0.0)
                ]
                weights = [0.4, 0.3, 0.2, 0.1]  # 가중치 조정
                final_scores[emotion] = sum(s * w for s, w in zip(scores, weights))
            
            # 6. 정규화
            total = sum(final_scores.values())
            if total > 0:
                final_scores = {k: v/total for k, v in final_scores.items()}
            
            return final_scores
            
        except Exception as e:
            logger.error(f"감정 점수 계산 중 오류: {str(e)}")
            return {"neutral": 1.0}

    def _calculate_keyword_scores(self, text: str) -> Dict[str, float]:
        """키워드 기반 감정 점수 계산"""
        scores = {emotion: 0.0 for emotion in self.emotion_weights.keys()}
        
        for emotion, keywords in self.emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text)
            if count > 0:
                scores[emotion] = min(0.3 + (count * 0.1), 1.0)
        
        return scores

    def _calculate_embedding_scores(self, embedding: List[float]) -> Dict[str, float]:
        """임베딩 기반 감정 점수 계산"""
        try:
            # 임베딩을 감정 차원으로 매핑
            emotion_embeddings = {
                "joy": [0.8, 0.2, 0.1],
                "sadness": [0.1, 0.8, 0.2],
                "anger": [0.7, 0.6, 0.3],
                "fear": [0.2, 0.7, 0.8],
                "surprise": [0.5, 0.5, 0.5],
                "neutral": [0.3, 0.3, 0.3]
            }
            
            # 임베딩 차원 축소
            reduced_embedding = np.mean(np.array(embedding).reshape(-1, 3), axis=0)
            
            # 각 감정과의 유사도 계산
            scores = {}
            for emotion, emotion_emb in emotion_embeddings.items():
                similarity = np.dot(reduced_embedding, emotion_emb) / (
                    np.linalg.norm(reduced_embedding) * np.linalg.norm(emotion_emb)
                )
                scores[emotion] = float(similarity)
            
            return scores
            
        except Exception:
            return {"neutral": 1.0}

    def _calculate_context_scores(self, context: Dict[str, Any]) -> Dict[str, float]:
        """문맥 기반 감정 점수 계산"""
        scores = {emotion: 0.0 for emotion in self.emotion_weights.keys()}
        
        if not context:
            return scores
            
        # 이전 감정 상태 반영
        if "previous_emotion" in context:
            prev_emotion = context["previous_emotion"]
            if prev_emotion in scores:
                scores[prev_emotion] += 0.2
        
        # 대화 주제 반영
        if "topic" in context:
            topic = context["topic"].lower()
            if "긍정" in topic or "기쁨" in topic:
                scores["joy"] += 0.3
            elif "부정" in topic or "슬픔" in topic:
                scores["sadness"] += 0.3
        
        return scores

    def _calculate_history_scores(self) -> Dict[str, float]:
        """감정 이력 기반 점수 계산"""
        scores = {emotion: 0.0 for emotion in self.emotion_weights.keys()}
        
        if not self._emotion_history:
            return scores
            
        # 최근 감정 이력 분석
        recent_emotions = [e[0] for e in self._emotion_history[-3:]]
        for emotion in recent_emotions:
            if emotion in scores:
                scores[emotion] += 0.1
        
        return scores

    def _calculate_emotion_intensity(self, emotion_scores: Dict[str, float]) -> float:
        """감정 강도 계산"""
        try:
            # 최고 점수 감정의 강도 계산
            max_score = max(emotion_scores.values())
            max_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            
            # 임계값 기반 강도 조정
            threshold = self.emotion_weights[max_emotion]["threshold"]
            intensity = (max_score - threshold) / (1 - threshold) if max_score > threshold else 0.0
            
            return min(max(intensity, 0.0), 1.0)
            
        except Exception:
            return 0.5

    def _update_emotion_history(self, emotion: str, intensity: float):
        """감정 이력 업데이트"""
        self._emotion_history.append((emotion, intensity, datetime.now()))
        if len(self._emotion_history) > self._max_history:
            self._emotion_history.pop(0)

    def _update_cache(self, key: int, value: Tuple[str, float, Dict[str, float]]):
        """캐시 업데이트"""
        if len(self._cache) >= self._cache_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = value

_analyzer_instance = EmotionAnalyzer()

async def analyze_emotion(text: str,
                         context: Dict[str, Any] = None,
                         emotion: Dict[str, Any] = None,
                         belief: Dict[str, Any] = None,
                         wisdom: Dict[str, Any] = None,
                         eora: Dict[str, Any] = None,
                         system: Dict[str, Any] = None) -> Tuple[str, float, Dict[str, float]]:
    """감정 분석 수행 (싱글톤 인스턴스 사용)"""
    return await _analyzer_instance.analyze_emotion(
        text=text,
        context=context,
        emotion=emotion,
        belief=belief,
        wisdom=wisdom,
        eora=eora,
        system=system
    ) 