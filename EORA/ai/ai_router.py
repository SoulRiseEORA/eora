"""
AI Router Module
AI 역할 분기 및 라우팅 기능을 제공합니다.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)

class AIRole(Enum):
    """AI 역할 열거형"""
    GENERAL = "general"
    ANALYZER = "analyzer"
    CREATOR = "creator"
    ADVISOR = "advisor"
    TEACHER = "teacher"
    CODER = "coder"
    RESEARCHER = "researcher"

class AIRouter:
    """AI 역할 분기 및 라우팅 클래스"""
    
    def __init__(self):
        self.role_handlers = {
            AIRole.GENERAL: self._handle_general,
            AIRole.ANALYZER: self._handle_analyzer,
            AIRole.CREATOR: self._handle_creator,
            AIRole.ADVISOR: self._handle_advisor,
            AIRole.TEACHER: self._handle_teacher,
            AIRole.CODER: self._handle_coder,
            AIRole.RESEARCHER: self._handle_researcher
        }
        
        self.role_prompts = {
            AIRole.GENERAL: "일반적인 대화와 질문에 답변합니다.",
            AIRole.ANALYZER: "데이터와 정보를 분석하고 인사이트를 제공합니다.",
            AIRole.CREATOR: "창의적인 아이디어와 콘텐츠를 생성합니다.",
            AIRole.ADVISOR: "전문적인 조언과 가이드를 제공합니다.",
            AIRole.TEACHER: "교육적이고 학습에 도움이 되는 답변을 제공합니다.",
            AIRole.CODER: "프로그래밍과 기술적 문제를 해결합니다.",
            AIRole.RESEARCHER: "연구와 탐구를 통해 깊이 있는 정보를 제공합니다."
        }
    
    def route_request(self, 
                     user_input: str, 
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        사용자 입력을 분석하여 적절한 AI 역할로 라우팅합니다.
        
        Args:
            user_input: 사용자 입력
            context: 컨텍스트 정보
            
        Returns:
            라우팅 결과
        """
        try:
            # 역할 결정
            role = self._determine_role(user_input, context)
            
            # 역할별 처리
            result = self.role_handlers[role](user_input, context)
            
            return {
                "role": role.value,
                "role_prompt": self.role_prompts[role],
                "result": result,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"라우팅 중 오류: {e}")
            return {
                "role": AIRole.GENERAL.value,
                "role_prompt": self.role_prompts[AIRole.GENERAL],
                "result": f"오류가 발생했습니다: {str(e)}",
                "success": False
            }
    
    def _determine_role(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AIRole:
        """사용자 입력을 분석하여 적절한 역할을 결정합니다."""
        input_lower = user_input.lower()
        
        # 키워드 기반 역할 결정
        if any(keyword in input_lower for keyword in ["분석", "데이터", "통계", "인사이트"]):
            return AIRole.ANALYZER
        elif any(keyword in input_lower for keyword in ["생성", "만들", "창작", "아이디어"]):
            return AIRole.CREATOR
        elif any(keyword in input_lower for keyword in ["조언", "추천", "가이드", "어떻게"]):
            return AIRole.ADVISOR
        elif any(keyword in input_lower for keyword in ["설명", "가르쳐", "학습", "교육"]):
            return AIRole.TEACHER
        elif any(keyword in input_lower for keyword in ["코드", "프로그램", "버그", "개발"]):
            return AIRole.CODER
        elif any(keyword in input_lower for keyword in ["연구", "탐구", "조사", "분석"]):
            return AIRole.RESEARCHER
        else:
            return AIRole.GENERAL
    
    def _handle_general(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """일반적인 대화 처리"""
        return f"안녕하세요! {user_input}에 대해 이야기해보겠습니다."
    
    def _handle_analyzer(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """분석 역할 처리"""
        return f"분석 모드로 전환했습니다. {user_input}에 대한 심층 분석을 제공하겠습니다."
    
    def _handle_creator(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """창작 역할 처리"""
        return f"창작 모드로 전환했습니다. {user_input}에 대한 창의적인 아이디어를 제시하겠습니다."
    
    def _handle_advisor(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """조언 역할 처리"""
        return f"조언 모드로 전환했습니다. {user_input}에 대한 전문적인 조언을 제공하겠습니다."
    
    def _handle_teacher(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """교육 역할 처리"""
        return f"교육 모드로 전환했습니다. {user_input}에 대해 단계별로 설명해드리겠습니다."
    
    def _handle_coder(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """코딩 역할 처리"""
        return f"코딩 모드로 전환했습니다. {user_input}에 대한 기술적 해결책을 제시하겠습니다."
    
    def _handle_researcher(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """연구 역할 처리"""
        return f"연구 모드로 전환했습니다. {user_input}에 대한 깊이 있는 연구 결과를 제공하겠습니다."
    
    def get_available_roles(self) -> List[Dict[str, str]]:
        """사용 가능한 역할 목록을 반환합니다."""
        return [
            {"role": role.value, "description": self.role_prompts[role]}
            for role in AIRole
        ]
    
    def set_custom_role(self, role_name: str, description: str, handler_func):
        """사용자 정의 역할을 추가합니다."""
        custom_role = AIRole(role_name)
        self.role_prompts[custom_role] = description
        self.role_handlers[custom_role] = handler_func
        logger.info(f"사용자 정의 역할 추가: {role_name}")

# 전역 인스턴스
_ai_router = AIRouter()

def route_ai_request(user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    AI 요청을 라우팅하는 전역 함수
    
    Args:
        user_input: 사용자 입력
        context: 컨텍스트 정보
        
    Returns:
        라우팅 결과
    """
    return _ai_router.route_request(user_input, context)

def get_ai_roles() -> List[Dict[str, str]]:
    """사용 가능한 AI 역할 목록을 반환합니다."""
    return _ai_router.get_available_roles()