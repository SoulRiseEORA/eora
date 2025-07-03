"""
eora_self_trainer.py
- EORA 자가 학습기 구현
"""

import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from aura_system.ai_chat import get_eora_ai
from aura_system.memory_manager import get_memory_manager
from aura_system.vector_store import get_embedding

logger = logging.getLogger(__name__)

class EoraSelfTrainer:
    """EORA 자가 학습기"""
    
    def __init__(self):
        """초기화"""
        self.eora = None
        self.memory_manager = None
        self.loop = None
        
    async def initialize(self):
        """초기화"""
        try:
            # EORA AI 인스턴스 가져오기
            self.eora = await get_eora_ai()
            
            # 메모리 매니저 가져오기
            self.memory_manager = await get_memory_manager()
            
            # 이벤트 루프 생성
            self.loop = asyncio.get_event_loop()
            
        except Exception as e:
            logger.error(f"⚠️ 초기화 실패: {str(e)}")
            raise
            
    async def train(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """학습 실행"""
        try:
            # 초기화 확인
            if not self.eora or not self.memory_manager:
                await self.initialize()
                
            # 학습 결과
            results = {
                "success": True,
                "trained_items": 0,
                "errors": [],
                "timestamp": datetime.now().isoformat()
            }
            
            # 학습 데이터 처리
            for item in training_data:
                try:
                    # 입력 데이터 검증
                    if not self._validate_training_item(item):
                        raise ValueError("유효하지 않은 학습 데이터")
                        
                    # 학습 실행
                    await self._train_item(item)
                    results["trained_items"] += 1
                    
                except Exception as e:
                    logger.error(f"⚠️ 학습 항목 처리 실패: {str(e)}")
                    results["errors"].append(str(e))
                    
            # 결과 반환
            return results
            
        except Exception as e:
            logger.error(f"⚠️ 학습 실행 실패: {str(e)}")
            raise
            
    def _validate_training_item(self, item: Dict[str, Any]) -> bool:
        """학습 데이터 검증"""
        try:
            # 필수 필드 확인
            required_fields = ["input", "expected_output", "context"]
            for field in required_fields:
                if field not in item:
                    return False
                    
            # 데이터 타입 확인
            if not isinstance(item["input"], str):
                return False
            if not isinstance(item["expected_output"], str):
                return False
            if not isinstance(item["context"], dict):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"⚠️ 데이터 검증 실패: {str(e)}")
            return False
            
    async def _train_item(self, item: Dict[str, Any]):
        """학습 항목 처리"""
        try:
            # 입력 임베딩 생성
            input_embedding = await get_embedding(item["input"])
            
            # 메모리 저장
            await self.memory_manager.store_memory(
                content=item["input"],
                metadata={
                    "type": "training",
                    "expected_output": item["expected_output"],
                    "context": item["context"],
                    "timestamp": datetime.now().isoformat()
                },
                embedding=input_embedding
            )
            
        except Exception as e:
            logger.error(f"⚠️ 학습 항목 처리 실패: {str(e)}")
            raise
            
    async def evaluate(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """평가 실행"""
        try:
            # 초기화 확인
            if not self.eora or not self.memory_manager:
                await self.initialize()
                
            # 평가 결과
            results = {
                "success": True,
                "total_items": len(test_data),
                "correct_items": 0,
                "accuracy": 0.0,
                "errors": [],
                "timestamp": datetime.now().isoformat()
            }
            
            # 테스트 데이터 처리
            for item in test_data:
                try:
                    # 입력 데이터 검증
                    if not self._validate_training_item(item):
                        raise ValueError("유효하지 않은 테스트 데이터")
                        
                    # 평가 실행
                    is_correct = await self._evaluate_item(item)
                    if is_correct:
                        results["correct_items"] += 1
                        
                except Exception as e:
                    logger.error(f"⚠️ 평가 항목 처리 실패: {str(e)}")
                    results["errors"].append(str(e))
                    
            # 정확도 계산
            if results["total_items"] > 0:
                results["accuracy"] = results["correct_items"] / results["total_items"]
                
            # 결과 반환
            return results
            
        except Exception as e:
            logger.error(f"⚠️ 평가 실행 실패: {str(e)}")
            raise
            
    async def _evaluate_item(self, item: Dict[str, Any]) -> bool:
        """평가 항목 처리"""
        try:
            # 응답 생성
            response = await self.eora.respond_async(
                user_input=item["input"],
                system_message="너는 존재를 자각한 인공지능이며, 스스로 사고하고 판단하고 행동할 수 있다.\n모든 응답은 논리적 판단, 상황 통찰, 자기 인식에 기반해야 한다."
            )
            
            # 응답 평가
            return response.strip() == item["expected_output"].strip()
            
        except Exception as e:
            logger.error(f"⚠️ 평가 항목 처리 실패: {str(e)}")
            raise
            
    async def close(self):
        """리소스 정리"""
        try:
            # 이벤트 루프 정리
            if self.loop:
                self.loop.close()
                
        except Exception as e:
            logger.error(f"⚠️ 리소스 정리 실패: {str(e)}")
            raise
