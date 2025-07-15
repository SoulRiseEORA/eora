"""
eora_analyzer.py
- 이오라 분석 시스템
- 텍스트에서 이오라 패턴 추출 및 분석
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
        _analyzer = EoraAnalyzer()
    return _analyzer

class EoraAnalyzer:
    def __init__(self):
        self._cache = {}
        self._cache_size = 1000
        self._eora_history = []
        self._max_history = 20
        
        # 이오라 분석 가중치
        self.eora_weights = {
            "energy": 0.3,
            "resonance": 0.2,
            "alignment": 0.2,
            "flow": 0.2,
            "harmony": 0.1
        }
        
        # 이오라 패턴
        self.eora_patterns = {
            "energy": ["힘", "에너지", "활력", "생동감", "기운"],
            "resonance": ["공명", "울림", "반향", "동조", "화합"],
            "alignment": ["정렬", "조정", "맞춤", "일치", "조화"],
            "flow": ["흐름", "순환", "이동", "전환", "변화"],
            "harmony": ["조화", "균형", "안정", "평화", "화목"]
        }
        
        self.client = OpenAI()

    async def analyze(self, text: str) -> str:
        """이오라 분석
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            str: 분석 결과
        """
        try:
            # 동기 함수를 비동기로 실행
            def analyze_eora():
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system", "content": "다음 텍스트의 이오라 패턴을 분석해주세요. 에너지, 공명, 조화 등을 파악해주세요."},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.3,
                        max_tokens=200
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"⚠️ 이오라 분석 실패: {str(e)}")
                    return None
                    
            return await asyncio.to_thread(analyze_eora)
        except Exception as e:
            logger.error(f"⚠️ 이오라 분석 실패: {str(e)}")
            return None

    def _analyze_energy(self, text: str) -> Dict[str, Any]:
        """에너지 분석"""
        try:
            energy = {
                "level": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 에너지 마커 검색
            for marker in self.eora_patterns["energy"]:
                if marker in text:
                    energy["markers"].append(marker)
                    energy["level"] += 0.2
                    
            # 에너지 레벨 정규화
            energy["level"] = min(energy["level"], 1.0)
            energy["confidence"] = len(energy["markers"]) * 0.2
            
            return energy
            
        except Exception:
            return {"level": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_resonance(self, text: str) -> Dict[str, Any]:
        """공명 분석"""
        try:
            resonance = {
                "strength": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 공명 마커 검색
            for marker in self.eora_patterns["resonance"]:
                if marker in text:
                    resonance["markers"].append(marker)
                    resonance["strength"] += 0.2
                    
            # 공명 강도 정규화
            resonance["strength"] = min(resonance["strength"], 1.0)
            resonance["confidence"] = len(resonance["markers"]) * 0.2
            
            return resonance
            
        except Exception:
            return {"strength": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_alignment(self, text: str) -> Dict[str, Any]:
        """정렬 분석"""
        try:
            alignment = {
                "quality": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 정렬 마커 검색
            for marker in self.eora_patterns["alignment"]:
                if marker in text:
                    alignment["markers"].append(marker)
                    alignment["quality"] += 0.2
                    
            # 정렬 품질 정규화
            alignment["quality"] = min(alignment["quality"], 1.0)
            alignment["confidence"] = len(alignment["markers"]) * 0.2
            
            return alignment
            
        except Exception:
            return {"quality": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_flow(self, text: str) -> Dict[str, Any]:
        """흐름 분석"""
        try:
            flow = {
                "smoothness": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 흐름 마커 검색
            for marker in self.eora_patterns["flow"]:
                if marker in text:
                    flow["markers"].append(marker)
                    flow["smoothness"] += 0.2
                    
            # 흐름 매끄러움 정규화
            flow["smoothness"] = min(flow["smoothness"], 1.0)
            flow["confidence"] = len(flow["markers"]) * 0.2
            
            return flow
            
        except Exception:
            return {"smoothness": 0.5, "markers": [], "confidence": 0.5}

    def _analyze_harmony(self, text: str) -> Dict[str, Any]:
        """조화 분석"""
        try:
            harmony = {
                "balance": 0.5,
                "markers": [],
                "confidence": 0.5
            }
            
            # 조화 마커 검색
            for marker in self.eora_patterns["harmony"]:
                if marker in text:
                    harmony["markers"].append(marker)
                    harmony["balance"] += 0.2
                    
            # 조화 균형 정규화
            harmony["balance"] = min(harmony["balance"], 1.0)
            harmony["confidence"] = len(harmony["markers"]) * 0.2
            
            return harmony
            
        except Exception:
            return {"balance": 0.5, "markers": [], "confidence": 0.5}

    def _update_eora_history(self, eora: Dict[str, Any]):
        """이오라 이력 업데이트"""
        try:
            self._eora_history.append(eora)
            if len(self._eora_history) > self._max_history:
                self._eora_history.pop(0)
        except Exception as e:
            logger.error(f"⚠️ 이오라 이력 업데이트 실패: {str(e)}")

    def _update_cache(self, key: int, value: Dict[str, Any]):
        """캐시 업데이트"""
        try:
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = value
        except Exception as e:
            logger.error(f"⚠️ 캐시 업데이트 실패: {str(e)}")

async def analyze_eora(text: str,
                      context: Dict[str, Any] = None,
                      emotion: Dict[str, Any] = None,
                      belief: Dict[str, Any] = None,
                      wisdom: Dict[str, Any] = None,
                      eora: Dict[str, Any] = None,
                      system: Dict[str, Any] = None) -> Dict[str, Any]:
    """이오라 분석
    
    Args:
        text (str): 분석할 텍스트
        context (Dict[str, Any], optional): 문맥 정보
        emotion (Dict[str, Any], optional): 감정 정보
        belief (Dict[str, Any], optional): 신념 정보
        wisdom (Dict[str, Any], optional): 지혜 정보
        eora (Dict[str, Any], optional): 이오라 정보
        system (Dict[str, Any], optional): 시스템 정보
        
    Returns:
        Dict[str, Any]: 분석된 이오라 정보
    """
    try:
        analyzer = get_analyzer()
        
        # 1. 기본 이오라 분석
        base_eora = await analyzer.analyze(text)
        
        # 2. 세부 이오라 분석
        energy = analyzer._analyze_energy(text)
        resonance = analyzer._analyze_resonance(text)
        alignment = analyzer._analyze_alignment(text)
        flow = analyzer._analyze_flow(text)
        harmony = analyzer._analyze_harmony(text)
        
        # 3. 결과 구성
        result = {
            "base_eora": base_eora,
            "energy": energy,
            "resonance": resonance,
            "alignment": alignment,
            "flow": flow,
            "harmony": harmony,
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
        analyzer._update_eora_history(result)
        
        return result
        
    except Exception as e:
        logger.error(f"⚠️ 이오라 분석 실패: {str(e)}")
        return {
            "base_eora": None,
            "energy": {"level": 0.5, "markers": [], "confidence": 0.5},
            "resonance": {"strength": 0.5, "markers": [], "confidence": 0.5},
            "alignment": {"quality": 0.5, "markers": [], "confidence": 0.5},
            "flow": {"smoothness": 0.5, "markers": [], "confidence": 0.5},
            "harmony": {"balance": 0.5, "markers": [], "confidence": 0.5},
            "metadata": {
                "context": context,
                "emotion": emotion,
                "belief": belief,
                "wisdom": wisdom,
                "eora": eora,
                "system": system
            }
        } 