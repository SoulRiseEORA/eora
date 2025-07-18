#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
토큰 계산기 - 정확한 토큰 수 계산 및 포인트 차감 시스템
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import tiktoken
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenCalculator:
    """정확한 토큰 계산 및 포인트 차감 시스템"""
    
    def __init__(self):
        """토큰 계산기 초기화"""
        load_dotenv()
        
        # OpenAI API 키 확인
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ OpenAI API 키가 설정되지 않았습니다.")
        
        # tiktoken 인코더 초기화
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4o")
            logger.info("✅ tiktoken 인코더 초기화 완료")
        except Exception as e:
            logger.error(f"❌ tiktoken 인코더 초기화 실패: {e}")
            self.encoding = None
        
        # 국가별 글자수 계산을 위한 정규식 패턴
        self.language_patterns = {
            'korean': re.compile(r'[가-힣]'),  # 한글
            'english': re.compile(r'[a-zA-Z]'),  # 영어
            'chinese': re.compile(r'[\u4e00-\u9fff]'),  # 한자
            'japanese': re.compile(r'[\u3040-\u309f\u30a0-\u30ff]'),  # 히라가나, 카타카나
            'numbers': re.compile(r'[0-9]'),  # 숫자
            'symbols': re.compile(r'[^\w\s가-힣\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]')  # 특수문자
        }
        
        # 포인트 차감 비율 (토큰의 2배)
        self.point_deduction_ratio = 2.0
        
        logger.info("✅ 토큰 계산기 초기화 완료")
    
    def count_tokens_exact(self, text: str) -> int:
        """정확한 토큰 수 계산 (tiktoken 사용)"""
        try:
            if not text or not isinstance(text, str):
                return 0
            
            if self.encoding:
                return len(self.encoding.encode(text))
            else:
                # tiktoken이 없는 경우 대체 계산
                return self._estimate_tokens(text)
                
        except Exception as e:
            logger.error(f"❌ 토큰 계산 실패: {e}")
            return self._estimate_tokens(text)
    
    def _estimate_tokens(self, text: str) -> int:
        """토큰 수 추정 (tiktoken이 없는 경우)"""
        try:
            # 언어별 글자수 분석
            char_counts = self.analyze_language_distribution(text)
            
            # 언어별 토큰 비율 (실제 GPT 토큰화 기준)
            token_ratios = {
                'korean': 1.0,      # 한글: 1글자 = 1토큰
                'english': 0.75,    # 영어: 4글자 = 3토큰
                'chinese': 1.0,     # 한자: 1글자 = 1토큰
                'japanese': 1.0,    # 일본어: 1글자 = 1토큰
                'numbers': 0.5,     # 숫자: 2글자 = 1토큰
                'symbols': 0.5      # 특수문자: 2글자 = 1토큰
            }
            
            total_tokens = 0
            for lang, count in char_counts.items():
                if lang in token_ratios:
                    total_tokens += int(count * token_ratios[lang])
            
            return max(1, total_tokens)  # 최소 1토큰
            
        except Exception as e:
            logger.error(f"❌ 토큰 추정 실패: {e}")
            # 기본 계산: 단어 수 * 1.3
            return max(1, len(text.split()) * 1.3)
    
    def analyze_language_distribution(self, text: str) -> Dict[str, int]:
        """텍스트의 언어별 글자수 분석"""
        try:
            char_counts = {
                'korean': 0,
                'english': 0,
                'chinese': 0,
                'japanese': 0,
                'numbers': 0,
                'symbols': 0
            }
            
            for char in text:
                if self.language_patterns['korean'].match(char):
                    char_counts['korean'] += 1
                elif self.language_patterns['english'].match(char):
                    char_counts['english'] += 1
                elif self.language_patterns['chinese'].match(char):
                    char_counts['chinese'] += 1
                elif self.language_patterns['japanese'].match(char):
                    char_counts['japanese'] += 1
                elif self.language_patterns['numbers'].match(char):
                    char_counts['numbers'] += 1
                elif self.language_patterns['symbols'].match(char):
                    char_counts['symbols'] += 1
            
            return char_counts
            
        except Exception as e:
            logger.error(f"❌ 언어 분석 실패: {e}")
            return {'korean': 0, 'english': 0, 'chinese': 0, 'japanese': 0, 'numbers': 0, 'symbols': 0}
    
    def calculate_chat_cost(self, user_message: str, ai_response: str) -> Dict[str, any]:
        """채팅 비용 계산 (사용자 메시지 + AI 응답)"""
        try:
            # 사용자 메시지 토큰 수
            user_tokens = self.count_tokens_exact(user_message)
            
            # AI 응답 토큰 수
            ai_tokens = self.count_tokens_exact(ai_response)
            
            # 총 토큰 수
            total_tokens = user_tokens + ai_tokens
            
            # 포인트 차감량 (토큰의 2배)
            points_to_deduct = int(total_tokens * self.point_deduction_ratio)
            
            # 언어별 분석
            user_lang_analysis = self.analyze_language_distribution(user_message)
            ai_lang_analysis = self.analyze_language_distribution(ai_response)
            
            return {
                'user_tokens': user_tokens,
                'ai_tokens': ai_tokens,
                'total_tokens': total_tokens,
                'points_to_deduct': points_to_deduct,
                'user_language_analysis': user_lang_analysis,
                'ai_language_analysis': ai_lang_analysis,
                'calculation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 채팅 비용 계산 실패: {e}")
            return {
                'user_tokens': 0,
                'ai_tokens': 0,
                'total_tokens': 0,
                'points_to_deduct': 0,
                'error': str(e)
            }
    
    def calculate_message_cost(self, message: str) -> Dict[str, any]:
        """단일 메시지 비용 계산"""
        try:
            tokens = self.count_tokens_exact(message)
            points = int(tokens * self.point_deduction_ratio)
            lang_analysis = self.analyze_language_distribution(message)
            
            return {
                'tokens': tokens,
                'points_to_deduct': points,
                'language_analysis': lang_analysis,
                'calculation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 메시지 비용 계산 실패: {e}")
            return {
                'tokens': 0,
                'points_to_deduct': 0,
                'error': str(e)
            }
    
    def validate_points_sufficient(self, current_points: int, required_points: int) -> Dict[str, any]:
        """포인트 충분성 검증"""
        try:
            is_sufficient = current_points >= required_points
            remaining_points = current_points - required_points if is_sufficient else current_points
            
            return {
                'is_sufficient': is_sufficient,
                'current_points': current_points,
                'required_points': required_points,
                'remaining_points': remaining_points,
                'can_proceed': is_sufficient
            }
            
        except Exception as e:
            logger.error(f"❌ 포인트 검증 실패: {e}")
            return {
                'is_sufficient': False,
                'current_points': 0,
                'required_points': required_points,
                'remaining_points': 0,
                'can_proceed': False,
                'error': str(e)
            }

# 전역 인스턴스
token_calculator = TokenCalculator()

def get_token_calculator() -> TokenCalculator:
    """토큰 계산기 인스턴스 반환"""
    return token_calculator 