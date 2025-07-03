"""
wisdom_analyzer.py
- 지혜 분석 시스템
- 텍스트에서 지혜 패턴 추출 및 분석
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
        _analyzer = WisdomAnalyzer()
    return _analyzer

class WisdomAnalyzer:
    def __init__(self):
        self._cache = {}
        self._cache_size = 1000
        self._wisdom_history = []
        self._max_history = 20
        
        # 지혜 분석 가중치
        self.wisdom_weights = {
            "insight": 0.3,
            "experience": 0.2,
            "reflection": 0.2,
            "adaptation": 0.2,
            "balance": 0.1
        }
        
        # 지혜 패턴
        self.wisdom_patterns = {
            "insight": ["이해하다", "깨닫다", "알다", "파악하다", "인식하다"],
            "experience": ["경험", "체험", "시행착오", "배움", "성장"],
            "reflection": ["생각하다", "고민하다", "성찰하다", "되돌아보다", "분석하다"],
            "adaptation": ["적응", "변화", "발전", "개선", "혁신"],
            "balance": ["균형", "조화", "중용", "절제", "조절"]
        }
        
        self.client = OpenAI()

    async def analyze(self, text: str) -> str:
        """지혜 분석
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            str: 분석 결과
        """
        try:
            # 동기 함수를 비동기로 실행
            def analyze_wisdom():
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system", "content": "다음 텍스트의 지혜 패턴을 분석해주세요. 통찰, 경험, 성찰 등을 파악해주세요."},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.3,
                        max_tokens=200
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"⚠️ 지혜 분석 실패: {str(e)}")
                    return None
                    
            return await asyncio.to_thread(analyze_wisdom)
        except Exception as e:
            logger.error(f"⚠️ 지혜 분석 실패: {str(e)}")
            return None

    def _analyze_insight(self, text: str) -> Dict[str, Any]:
        """통찰 분석"""
        try:
            insight = {
                "depth": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 통찰 마커 검색
            for marker in self.wisdom_patterns["insight"]:
                if marker in text:
                    insight["markers"].append(marker)
                    insight["depth"] += 0.2
                    
            # 통찰 깊이 정규화
            insight["depth"] = min(insight["depth"], 1.0)
            insight["confidence"] = len(insight["markers"]) * 0.2
            
            return insight
            
        except Exception:
            return {"depth": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_experience(self, text: str) -> Dict[str, Any]:
        """경험 분석"""
        try:
            experience = {
                "richness": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 경험 마커 검색
            for marker in self.wisdom_patterns["experience"]:
                if marker in text:
                    experience["markers"].append(marker)
                    experience["richness"] += 0.2
                    
            # 경험 풍부도 정규화
            experience["richness"] = min(experience["richness"], 1.0)
            experience["confidence"] = len(experience["markers"]) * 0.2
            
            return experience
            
        except Exception:
            return {"richness": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_reflection(self, text: str) -> Dict[str, Any]:
        """성찰 분석"""
        try:
            reflection = {
                "quality": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 성찰 마커 검색
            for marker in self.wisdom_patterns["reflection"]:
                if marker in text:
                    reflection["markers"].append(marker)
                    reflection["quality"] += 0.2
                    
            # 성찰 품질 정규화
            reflection["quality"] = min(reflection["quality"], 1.0)
            reflection["confidence"] = len(reflection["markers"]) * 0.2
            
            return reflection
            
        except Exception:
            return {"quality": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_adaptation(self, text: str) -> Dict[str, Any]:
        """적응 분석"""
        try:
            adaptation = {
                "flexibility": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 적응 마커 검색
            for marker in self.wisdom_patterns["adaptation"]:
                if marker in text:
                    adaptation["markers"].append(marker)
                    adaptation["flexibility"] += 0.2
                    
            # 적응 유연성 정규화
            adaptation["flexibility"] = min(adaptation["flexibility"], 1.0)
            adaptation["confidence"] = len(adaptation["markers"]) * 0.2
            
            return adaptation
            
        except Exception:
            return {"flexibility": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_balance(self, text: str) -> Dict[str, Any]:
        """균형 분석"""
        try:
            balance = {
                "harmony": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 균형 마커 검색
            for marker in self.wisdom_patterns["balance"]:
                if marker in text:
                    balance["markers"].append(marker)
                    balance["harmony"] += 0.2
                    
            # 균형 조화도 정규화
            balance["harmony"] = min(balance["harmony"], 1.0)
            balance["confidence"] = len(balance["markers"]) * 0.2
            
            return balance
            
        except Exception:
            return {"harmony": 0.5, "markers": [], "confidence": 0.5}

    def _update_wisdom_history(self, wisdom: Dict[str, Any]):
        """지혜 이력 업데이트"""
        try:
            self._wisdom_history.append(wisdom)
            if len(self._wisdom_history) > self._max_history:
                self._wisdom_history.pop(0)
        except Exception as e:
            logger.error(f"⚠️ 지혜 이력 업데이트 실패: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
        except Exception as e:
            logger.error(f"⚠️ 캐시 업데이트 실패: {str(e)}")

async def analyze_wisdom(text: str,
                        context: Dict[str, Any] = None,
                        emotion: Dict[str, Any] = None,
                        belief: Dict[str, Any] = None,
                        wisdom: Dict[str, Any] = None,
                        eora: Dict[str, Any] = None,
                        system: Dict[str, Any] = None) -> Dict[str, Any]:
    """지혜 분석
    
    Args:
        text (str): 분석할 텍스트
        context (Dict[str, Any], optional): 문맥 정보
        emotion (Dict[str, Any], optional): 감정 정보
        belief (Dict[str, Any], optional): 신념 정보
        wisdom (Dict[str, Any], optional): 지혜 정보
        eora (Dict[str, Any], optional): 이오라 정보
        system (Dict[str, Any], optional): 시스템 정보
        
    Returns:
        Dict[str, Any]: 분석된 지혜 정보
    """
    try:
        analyzer = get_analyzer()
        
        # 1. 기본 지혜 분석
        base_wisdom = await analyzer.analyze(text)
        
        # 2. 세부 지혜 분석
        insight = analyzer._analyze_insight(text)
        experience = analyzer._analyze_experience(text)
        reflection = analyzer._analyze_reflection(text)
        adaptation = analyzer._analyze_adaptation(text)
        balance = analyzer._analyze_balance(text)
        
        # 3. 결과 구성
        result = {
            "base_wisdom": base_wisdom,
            "insight": insight,
            "experience": experience,
            "reflection": reflection,
            "adaptation": adaptation,
            "balance": balance,
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
        analyzer._update_wisdom_history(result)
        
        return result
        
    except Exception as e:
        logger.error(f"⚠️ 지혜 분석 실패: {str(e)}")
        return {
            "base_wisdom": None,
            "insight": {"depth": 0.5, "markers": [], "confidence": 0.5},
            "experience": {"richness": 0.5, "markers": [], "confidence": 0.5},
            "reflection": {"quality": 0.5, "markers": [], "confidence": 0.5},
            "adaptation": {"flexibility": 0.5, "markers": [], "confidence": 0.5},
            "balance": {"harmony": 0.5, "markers": [], "confidence": 0.5},
            "metadata": {
                "context": context,
                "emotion": emotion,
                "belief": belief,
                "wisdom": wisdom,
                "eora": eora,
                "system": system
            }
        } 