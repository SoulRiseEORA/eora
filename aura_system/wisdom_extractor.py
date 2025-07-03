"""
wisdom_extractor.py
- 지혜(통찰 등) 추출 및 분석 함수 제공
"""

from typing import Any, Dict, Optional
from aura_system.wisdom_engine import analyze_wisdom

async def extract_wisdom(
    text: str,
    context: Optional[Dict[str, Any]] = None,
    extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    지혜(통찰 등)를 추출/분석합니다.
    Args:
        text (str): 분석 대상 텍스트
        context (dict, optional): 추가 컨텍스트 정보
        extra (dict, optional): 기타 부가 정보
    Returns:
        dict: 지혜 분석 결과
    """
    result = await analyze_wisdom(text, context)
    # 필요시 extra 정보 병합 등 추가 처리
    return result 