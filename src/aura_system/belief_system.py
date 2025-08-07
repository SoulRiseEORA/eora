"""
belief_system.py
- 신념 시스템 관리 및 갱신 함수 제공
"""

from typing import Any, Dict, Optional
from aura_system.belief_engine import get_belief_engine

async def update_belief_system(
    text: str,
    context: Optional[Dict[str, Any]] = None,
    extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    신념 시스템을 갱신(업데이트)합니다.
    Args:
        text (str): 신념 분석 대상 텍스트
        context (dict, optional): 추가 컨텍스트 정보
        extra (dict, optional): 기타 부가 정보
    Returns:
        dict: 신념 분석 및 갱신 결과
    """
    engine = get_belief_engine()
    result = await engine.analyze_belief(text, context)
    # 필요시 extra 정보 병합 등 추가 처리
    return result 