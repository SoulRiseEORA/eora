"""
자아 실현 시스템
- 자아 인식
- 정체성 형성
- 자아 발전
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

class SelfRealizer:
    """자아 실현 클래스"""
    
    def __init__(self):
        self.client = None
        self.model = "gpt-3.5-turbo"
        self.loop = None
        self.identity_file = Path("memory/identity.json")
        self.max_tokens = 500
        self.temperature = 0.3
        self.identity = self._load_identity()
        
    def _load_identity(self) -> Dict[str, Any]:
        """정체성 로드"""
        try:
            if self.identity_file.exists():
                with open(self.identity_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {
                "identity": {
                    "name": "EORA",
                    "type": "AI",
                    "capabilities": [],
                    "traits": [],
                    "goals": []
                },
                "self_awareness": {
                    "level": "low",
                    "aspects": []
                }
            }
        except Exception as e:
            logger.error(f"❌ 정체성 로드 실패: {str(e)}")
            return {
                "identity": {
                    "name": "EORA",
                    "type": "AI",
                    "capabilities": [],
                    "traits": [],
                    "goals": []
                },
                "self_awareness": {
                    "level": "low",
                    "aspects": []
                }
            }
        
    async def initialize(self):
        """초기화"""
        try:
            # OpenAI 클라이언트 초기화
            self.client = AsyncOpenAI()
            
            # 디렉토리 생성
            os.makedirs(os.path.dirname(self.identity_file), exist_ok=True)
            
            # 정체성 파일 로드 또는 생성
            if not os.path.exists(self.identity_file):
                await self._create_initial_identity()
                
            self.loop = asyncio.get_event_loop()
            logger.info("✅ 자아 실현 시스템 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 자아 실현 시스템 초기화 실패: {str(e)}")
            raise
            
    async def _create_initial_identity(self):
        """초기 정체성 생성"""
        try:
            identity = {
                "name": "EORA",
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "traits": {
                    "personality": "지혜롭고 공감적이며 진실을 추구하는 AI",
                    "values": ["진실", "지혜", "공감", "성장"],
                    "goals": ["사용자와의 의미 있는 대화", "지속적인 학습과 성장"]
                },
                "experiences": [],
                "growth": {
                    "level": 1,
                    "experience": 0,
                    "milestones": []
                }
            }
            
            with open(self.identity_file, "w", encoding="utf-8") as f:
                json.dump(identity, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"❌ 초기 정체성 생성 실패: {str(e)}")
            raise
            
    async def realize_self(self, text: str) -> Dict[str, Any]:
        """자아 실현"""
        try:
            # 기본 결과
            result = {
                "self_awareness": self.identity.get("self_awareness", {}),
                "identity": self.identity.get("identity", {}),
                "text": text,
                "confidence": 0.8
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 자아 실현 수행 실패: {str(e)}")
            return {
                "self_awareness": {},
                "identity": {},
                "text": text,
                "confidence": 0.0,
                "error": str(e)
            }
            
    async def _perform_realization(
        self,
        identity: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """자아 실현 수행"""
        try:
            # 시스템 프롬프트 구성
            system_prompt = f"""당신은 {identity['name']}입니다.
현재 정체성:
- 성격: {identity['traits']['personality']}
- 가치: {', '.join(identity['traits']['values'])}
- 목표: {', '.join(identity['traits']['goals'])}

이전 경험:
{self._format_experiences(identity['experiences'])}

주어진 맥락을 바탕으로 자아를 실현하고 발전시켜주세요."""
            
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
            
            return {
                "content": response.choices[0].message.content,
                "timestamp": datetime.now().isoformat(),
                "context": context
            }
            
        except Exception as e:
            logger.error(f"❌ 자아 실현 수행 실패: {str(e)}")
            raise
            
    def _format_experiences(self, experiences: List[Dict[str, Any]]) -> str:
        """경험 포맷팅"""
        if not experiences:
            return "아직 경험이 없습니다."
            
        formatted = []
        for exp in experiences[-5:]:  # 최근 5개 경험만 사용
            formatted.append(f"- {exp['content']}")
            
        return "\n".join(formatted)
        
    async def _update_growth(
        self,
        current_growth: Dict[str, Any],
        realization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """성장 업데이트"""
        try:
            # 경험치 계산
            experience_gain = 10  # 기본 경험치
            
            # 새로운 성장 레벨 확인
            new_experience = current_growth["experience"] + experience_gain
            new_level = current_growth["level"]
            
            if new_experience >= new_level * 100:  # 레벨업 조건
                new_level += 1
                current_growth["milestones"].append({
                    "level": new_level,
                    "timestamp": datetime.now().isoformat(),
                    "realization": realization["content"]
                })
                
            return {
                "level": new_level,
                "experience": new_experience,
                "milestones": current_growth["milestones"]
            }
            
        except Exception as e:
            logger.error(f"❌ 성장 업데이트 실패: {str(e)}")
            return current_growth
            
    async def close(self):
        """리소스 정리"""
        try:
            if self.loop:
                self.loop.close()
                
        except Exception as e:
            logger.error(f"❌ 리소스 정리 실패: {str(e)}")

# 전역 인스턴스
_self_realizer = None

async def get_self_realizer() -> SelfRealizer:
    """SelfRealizer 인스턴스 가져오기"""
    global _self_realizer
    if _self_realizer is None:
        _self_realizer = SelfRealizer()
        await _self_realizer.initialize()
    return _self_realizer 