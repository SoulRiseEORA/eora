"""
system_analyzer.py
- 시스템 분석 시스템
- 텍스트에서 시스템 패턴 추출 및 분석
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
        _analyzer = SystemAnalyzer()
    return _analyzer

class SystemAnalyzer:
    def __init__(self):
        self._cache = {}
        self._cache_size = 1000
        self._system_history = []
        self._max_history = 20
        
        # 시스템 분석 가중치
        self.system_weights = {
            "structure": 0.3,
            "function": 0.2,
            "interaction": 0.2,
            "stability": 0.2,
            "efficiency": 0.1
        }
        
        # 시스템 패턴
        self.system_patterns = {
            "structure": ["구조", "체계", "틀", "형태", "모양"],
            "function": ["기능", "작용", "역할", "수행", "실행"],
            "interaction": ["상호작용", "교류", "소통", "연결", "관계"],
            "stability": ["안정", "견고", "지속", "유지", "보존"],
            "efficiency": ["효율", "성능", "생산성", "최적화", "개선"]
        }
        
        self.client = OpenAI()

    async def analyze(self, text: str) -> str:
        """시스템 분석
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            str: 분석 결과
        """
        try:
            # 동기 함수를 비동기로 실행
            def analyze_system():
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system", "content": "다음 텍스트의 시스템 패턴을 분석해주세요. 구조, 기능, 상호작용 등을 파악해주세요."},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.3,
                        max_tokens=200
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"⚠️ 시스템 분석 실패: {str(e)}")
                    return None
                    
            return await asyncio.to_thread(analyze_system)
        except Exception as e:
            logger.error(f"⚠️ 시스템 분석 실패: {str(e)}")
            return None

    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """구조 분석"""
        try:
            structure = {
                "clarity": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 구조 마커 검색
            for marker in self.system_patterns["structure"]:
                if marker in text:
                    structure["markers"].append(marker)
                    structure["clarity"] += 0.2
                    
            # 구조 명확도 정규화
            structure["clarity"] = min(structure["clarity"], 1.0)
            structure["confidence"] = len(structure["markers"]) * 0.2
            
            return structure
            
        except Exception:
            return {"clarity": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_function(self, text: str) -> Dict[str, Any]:
        """기능 분석"""
        try:
            function = {
                "effectiveness": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 기능 마커 검색
            for marker in self.system_patterns["function"]:
                if marker in text:
                    function["markers"].append(marker)
                    function["effectiveness"] += 0.2
                    
            # 기능 효과성 정규화
            function["effectiveness"] = min(function["effectiveness"], 1.0)
            function["confidence"] = len(function["markers"]) * 0.2
            
            return function
            
        except Exception:
            return {"effectiveness": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_interaction(self, text: str) -> Dict[str, Any]:
        """상호작용 분석"""
        try:
            interaction = {
                "quality": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 상호작용 마커 검색
            for marker in self.system_patterns["interaction"]:
                if marker in text:
                    interaction["markers"].append(marker)
                    interaction["quality"] += 0.2
                    
            # 상호작용 품질 정규화
            interaction["quality"] = min(interaction["quality"], 1.0)
            interaction["confidence"] = len(interaction["markers"]) * 0.2
            
            return interaction
            
        except Exception:
            return {"quality": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_stability(self, text: str) -> Dict[str, Any]:
        """안정성 분석"""
        try:
            stability = {
                "level": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 안정성 마커 검색
            for marker in self.system_patterns["stability"]:
                if marker in text:
                    stability["markers"].append(marker)
                    stability["level"] += 0.2
                    
            # 안정성 레벨 정규화
            stability["level"] = min(stability["level"], 1.0)
            stability["confidence"] = len(stability["markers"]) * 0.2
            
            return stability
            
        except Exception:
            return {"level": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_efficiency(self, text: str) -> Dict[str, Any]:
        """효율성 분석"""
        try:
            efficiency = {
                "performance": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 효율성 마커 검색
            for marker in self.system_patterns["efficiency"]:
                if marker in text:
                    efficiency["markers"].append(marker)
                    efficiency["performance"] += 0.2
                    
            # 효율성 성능 정규화
            efficiency["performance"] = min(efficiency["performance"], 1.0)
            efficiency["confidence"] = len(efficiency["markers"]) * 0.2
            
            return efficiency
            
        except Exception:
            return {"performance": 0.5, "markers": [], "confidence": 0.5}

    def _update_system_history(self, system: Dict[str, Any]):
        """시스템 이력 업데이트"""
        try:
            self._system_history.append(system)
            if len(self._system_history) > self._max_history:
                self._system_history.pop(0)
        except Exception as e:
            logger.error(f"⚠️ 시스템 이력 업데이트 실패: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
        except Exception as e:
            logger.error(f"⚠️ 캐시 업데이트 실패: {str(e)}")

async def analyze_system(text: str,
                        context: Dict[str, Any] = None,
                        emotion: Dict[str, Any] = None,
                        belief: Dict[str, Any] = None,
                        wisdom: Dict[str, Any] = None,
                        eora: Dict[str, Any] = None,
                        system: Dict[str, Any] = None) -> Dict[str, Any]:
    """시스템 분석
    
    Args:
        text (str): 분석할 텍스트
        context (Dict[str, Any], optional): 문맥 정보
        emotion (Dict[str, Any], optional): 감정 정보
        belief (Dict[str, Any], optional): 신념 정보
        wisdom (Dict[str, Any], optional): 지혜 정보
        eora (Dict[str, Any], optional): 이오라 정보
        system (Dict[str, Any], optional): 시스템 정보
        
    Returns:
        Dict[str, Any]: 분석된 시스템 정보
    """
    try:
        analyzer = get_analyzer()
        
        # 1. 기본 시스템 분석
        base_system = await analyzer.analyze(text)
        
        # 2. 세부 시스템 분석
        structure = analyzer._analyze_structure(text)
        function = analyzer._analyze_function(text)
        interaction = analyzer._analyze_interaction(text)
        stability = analyzer._analyze_stability(text)
        efficiency = analyzer._analyze_efficiency(text)
        
        # 3. 결과 구성
        result = {
            "base_system": base_system,
            "structure": structure,
            "function": function,
            "interaction": interaction,
            "stability": stability,
            "efficiency": efficiency,
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
        analyzer._update_system_history(result)
        
        return result
        
    except Exception as e:
        logger.error(f"⚠️ 시스템 분석 실패: {str(e)}")
        return {
            "base_system": None,
            "structure": {"clarity": 0.5, "markers": [], "confidence": 0.5},
            "function": {"effectiveness": 0.5, "markers": [], "confidence": 0.5},
            "interaction": {"quality": 0.5, "markers": [], "confidence": 0.5},
            "stability": {"level": 0.5, "markers": [], "confidence": 0.5},
            "efficiency": {"performance": 0.5, "markers": [], "confidence": 0.5},
            "metadata": {
                "context": context,
                "emotion": emotion,
                "belief": belief,
                "wisdom": wisdom,
                "eora": eora,
                "system": system
            }
        } 