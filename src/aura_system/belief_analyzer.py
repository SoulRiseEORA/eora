"""
belief_analyzer.py
- 신념 분석 시스템
- 텍스트에서 신념 패턴 추출 및 분석
"""

import numpy as np
from typing import Dict, List, Any, Tuple
import asyncio
from datetime import datetime
from aura_system.vector_store import embed_text_async
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

# 싱글톤 인스턴스
_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = BeliefAnalyzer()
    return _analyzer

class BeliefAnalyzer:
    def __init__(self):
        self._cache = {}
        self._cache_size = 1000
        self._belief_history = []
        self._max_history = 20
        
        # 신념 분석 가중치
        self.belief_weights = {
            "certainty": 0.3,
            "morality": 0.2,
            "value": 0.2,
            "identity": 0.2,
            "purpose": 0.1
        }
        
        # 신념 패턴
        self.belief_patterns = {
            "certainty": ["반드시", "절대로", "확실히", "분명히", "틀림없이"],
            "morality": ["옳다", "그르다", "선하다", "악하다", "도덕적"],
            "value": ["중요하다", "가치있다", "필요하다", "필수적", "꼭"],
            "identity": ["나는", "내가", "우리는", "우리가", "저는"],
            "purpose": ["목적", "이유", "의미", "가치", "방향"]
        }
        
        self.client = OpenAI()

    async def analyze(self, text: str) -> str:
        """신념 분석
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            str: 분석 결과
        """
        try:
            # 동기 함수를 비동기로 실행
            def analyze_belief():
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system", "content": "다음 텍스트의 신념 패턴을 분석해주세요. 확신, 가치관, 정체성 등을 파악해주세요."},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.3,
                        max_tokens=200
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"⚠️ 신념 분석 실패: {str(e)}")
                    return None
                    
            return await asyncio.to_thread(analyze_belief)
        except Exception as e:
            logger.error(f"⚠️ 신념 분석 실패: {str(e)}")
            return None

    def _analyze_certainty(self, text: str) -> Dict[str, Any]:
        """확신도 분석"""
        try:
            certainty = {
                "level": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 확신 마커 검색
            for marker in self.belief_patterns["certainty"]:
                if marker in text:
                    certainty["markers"].append(marker)
                    certainty["level"] += 0.2
                    
            # 확신도 정규화
            certainty["level"] = min(certainty["level"], 1.0)
            certainty["confidence"] = len(certainty["markers"]) * 0.2
            
            return certainty
            
        except Exception:
            return {"level": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_morality(self, text: str) -> Dict[str, Any]:
        """도덕성 분석"""
        try:
            morality = {
                "orientation": "neutral",
                "strength": 0.5,
                "markers": []
            }
            
            # 도덕 마커 검색
            for marker in self.belief_patterns["morality"]:
                if marker in text:
                    morality["markers"].append(marker)
                    morality["strength"] += 0.2
                    
            # 도덕성 정규화
            morality["strength"] = min(morality["strength"], 1.0)
            
            # 도덕적 방향 결정
            if morality["markers"]:
                positive_markers = ["옳다", "선하다"]
                negative_markers = ["그르다", "악하다"]
                
                positive_count = sum(1 for m in morality["markers"] if m in positive_markers)
                negative_count = sum(1 for m in morality["markers"] if m in negative_markers)
                
                if positive_count > negative_count:
                    morality["orientation"] = "positive"
                elif negative_count > positive_count:
                    morality["orientation"] = "negative"
                    
            return morality
            
        except Exception:
            return {"orientation": "neutral", "strength": 0.5, "markers": []}

    def _analyze_value(self, text: str) -> Dict[str, Any]:
        """가치 분석"""
        try:
            value = {
                "importance": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 가치 마커 검색
            for marker in self.belief_patterns["value"]:
                if marker in text:
                    value["markers"].append(marker)
                    value["importance"] += 0.2
                    
            # 가치 중요도 정규화
            value["importance"] = min(value["importance"], 1.0)
            value["confidence"] = len(value["markers"]) * 0.2
            
            return value
            
        except Exception:
            return {"importance": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_identity(self, text: str) -> Dict[str, Any]:
        """정체성 분석"""
        try:
            identity = {
                "type": "individual",
                "markers": [],
                "confidence": 0.5
            }
            
            # 정체성 마커 검색
            for marker in self.belief_patterns["identity"]:
                if marker in text:
                    identity["markers"].append(marker)
                    
            # 정체성 유형 결정
            if identity["markers"]:
                individual_markers = ["나는", "내가", "저는"]
                collective_markers = ["우리는", "우리가"]
                
                individual_count = sum(1 for m in identity["markers"] if m in individual_markers)
                collective_count = sum(1 for m in identity["markers"] if m in collective_markers)
                
                if collective_count > individual_count:
                    identity["type"] = "collective"
                    
            identity["confidence"] = len(identity["markers"]) * 0.2
            
            return identity
            
        except Exception:
            return {"type": "individual", "markers": [], "confidence": 0.5}

    def _analyze_purpose(self, text: str) -> Dict[str, Any]:
        """목적 분석"""
        try:
            purpose = {
                "clarity": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 목적 마커 검색
            for marker in self.belief_patterns["purpose"]:
                if marker in text:
                    purpose["markers"].append(marker)
                    purpose["clarity"] += 0.2
                    
            # 목적 명확도 정규화
            purpose["clarity"] = min(purpose["clarity"], 1.0)
            purpose["confidence"] = len(purpose["markers"]) * 0.2
            
            return purpose
            
        except Exception:
            return {"clarity": 0.5, "markers": [], "confidence": 0.5}

    def _update_belief_history(self, belief: Dict[str, Any]):
        """신념 이력 업데이트"""
        try:
            self._belief_history.append(belief)
            if len(self._belief_history) > self._max_history:
                self._belief_history.pop(0)
        except Exception as e:
            logger.error(f"⚠️ 신념 이력 업데이트 실패: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
        except Exception as e:
            logger.error(f"⚠️ 캐시 업데이트 실패: {str(e)}")

async def analyze_belief(text: str,
                        context: Dict[str, Any] = None,
                        emotion: Dict[str, Any] = None,
                        belief: Dict[str, Any] = None,
                        wisdom: Dict[str, Any] = None,
                        eora: Dict[str, Any] = None,
                        system: Dict[str, Any] = None) -> Dict[str, Any]:
    """신념 분석
    
    Args:
        text (str): 분석할 텍스트
        context (Dict[str, Any], optional): 문맥 정보
        emotion (Dict[str, Any], optional): 감정 정보
        belief (Dict[str, Any], optional): 신념 정보
        wisdom (Dict[str, Any], optional): 지혜 정보
        eora (Dict[str, Any], optional): 이오라 정보
        system (Dict[str, Any], optional): 시스템 정보
        
    Returns:
        Dict[str, Any]: 분석된 신념 정보
    """
    try:
        analyzer = get_analyzer()
        
        # 1. 기본 신념 분석
        base_belief = await analyzer.analyze(text)
        
        # 2. 세부 신념 분석
        certainty = analyzer._analyze_certainty(text)
        morality = analyzer._analyze_morality(text)
        value = analyzer._analyze_value(text)
        identity = analyzer._analyze_identity(text)
        purpose = analyzer._analyze_purpose(text)
        
        # 3. 결과 구성
        result = {
            "base_belief": base_belief,
            "certainty": certainty,
            "morality": morality,
            "value": value,
            "identity": identity,
            "purpose": purpose,
            "metadata": {
                "context": context,
                "emotion": emotion,
                "belief": belief,
                "wisdom": wisdom,
                "eora": eora,
                "system": system
            }
        }
        
        # 4. 이력 업데이트
        analyzer._update_belief_history(result)
        
        return result
        
    except Exception as e:
        logger.error(f"⚠️ 신념 분석 실패: {str(e)}")
        return {
            "base_belief": None,
            "certainty": {"level": 0.5, "markers": [], "confidence": 0.5},
            "morality": {"orientation": "neutral", "strength": 0.5, "markers": []},
            "value": {"importance": 0.5, "markers": [], "confidence": 0.5},
            "identity": {"type": "individual", "markers": [], "confidence": 0.5},
            "purpose": {"clarity": 0.5, "markers": [], "confidence": 0.5},
            "metadata": {
                "context": context,
                "emotion": emotion,
                "belief": belief,
                "wisdom": wisdom,
                "eora": eora,
                "system": system
            }
        } 