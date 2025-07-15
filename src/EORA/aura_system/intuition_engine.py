"""
aura_system.intuition_engine

직감 엔진 모듈
- IR-Core 예측
- 직감 기반 판단
"""

import logging
import numpy as np
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def run_ir_core_prediction(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    IR-Core 예측 실행
    
    Args:
        input_data (Dict): 입력 데이터
        
    Returns:
        Dict: 예측 결과
    """
    try:
        # 간단한 더미 예측 결과
        result = {
            "prediction": "직감 기반 예측 결과",
            "confidence": 0.75,
            "intuition_score": 0.8,
            "reasoning": "직감 엔진이 분석한 결과입니다.",
            "metadata": {
                "model": "IR-Core",
                "version": "1.0",
                "timestamp": "2024-01-01T00:00:00"
            }
        }
        
        logger.debug("IR-Core 예측 완료")
        return result
        
    except Exception as e:
        logger.error(f"IR-Core 예측 실패: {str(e)}")
        return {
            "prediction": "예측 실패",
            "confidence": 0.0,
            "error": str(e)
        }

def calculate_intuition_score(features: List[float]) -> float:
    """
    직감 점수 계산
    
    Args:
        features (List[float]): 특징 벡터
        
    Returns:
        float: 직감 점수 (0-1)
    """
    try:
        if not features:
            return 0.0
        
        # 간단한 평균 기반 직감 점수
        score = np.mean(features)
        return min(1.0, max(0.0, score))
        
    except Exception as e:
        logger.error(f"직감 점수 계산 실패: {str(e)}")
        return 0.0

# 테스트 함수
def test_intuition_engine():
    """직감 엔진 테스트"""
    print("=== Intuition Engine 테스트 ===")
    
    # IR-Core 예측 테스트
    input_data = {
        "text": "테스트 입력",
        "features": [0.5, 0.7, 0.3, 0.8, 0.6]
    }
    
    result = run_ir_core_prediction(input_data)
    print(f"예측 결과: {result['prediction']}")
    print(f"신뢰도: {result['confidence']}")
    print(f"직감 점수: {result['intuition_score']}")
    
    # 직감 점수 계산 테스트
    features = [0.5, 0.7, 0.3, 0.8, 0.6]
    intuition_score = calculate_intuition_score(features)
    print(f"직감 점수: {intuition_score:.3f}")
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_intuition_engine() 