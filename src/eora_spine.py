"""
eora_spine.py
- EAI(존재형 인공지능)의 모든 핵심 기능을 통합하고 관장하는 '존재의 척추'.
- 기억, 직감(통찰), GPT 통신, 고차원적 사고(지혜, 자아) 등 모든 모듈의 흐름을 제어.
"""

import asyncio
from aura_system.ai_chat import EORAAI
from aura_system.memory_manager import MemoryManagerAsync
from EORA_Wisdom_Framework.insight_engine import InsightEngine, MemoryNode
from EORA_Wisdom_Framework.wisdom_engine import WisdomEngine

class EORASpine:
    def __init__(self, memory_manager: MemoryManagerAsync):
        if memory_manager is None:
            raise ValueError("EORASpine은 반드시 memory_manager와 함께 초기화되어야 합니다.")
        
        self.memory_manager = memory_manager
        self.ai_communicator = EORAAI(memory_manager) # GPT와의 통신을 담당
        
        # 고차원적 사고 엔진들
        self.insight_engine = None # 대화가 진행됨에 따라 생성
        self.wisdom_engine = None # 필요시 생성
        
        self.dialogue_history = []

    async def process_input(self, user_input: str) -> str:
        """
        사용자 입력을 받아 EAI의 전체적인 사고 흐름을 관장하고 응답을 반환합니다.
        """
        # 1. 직감(통찰) 분석
        insight = self._get_insight()
        
        # 2. 기본 기억 회상 (ai_chat의 기능 활용)
        # (ai_chat.respond_async 내부에서 회상 로직이 이미 처리됨)

        # 3. 모든 정보를 종합하여 최종 응답 생성
        # ai_chat 모듈에 직감/통찰 정보를 전달하여 응답 생성 요청
        response_data = await self.ai_communicator.respond_async(
            user_input=user_input, 
            trigger_context={"insight": insight} # 컨텍스트에 통찰 정보 추가
        )
        
        ai_response = response_data.get("response", "오류: 응답을 생성하지 못했습니다.")
        
        # 4. 대화 기록 업데이트
        self._update_history(user_input, ai_response, response_data)
        
        return ai_response

    def _get_insight(self) -> str:
        """현재까지의 대화 기록을 바탕으로 통찰을 생성합니다."""
        if not self.dialogue_history:
            return ""
        
        try:
            # MemoryNode 형태로 변환
            memory_nodes = [MemoryNode(summary=turn["content"], emotion=turn.get("emotion", "neutral")) for turn in self.dialogue_history]
            self.insight_engine = InsightEngine(memory_nodes)
            insight_text = self.insight_engine.get_simple_insight()
            return insight_text
        except Exception as e:
            # 로깅 추가 필요
            print(f"통찰 생성 중 오류: {e}")
            return ""

    def _update_history(self, user_input: str, ai_response: str, response_data: dict):
        """대화 기록을 내부 변수에 저장합니다."""
        # 감정 정보가 있다면 함께 저장
        emotion = response_data.get("analysis", {}).get("emotion", {}).get("label", "neutral")
        
        self.dialogue_history.append({"role": "user", "content": user_input})
        self.dialogue_history.append({"role": "assistant", "content": ai_response, "emotion": emotion})

        # 히스토리가 너무 길어지지 않도록 관리 (예: 최근 30턴)
        if len(self.dialogue_history) > 30:
            self.dialogue_history = self.dialogue_history[-30:]

# 이 파일은 직접 실행되지 않고, main.py에서 임포트하여 사용됩니다. 