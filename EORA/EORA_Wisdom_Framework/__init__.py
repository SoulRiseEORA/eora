"""
EORA_Wisdom_Framework 패키지

EORA 시스템의 지혜 프레임워크
- 통찰 관리
- 메모리 전략
"""

from .EORAInsightManagerV2 import EORAInsightManagerV2
from .memory_strategy_manager import get_turn_limit_for_context

__all__ = [
    'EORAInsightManagerV2',
    'get_turn_limit_for_context'
] 