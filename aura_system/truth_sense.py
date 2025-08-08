"""
진리 인식 시스템
- 진리 인식
- 패턴 분석
- 진리 검증
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
from pathlib import Path

logger = logging.getLogger(__name__)

class TruthSense:
    """진리 인식 클래스"""
    
    def __init__(self):
        self.client = None
        self.model = "gpt-3.5-turbo"
        self.loop = None
        self.patterns_file = Path("memory/truth_patterns.json")
        self.max_tokens = 500
        self.temperature = 0.3
        self.min_confidence = 0.7
        self.patterns = self._load_patterns()
        
    async def initialize(self):
        """초기화"""
        try:
            # OpenAI 클라이언트 초기화
            self.client = AsyncOpenAI()
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(self.patterns_file), exist_ok=True)
            
            # 패턴 파일 로드 또는 생성
            if not self.patterns_file.exists():
                await self._create_initial_patterns()
                
            self.loop = asyncio.get_event_loop()
            logger.info("✅ 진리 인식 시스템 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 진리 인식 시스템 초기화 실패: {str(e)}")
            raise
            
    async def _create_initial_patterns(self):
        """초기 패턴 생성"""
        try:
            patterns = {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "patterns": [
                    {
                        "id": "truth_1",
                        "name": "보편적 진리",
                        "description": "모든 상황에 적용되는 근본적인 진리",
                        "examples": [
                            "변화는 불가피하다",
                            "모든 행동에는 결과가 따른다"
                        ]
                    },
                    {
                        "id": "truth_2",
                        "name": "윤리적 진리",
                        "description": "도덕과 윤리에 관한 진리",
                        "examples": [
                            "타인을 존중해야 한다",
                            "정직은 최선의 정책이다"
                        ]
                    },
                    {
                        "id": "truth_3",
                        "name": "실용적 진리",
                        "description": "일상 생활에 적용되는 실용적인 진리",
                        "examples": [
                            "연습은 완벽을 만든다",
                            "시간 관리는 성공의 열쇠다"
                        ]
                    }
                ]
            }
            
            with open(self.patterns_file, "w", encoding="utf-8") as f:
                json.dump(patterns, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"❌ 초기 패턴 생성 실패: {str(e)}")
            raise
            
    def _load_patterns(self) -> Dict[str, Any]:
        """진리 패턴 로드"""
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {"patterns": [], "threshold": 0.5}
        except Exception as e:
            logger.error(f"❌ 진리 패턴 로드 실패: {str(e)}")
            return {"patterns": [], "threshold": 0.5}
            
    async def recognize_truth(self, text: str) -> Dict[str, Any]:
        """진리 인식"""
        try:
            # 기본 결과
            result = {
                "is_truth": False,
                "confidence": 0.0,
                "matched_patterns": [],
                "text": text
            }
            
            # 패턴 매칭
            for pattern in self.patterns.get("patterns", []):
                if pattern.get("pattern", "") in text:
                    result["matched_patterns"].append(pattern)
                    result["confidence"] += pattern.get("weight", 0.0)
                    
            # 임계값 체크
            threshold = self.patterns.get("threshold", 0.5)
            result["is_truth"] = result["confidence"] >= threshold
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 진리 인식 수행 실패: {str(e)}")
            return {
                "is_truth": False,
                "confidence": 0.0,
                "matched_patterns": [],
                "text": text,
                "error": str(e)
            }
            
    async def _perform_recognition(
        self,
        patterns: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """진리 인식 수행"""
        try:
            # 시스템 프롬프트 구성
            system_prompt = f"""당신은 진리 인식 전문가입니다.
현재 알려진 진리 패턴:
{self._format_patterns(patterns['patterns'])}

주어진 맥락에서 진리를 인식하고 분류해주세요."""
            
            # 응답 생성
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(context, ensure_ascii=False)}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # 응답 파싱
            content = response.choices[0].message.content
            lines = content.split("\n")
            
            return {
                "content": lines[0],
                "type": lines[1] if len(lines) > 1 else "unknown",
                "description": lines[2] if len(lines) > 2 else "",
                "confidence": float(lines[3]) if len(lines) > 3 else 0.0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 진리 인식 수행 실패: {str(e)}")
            raise
            
    def _format_patterns(self, patterns: List[Dict[str, Any]]) -> str:
        """패턴 포맷팅"""
        formatted = []
        for pattern in patterns:
            formatted.append(f"- {pattern['name']}: {pattern['description']}")
            formatted.append("  예시:")
            for example in pattern["examples"]:
                formatted.append(f"  * {example}")
            formatted.append("")
            
        return "\n".join(formatted)
        
    async def get_patterns(self) -> Dict[str, Any]:
        """패턴 조회"""
        try:
            with open(self.patterns_file, "r", encoding="utf-8") as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"❌ 패턴 조회 실패: {str(e)}")
            return {"patterns": []}
            
    async def close(self):
        """리소스 정리"""
        try:
            if self.loop:
                self.loop.close()
                
        except Exception as e:
            logger.error(f"❌ 리소스 정리 실패: {str(e)}")

# 싱글톤 인스턴스
_truth_sense = None

def get_truth_sense():
    """진리 감지 인스턴스 반환"""
    global _truth_sense
    if _truth_sense is None:
        _truth_sense = TruthSense()
    return _truth_sense

async def analyze_truth(context: Dict[str, Any]) -> Dict[str, Any]:
    """진리 분석 수행"""
    engine = get_truth_sense()
    return await engine.process_truth(context) 