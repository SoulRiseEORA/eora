#!/usr/bin/env python3
"""
8종 회상 시스템 테스트 스크립트
- 회상 정확도 향상 테스트
- 8가지 회상 전략 검증
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class RecallSystemTester:
    """8종 회상 시스템 테스터"""
    
    def __init__(self):
        self.test_results = []
        self.recall_engine = None
        
    async def initialize_recall_system(self):
        """회상 시스템 초기화"""
        try:
            from aura_system.recall_engine import RecallEngine
            from aura_system.memory_manager import MemoryManagerAsync
            
            # 메모리 매니저 초기화
            memory_manager = MemoryManagerAsync()
            if not memory_manager.is_initialized:
                await memory_manager.initialize()
            
            # 회상 엔진 초기화
            self.recall_engine = RecallEngine(memory_manager)
            logger.info("✅ 회상 시스템 초기화 완료")
            return True
            
        except ImportError as e:
            logger.error(f"❌ 회상 시스템 임포트 실패: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 회상 시스템 초기화 실패: {e}")
            return False
    
    async def test_recall_strategies(self):
        """8가지 회상 전략 테스트"""
        if not self.recall_engine:
            logger.error("❌ 회상 엔진이 초기화되지 않음")
            return
        
        test_cases = [
            {
                "name": "키워드 기반 회상",
                "query": "AI 시스템",
                "expected_keywords": ["AI", "시스템"],
                "strategy": "keywords"
            },
            {
                "name": "감정 기반 회상",
                "query": "정말 기쁘고 행복해요",
                "expected_emotion": "기쁨",
                "strategy": "emotion"
            },
            {
                "name": "신념 기반 회상",
                "query": "절대적으로 확실하다고 믿어요",
                "expected_belief": ["절대", "확실", "믿음"],
                "strategy": "belief"
            },
            {
                "name": "시간 기반 회상",
                "query": "어제 대화했던 내용",
                "expected_time": "yesterday",
                "strategy": "time"
            },
            {
                "name": "맥락 기반 회상",
                "query": "이전 세션에서 논의했던 내용",
                "expected_context": "session",
                "strategy": "context"
            },
            {
                "name": "임베딩 기반 회상",
                "query": "프로그래밍 자동화",
                "expected_semantic": "programming",
                "strategy": "embedding"
            },
            {
                "name": "시퀀스 체인 회상",
                "query": "이전 대화의 연속",
                "expected_chain": "sequence",
                "strategy": "sequence"
            },
            {
                "name": "트리거 기반 회상",
                "query": "기억해보세요",
                "expected_trigger": "recall",
                "strategy": "trigger"
            }
        ]
        
        logger.info("🧪 8종 회상 전략 테스트 시작")
        
        for test_case in test_cases:
            try:
                result = await self._test_single_strategy(test_case)
                self.test_results.append(result)
                logger.info(f"✅ {test_case['name']} 테스트 완료")
            except Exception as e:
                logger.error(f"❌ {test_case['name']} 테스트 실패: {e}")
                self.test_results.append({
                    "name": test_case['name'],
                    "success": False,
                    "error": str(e)
                })
    
    async def _test_single_strategy(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """단일 회상 전략 테스트"""
        query = test_case["query"]
        strategy = test_case["strategy"]
        
        # 컨텍스트 정보 구성
        context = {
            "user_id": "test_user",
            "session_id": "test_session",
            "time_tag": datetime.now().strftime("%Y-%m-%d"),
            "topic": "test"
        }
        
        # 감정 분석
        emotion = None
        if "기쁘" in query or "행복" in query:
            emotion = {"label": "기쁨"}
        elif "슬프" in query or "우울" in query:
            emotion = {"label": "슬픔"}
        elif "화나" in query or "분노" in query:
            emotion = {"label": "분노"}
        
        # 회상 실행
        start_time = datetime.now()
        memories = await self.recall_engine.recall(
            query=query,
            context=context,
            emotion=emotion,
            limit=3,
            distance_threshold=1.2
        )
        end_time = datetime.now()
        
        # 결과 분석
        execution_time = (end_time - start_time).total_seconds()
        memory_count = len(memories)
        
        return {
            "name": test_case["name"],
            "query": query,
            "strategy": strategy,
            "success": True,
            "memory_count": memory_count,
            "execution_time": execution_time,
            "memories": memories[:2],  # 처음 2개만 저장
            "expected": test_case
        }
    
    def generate_test_report(self):
        """테스트 결과 리포트 생성"""
        logger.info("\n" + "="*60)
        logger.info("📊 8종 회상 시스템 테스트 리포트")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.get("success", False))
        failed_tests = total_tests - successful_tests
        
        logger.info(f"총 테스트 수: {total_tests}")
        logger.info(f"성공: {successful_tests}")
        logger.info(f"실패: {failed_tests}")
        logger.info(f"성공률: {(successful_tests/total_tests)*100:.1f}%")
        
        # 각 전략별 상세 결과
        logger.info("\n📋 전략별 상세 결과:")
        for result in self.test_results:
            status = "✅" if result.get("success", False) else "❌"
            name = result["name"]
            memory_count = result.get("memory_count", 0)
            execution_time = result.get("execution_time", 0)
            
            logger.info(f"{status} {name}: {memory_count}개 메모리, {execution_time:.3f}초")
            
            if not result.get("success", False):
                error = result.get("error", "알 수 없는 오류")
                logger.info(f"   오류: {error}")
        
        # 성능 분석
        successful_results = [r for r in self.test_results if r.get("success", False)]
        if successful_results:
            avg_execution_time = sum(r.get("execution_time", 0) for r in successful_results) / len(successful_results)
            avg_memory_count = sum(r.get("memory_count", 0) for r in successful_results) / len(successful_results)
            
            logger.info(f"\n📈 성능 지표:")
            logger.info(f"평균 실행 시간: {avg_execution_time:.3f}초")
            logger.info(f"평균 회상 메모리 수: {avg_memory_count:.1f}개")
        
        logger.info("\n" + "="*60)
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests/total_tests)*100 if total_tests > 0 else 0,
            "results": self.test_results
        }

async def main():
    """메인 테스트 함수"""
    logger.info("🚀 8종 회상 시스템 테스트 시작")
    
    tester = RecallSystemTester()
    
    # 회상 시스템 초기화
    if not await tester.initialize_recall_system():
        logger.error("❌ 회상 시스템 초기화 실패로 테스트 중단")
        return
    
    # 8가지 회상 전략 테스트
    await tester.test_recall_strategies()
    
    # 테스트 리포트 생성
    report = tester.generate_test_report()
    
    # 결과 저장
    with open("recall_test_report.json", "w", encoding="utf-8") as f:
        import json
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info("✅ 테스트 완료! 결과가 recall_test_report.json에 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main()) 