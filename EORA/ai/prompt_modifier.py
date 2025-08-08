"""
AI Brain Prompt Modifier Module
AI 프롬프트 수정 및 관리 기능을 제공합니다.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptModifier:
    """AI 프롬프트 수정 및 관리 클래스"""
    
    def __init__(self):
        self.prompt_history = []
        self.modification_rules = {}
        
    def update_ai_prompt(self, 
                        current_prompt: str, 
                        modification_type: str = "enhancement",
                        context: Optional[Dict[str, Any]] = None) -> str:
        """
        AI 프롬프트를 수정하고 개선합니다.
        
        Args:
            current_prompt: 현재 프롬프트
            modification_type: 수정 타입 (enhancement, clarification, optimization)
            context: 수정 컨텍스트
            
        Returns:
            수정된 프롬프트
        """
        try:
            logger.info(f"프롬프트 수정 시작: {modification_type}")
            
            # 기본 수정 규칙 적용
            modified_prompt = self._apply_basic_modifications(current_prompt)
            
            # 타입별 수정 적용
            if modification_type == "enhancement":
                modified_prompt = self._enhance_prompt(modified_prompt, context)
            elif modification_type == "clarification":
                modified_prompt = self._clarify_prompt(modified_prompt, context)
            elif modification_type == "optimization":
                modified_prompt = self._optimize_prompt(modified_prompt, context)
            
            # 수정 이력 저장
            self._save_modification_history(current_prompt, modified_prompt, modification_type)
            
            logger.info("프롬프트 수정 완료")
            return modified_prompt
            
        except Exception as e:
            logger.error(f"프롬프트 수정 중 오류: {e}")
            return current_prompt
    
    def _apply_basic_modifications(self, prompt: str) -> str:
        """기본적인 프롬프트 수정을 적용합니다."""
        # 불필요한 공백 제거
        prompt = " ".join(prompt.split())
        
        # 명확성 개선
        if "명확하게" not in prompt:
            prompt = f"{prompt}\n\n명확하고 구체적으로 답변해주세요."
            
        return prompt
    
    def _enhance_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """프롬프트를 향상시킵니다."""
        enhancements = [
            "사용자의 의도를 정확히 파악하여 답변해주세요.",
            "실용적이고 구체적인 예시를 포함해주세요.",
            "필요한 경우 단계별로 설명해주세요."
        ]
        
        enhanced_prompt = prompt
        for enhancement in enhancements:
            if enhancement not in enhanced_prompt:
                enhanced_prompt += f"\n{enhancement}"
                
        return enhanced_prompt
    
    def _clarify_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """프롬프트를 명확하게 만듭니다."""
        clarifications = [
            "모호한 부분이 있다면 구체적으로 질문해주세요.",
            "답변의 범위와 깊이를 명시해주세요."
        ]
        
        clarified_prompt = prompt
        for clarification in clarifications:
            if clarification not in clarified_prompt:
                clarified_prompt += f"\n{clarification}"
                
        return clarified_prompt
    
    def _optimize_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """프롬프트를 최적화합니다."""
        # 중복 제거
        lines = prompt.split('\n')
        unique_lines = []
        for line in lines:
            if line.strip() and line.strip() not in unique_lines:
                unique_lines.append(line.strip())
        
        return '\n'.join(unique_lines)
    
    def _save_modification_history(self, 
                                 original_prompt: str, 
                                 modified_prompt: str, 
                                 modification_type: str):
        """수정 이력을 저장합니다."""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_prompt": original_prompt,
            "modified_prompt": modified_prompt,
            "modification_type": modification_type
        }
        
        self.prompt_history.append(history_entry)
        
        # 이력이 너무 많아지면 오래된 것부터 제거
        if len(self.prompt_history) > 100:
            self.prompt_history = self.prompt_history[-50:]
    
    def get_modification_history(self) -> list:
        """수정 이력을 반환합니다."""
        return self.prompt_history.copy()
    
    def reset_history(self):
        """수정 이력을 초기화합니다."""
        self.prompt_history = []

# 전역 인스턴스
_prompt_modifier = PromptModifier()

def update_ai_prompt(current_prompt: str, 
                    modification_type: str = "enhancement",
                    context: Optional[Dict[str, Any]] = None) -> str:
    """
    AI 프롬프트를 수정하는 전역 함수
    
    Args:
        current_prompt: 현재 프롬프트
        modification_type: 수정 타입
        context: 수정 컨텍스트
        
    Returns:
        수정된 프롬프트
    """
    return _prompt_modifier.update_ai_prompt(current_prompt, modification_type, context)

def get_prompt_modification_history() -> list:
    """프롬프트 수정 이력을 반환합니다."""
    return _prompt_modifier.get_modification_history()

def reset_prompt_modification_history():
    """프롬프트 수정 이력을 초기화합니다."""
    _prompt_modifier.reset_history() 