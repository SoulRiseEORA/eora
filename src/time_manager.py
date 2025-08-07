#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 시간 관리 시스템
회상 시스템의 시간 자동 조정 및 상대적 시간 표현
"""

import datetime
from typing import Dict, Any, Optional, List
import re


class TimeManager:
    """시간 관리 및 상대적 시간 표현 클래스"""
    
    def __init__(self):
        self.relative_time_map = {
            # 한국어 상대적 시간 표현
            "방금": {"minutes": 0, "hours": 0, "days": 0},
            "조금 전": {"minutes": -5, "hours": 0, "days": 0},
            "아까": {"minutes": -30, "hours": 0, "days": 0},
            "오늘": {"minutes": 0, "hours": 0, "days": 0},
            "어제": {"minutes": 0, "hours": 0, "days": -1},
            "그저께": {"minutes": 0, "hours": 0, "days": -2},
            "엊그제": {"minutes": 0, "hours": 0, "days": -2},
            "그끄저께": {"minutes": 0, "hours": 0, "days": -3},
            "사흘전": {"minutes": 0, "hours": 0, "days": -3},
            "나흘전": {"minutes": 0, "hours": 0, "days": -4},
            "닷새전": {"minutes": 0, "hours": 0, "days": -5},
            "엿새전": {"minutes": 0, "hours": 0, "days": -6},
            "일주일전": {"minutes": 0, "hours": 0, "days": -7},
            "지난주": {"minutes": 0, "hours": 0, "days": -7},
            "이번주": {"minutes": 0, "hours": 0, "days": 0},
            "지난달": {"minutes": 0, "hours": 0, "days": -30},
            "이번달": {"minutes": 0, "hours": 0, "days": 0},
            "작년": {"minutes": 0, "hours": 0, "days": -365},
            "올해": {"minutes": 0, "hours": 0, "days": 0},
            
            # 시간대별 표현
            "새벽": {"minutes": 0, "hours": 3, "days": 0},
            "아침": {"minutes": 0, "hours": 8, "days": 0},
            "오전": {"minutes": 0, "hours": 10, "days": 0},
            "점심": {"minutes": 0, "hours": 12, "days": 0},
            "오후": {"minutes": 0, "hours": 15, "days": 0},
            "저녁": {"minutes": 0, "hours": 18, "days": 0},
            "밤": {"minutes": 0, "hours": 21, "days": 0},
            
            # 영어 표현
            "now": {"minutes": 0, "hours": 0, "days": 0},
            "today": {"minutes": 0, "hours": 0, "days": 0},
            "yesterday": {"minutes": 0, "hours": 0, "days": -1},
            "last week": {"minutes": 0, "hours": 0, "days": -7},
            "this week": {"minutes": 0, "hours": 0, "days": 0},
            "last month": {"minutes": 0, "hours": 0, "days": -30},
            "this month": {"minutes": 0, "hours": 0, "days": 0},
        }
        
        # 시간 패턴 (숫자 + 단위)
        self.time_patterns = [
            (r'(\d+)분\s*전', lambda m: {"minutes": -int(m.group(1)), "hours": 0, "days": 0}),
            (r'(\d+)시간\s*전', lambda m: {"minutes": 0, "hours": -int(m.group(1)), "days": 0}),
            (r'(\d+)일\s*전', lambda m: {"minutes": 0, "hours": 0, "days": -int(m.group(1))}),
            (r'(\d+)주\s*전', lambda m: {"minutes": 0, "hours": 0, "days": -int(m.group(1)) * 7}),
            (r'(\d+)달\s*전', lambda m: {"minutes": 0, "hours": 0, "days": -int(m.group(1)) * 30}),
            (r'(\d+)년\s*전', lambda m: {"minutes": 0, "hours": 0, "days": -int(m.group(1)) * 365}),
            
            # 영어 패턴
            (r'(\d+)\s*minutes?\s*ago', lambda m: {"minutes": -int(m.group(1)), "hours": 0, "days": 0}),
            (r'(\d+)\s*hours?\s*ago', lambda m: {"minutes": 0, "hours": -int(m.group(1)), "days": 0}),
            (r'(\d+)\s*days?\s*ago', lambda m: {"minutes": 0, "hours": 0, "days": -int(m.group(1))}),
            (r'(\d+)\s*weeks?\s*ago', lambda m: {"minutes": 0, "hours": 0, "days": -int(m.group(1)) * 7}),
            (r'(\d+)\s*months?\s*ago', lambda m: {"minutes": 0, "hours": 0, "days": -int(m.group(1)) * 30}),
            (r'(\d+)\s*years?\s*ago', lambda m: {"minutes": 0, "hours": 0, "days": -int(m.group(1)) * 365}),
        ]
    
    def parse_relative_time(self, time_expression: str, reference_time: datetime.datetime = None) -> datetime.datetime:
        """상대적 시간 표현을 실제 datetime으로 변환"""
        if reference_time is None:
            reference_time = datetime.datetime.now()
        
        time_expression = time_expression.strip().lower()
        
        # 직접 매핑되는 표현 확인
        for expression, delta in self.relative_time_map.items():
            if expression in time_expression:
                return reference_time + datetime.timedelta(
                    minutes=delta["minutes"],
                    hours=delta["hours"],
                    days=delta["days"]
                )
        
        # 패턴 매칭
        for pattern, delta_func in self.time_patterns:
            match = re.search(pattern, time_expression, re.IGNORECASE)
            if match:
                delta = delta_func(match)
                return reference_time + datetime.timedelta(
                    minutes=delta["minutes"],
                    hours=delta["hours"],
                    days=delta["days"]
                )
        
        # 매칭되지 않으면 현재 시간 반환
        return reference_time
    
    def get_relative_description(self, target_time: datetime.datetime, reference_time: datetime.datetime = None) -> str:
        """실제 시간을 상대적 표현으로 변환"""
        if reference_time is None:
            reference_time = datetime.datetime.now()
        
        delta = reference_time - target_time
        total_seconds = int(delta.total_seconds())
        
        if total_seconds < 0:
            # 미래 시간
            future_delta = target_time - reference_time
            future_seconds = int(future_delta.total_seconds())
            
            if future_seconds < 60:
                return "곧"
            elif future_seconds < 3600:
                minutes = future_seconds // 60
                return f"{minutes}분 후"
            elif future_seconds < 86400:
                hours = future_seconds // 3600
                return f"{hours}시간 후"
            else:
                days = future_seconds // 86400
                return f"{days}일 후"
        
        # 과거 시간
        if total_seconds < 60:
            return "방금"
        elif total_seconds < 300:  # 5분
            return "조금 전"
        elif total_seconds < 1800:  # 30분
            return "아까"
        elif total_seconds < 3600:  # 1시간
            minutes = total_seconds // 60
            return f"{minutes}분 전"
        elif total_seconds < 86400:  # 1일
            hours = total_seconds // 3600
            if hours == 1:
                return "1시간 전"
            else:
                return f"{hours}시간 전"
        elif total_seconds < 172800:  # 2일
            return "어제"
        elif total_seconds < 259200:  # 3일
            return "그저께"
        elif total_seconds < 604800:  # 1주일
            days = total_seconds // 86400
            return f"{days}일 전"
        elif total_seconds < 2592000:  # 1달
            weeks = total_seconds // 604800
            return f"{weeks}주 전"
        elif total_seconds < 31536000:  # 1년
            months = total_seconds // 2592000
            return f"{months}달 전"
        else:
            years = total_seconds // 31536000
            return f"{years}년 전"
    
    def adjust_time_context(self, query: str, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """검색 쿼리의 시간 표현을 분석하여 메모리 결과를 시간순으로 조정"""
        
        # 쿼리에서 시간 표현 추출
        time_expressions = self._extract_time_expressions(query)
        
        if not time_expressions:
            return memories
        
        # 각 시간 표현에 대해 target_time 계산
        current_time = datetime.datetime.now()
        time_filters = []
        
        for expression in time_expressions:
            target_time = self.parse_relative_time(expression, current_time)
            time_filters.append({
                "expression": expression,
                "target_time": target_time,
                "time_range": self._get_time_range(target_time)
            })
        
        # 메모리를 시간 기준으로 필터링 및 정렬
        filtered_memories = []
        for memory in memories:
            memory_time = self._extract_memory_time(memory)
            if memory_time:
                # 시간 필터와 일치하는지 확인
                for time_filter in time_filters:
                    if self._is_time_in_range(memory_time, time_filter["time_range"]):
                        # 상대적 시간 설명 추가
                        memory["relative_time"] = self.get_relative_description(memory_time, current_time)
                        memory["time_relevance_score"] = self._calculate_time_relevance(
                            memory_time, time_filter["target_time"]
                        )
                        filtered_memories.append(memory)
                        break
        
        # 시간 관련성 점수로 정렬
        filtered_memories.sort(key=lambda x: x.get("time_relevance_score", 0), reverse=True)
        
        return filtered_memories if filtered_memories else memories
    
    def _extract_time_expressions(self, text: str) -> List[str]:
        """텍스트에서 시간 표현 추출"""
        expressions = []
        
        # 직접 매핑 표현 확인
        for expression in self.relative_time_map.keys():
            if expression in text.lower():
                expressions.append(expression)
        
        # 패턴 매칭 표현 확인
        for pattern, _ in self.time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                expressions.append(match)
        
        return expressions
    
    def _extract_memory_time(self, memory: Dict[str, Any]) -> Optional[datetime.datetime]:
        """메모리에서 시간 정보 추출"""
        
        # timestamp 필드 확인
        if "timestamp" in memory:
            timestamp = memory["timestamp"]
            if isinstance(timestamp, str):
                try:
                    return datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    try:
                        return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    except:
                        pass
            elif isinstance(timestamp, datetime.datetime):
                return timestamp
        
        # created_at 필드 확인
        if "created_at" in memory:
            created_at = memory["created_at"]
            if isinstance(created_at, str):
                try:
                    return datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    pass
            elif isinstance(created_at, datetime.datetime):
                return created_at
        
        return None
    
    def _get_time_range(self, target_time: datetime.datetime) -> Dict[str, datetime.datetime]:
        """목표 시간 주변의 시간 범위 반환"""
        # 하루 범위로 설정 (필요에 따라 조정 가능)
        start_time = target_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + datetime.timedelta(days=1)
        
        return {
            "start": start_time,
            "end": end_time
        }
    
    def _is_time_in_range(self, time: datetime.datetime, time_range: Dict[str, datetime.datetime]) -> bool:
        """시간이 범위 내에 있는지 확인"""
        return time_range["start"] <= time < time_range["end"]
    
    def _calculate_time_relevance(self, memory_time: datetime.datetime, target_time: datetime.datetime) -> float:
        """시간 관련성 점수 계산 (0~1, 1이 가장 관련성 높음)"""
        delta = abs((memory_time - target_time).total_seconds())
        
        # 1일 이내는 높은 점수, 그 이후는 급격히 감소
        if delta < 86400:  # 1일
            return 1.0 - (delta / 86400) * 0.5
        elif delta < 604800:  # 1주일
            return 0.5 - ((delta - 86400) / (604800 - 86400)) * 0.3
        else:
            return max(0.2 - (delta / 2592000) * 0.2, 0.0)  # 1달 이후는 최소 점수


# 전역 시간 관리자 인스턴스
time_manager = TimeManager()


def parse_relative_time(time_expression: str, reference_time: datetime.datetime = None) -> datetime.datetime:
    """상대적 시간 표현 파싱 함수"""
    return time_manager.parse_relative_time(time_expression, reference_time)


def get_relative_description(target_time: datetime.datetime, reference_time: datetime.datetime = None) -> str:
    """상대적 시간 설명 생성 함수"""
    return time_manager.get_relative_description(target_time, reference_time)


def adjust_time_context(query: str, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """시간 컨텍스트 조정 함수"""
    return time_manager.adjust_time_context(query, memories) 