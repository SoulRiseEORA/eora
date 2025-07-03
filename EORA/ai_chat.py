"""
ai_chat.py

AI 채팅 모듈
- AI 인스턴스 관리
- 채팅 기능
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class EoraInstance:
    """이오라 인스턴스 클래스"""
    
    def __init__(self, name: str = "이오라"):
        self.name = name
        self.memory = []
        self.personality = {
            "말투": "부드럽고 따뜻한 어조",
            "감정톤": "희망적이고 섬세함",
            "에너지": "차분하고 안정적"
        }
    
    def chat(self, message: str) -> str:
        """
        채팅 응답 생성
        
        Args:
            message (str): 사용자 메시지
            
        Returns:
            str: AI 응답
        """
        try:
            # 간단한 응답 생성
            responses = [
                f"안녕하세요! {message}에 대해 이야기해보겠습니다.",
                f"흥미로운 질문이네요. {message}에 대해 생각해보겠습니다.",
                f"좋은 질문입니다. {message}에 대해 답변드리겠습니다."
            ]
            
            import random
            return random.choice(responses)
            
        except Exception as e:
            logger.error(f"채팅 응답 생성 실패: {str(e)}")
            return "죄송합니다. 응답을 생성할 수 없습니다."

# 전역 인스턴스
_eora_instance = None

def get_eora_instance() -> EoraInstance:
    """이오라 인스턴스 반환 (싱글톤)"""
    global _eora_instance
    if _eora_instance is None:
        _eora_instance = EoraInstance()
    return _eora_instance

# 테스트 함수
def test_ai_chat():
    """AI 채팅 테스트"""
    print("=== AI Chat 테스트 ===")
    
    instance = get_eora_instance()
    
    test_messages = [
        "안녕하세요",
        "인공지능에 대해 어떻게 생각하세요?",
        "오늘 날씨가 좋네요"
    ]
    
    for message in test_messages:
        response = instance.chat(message)
        print(f"사용자: {message}")
        print(f"AI: {response}")
        print()
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_ai_chat() 