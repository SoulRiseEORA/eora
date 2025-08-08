#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
토큰 사용량 계산 유틸리티
OpenAI API 호출에서 사용된 토큰을 측정하고 포인트 차감을 계산합니다.
"""

import tiktoken
import re
from typing import Optional, Dict, Any

class TokenCalculator:
    """토큰 사용량 계산 클래스"""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """
        초기화
        
        Args:
            model_name: OpenAI 모델 이름
        """
        self.model_name = model_name
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except Exception:
            # 기본 인코딩 사용
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        텍스트의 토큰 수를 계산합니다.
        
        Args:
            text: 계산할 텍스트
            
        Returns:
            토큰 수
        """
        if not text:
            return 0
        
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            print(f"⚠️ 토큰 계산 오류: {e}")
            # 대략적인 계산 (4자당 1토큰)
            return len(text) // 4
    
    def count_messages_tokens(self, messages: list) -> int:
        """
        메시지 리스트의 총 토큰 수를 계산합니다.
        
        Args:
            messages: OpenAI 메시지 형식의 리스트
            
        Returns:
            총 토큰 수
        """
        total_tokens = 0
        
        for message in messages:
            # 메시지 오버헤드 (role, content 등의 메타데이터)
            total_tokens += 4
            
            # role 토큰
            if "role" in message:
                total_tokens += self.count_tokens(message["role"])
            
            # content 토큰
            if "content" in message:
                total_tokens += self.count_tokens(message["content"])
        
        # 전체 메시지 오버헤드
        total_tokens += 2
        
        return total_tokens
    
    def extract_usage_from_response(self, response: Dict[Any, Any]) -> Optional[Dict[str, int]]:
        """
        OpenAI API 응답에서 토큰 사용량을 추출합니다.
        
        Args:
            response: OpenAI API 응답 객체
            
        Returns:
            토큰 사용량 딕셔너리 (prompt_tokens, completion_tokens, total_tokens)
        """
        try:
            if hasattr(response, 'usage'):
                usage = response.usage
                return {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            elif isinstance(response, dict) and "usage" in response:
                usage = response["usage"]
                return {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
        except Exception as e:
            print(f"⚠️ 토큰 사용량 추출 오류: {e}")
        
        return None
    
    def calculate_points_cost(self, token_usage: Dict[str, int], multiplier: float = 1.5) -> int:
        """
        토큰 사용량을 기반으로 포인트 비용을 계산합니다.
        
        Args:
            token_usage: 토큰 사용량 딕셔너리
            multiplier: 포인트 차감 배수 (기본값: 1.5 = 토큰 50% 추가 소비)
            
        Returns:
            차감할 포인트
        """
        if not token_usage:
            return 0
        
        total_tokens = token_usage.get("total_tokens", 0)
        points_cost = int(total_tokens * multiplier)
        
        # 최소 1포인트는 차감
        return max(1, points_cost)
    
    def estimate_tokens_before_request(self, prompt: str, max_tokens: int = 150) -> Dict[str, int]:
        """
        API 요청 전에 토큰 사용량을 추정합니다.
        
        Args:
            prompt: 입력 프롬프트
            max_tokens: 최대 생성 토큰 수
            
        Returns:
            추정 토큰 사용량
        """
        prompt_tokens = self.count_tokens(prompt)
        estimated_completion_tokens = min(max_tokens, prompt_tokens // 2)  # 대략적인 추정
        total_tokens = prompt_tokens + estimated_completion_tokens
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": estimated_completion_tokens,
            "total_tokens": total_tokens
        }
    
    def calculate_chat_cost(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """
        채팅 대화의 실제 비용을 계산합니다.
        
        Args:
            user_message: 사용자 메시지
            ai_response: AI 응답
            
        Returns:
            채팅 비용 정보
        """
        user_tokens = self.count_tokens(user_message)
        ai_tokens = self.count_tokens(ai_response)
        total_tokens = user_tokens + ai_tokens
        
        # 토큰의 1.5배 (50% 추가)로 포인트 계산
        token_usage = {
            "prompt_tokens": user_tokens,
            "completion_tokens": ai_tokens,
            "total_tokens": total_tokens
        }
        points_to_deduct = self.calculate_points_cost(token_usage)
        
        return {
            "user_tokens": user_tokens,
            "ai_tokens": ai_tokens,
            "total_tokens": total_tokens,
            "points_to_deduct": points_to_deduct
        }
    
    def calculate_message_cost(self, message: str) -> Dict[str, Any]:
        """
        단일 메시지의 예상 비용을 계산합니다.
        
        Args:
            message: 메시지 내용
            
        Returns:
            메시지 비용 정보
        """
        tokens = self.count_tokens(message)
        
        # 응답 예상 토큰 (입력의 50% 정도로 추정)
        estimated_response_tokens = max(50, tokens // 2)
        total_estimated_tokens = tokens + estimated_response_tokens
        
        token_usage = {
            "prompt_tokens": tokens,
            "completion_tokens": estimated_response_tokens,
            "total_tokens": total_estimated_tokens
        }
        points_to_deduct = self.calculate_points_cost(token_usage)
        
        return {
            "tokens": tokens,
            "estimated_response_tokens": estimated_response_tokens,
            "total_estimated_tokens": total_estimated_tokens,
            "points_to_deduct": points_to_deduct
        }

# 전역 토큰 계산기 인스턴스
token_calculator = TokenCalculator()

def get_token_calculator(model_name: str = "gpt-4o") -> TokenCalculator:
    """토큰 계산기 인스턴스를 반환합니다."""
    global token_calculator
    if token_calculator.model_name != model_name:
        token_calculator = TokenCalculator(model_name)
    return token_calculator 