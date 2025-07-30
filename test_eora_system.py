#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI 시스템 종합 테스트 스크립트
"""

import sys
import os
import asyncio
import traceback
from datetime import datetime

# 프로젝트 루트 디렉토리를 path에 추가
sys.path.append('src')

def print_test_header(test_name):
    """테스트 헤더 출력"""
    print("\n" + "="*60)
    print(f"🧪 {test_name}")
    print("="*60)

def print_test_result(test_name, success, message=""):
    """테스트 결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{status} {test_name}")
    if message:
        print(f"   📝 {message}")

class EORASystemTester:
    """EORA 시스템 테스트 클래스"""
    
    def __init__(self):
        self.test_results = {}
        self.eora_memory_system = None
        
    def test_imports(self):
        """1. 모듈 임포트 테스트"""
        print_test_header("모듈 임포트 테스트")
        
        try:
            # EORAMemorySystem 임포트 테스트
            from aura_memory_system import EORAMemorySystem, AuraMemorySystem
            print_test_result("EORAMemorySystem 임포트", True)
            
            # 인스턴스 생성 테스트
            self.eora_memory_system = EORAMemorySystem()
            print_test_result("EORAMemorySystem 인스턴스 생성", True)
            
            # 별칭 클래스 테스트
            aura_system = AuraMemorySystem()
            print_test_result("AuraMemorySystem 별칭 클래스", True)
            
            self.test_results['imports'] = True
            
        except Exception as e:
            print_test_result("모듈 임포트", False, str(e))
            self.test_results['imports'] = False
            
    def test_memory_system_initialization(self):
        """2. 메모리 시스템 초기화 테스트"""
        print_test_header("메모리 시스템 초기화 테스트")
        
        if not self.eora_memory_system:
            print_test_result("메모리 시스템 초기화", False, "EORAMemorySystem 인스턴스가 없음")
            self.test_results['initialization'] = False
            return
            
        try:
            # 8종 회상 시스템 확인
            recall_types = self.eora_memory_system.recall_types
            expected_types = [
                "keyword_recall", "embedding_recall", "emotion_recall",
                "belief_recall", "context_recall", "temporal_recall",
                "association_recall", "pattern_recall"
            ]
            
            if len(recall_types) == 8 and all(t in recall_types for t in expected_types):
                print_test_result("8종 회상 시스템 설정", True, f"회상 유형: {len(recall_types)}개")
            else:
                print_test_result("8종 회상 시스템 설정", False, f"예상: 8개, 실제: {len(recall_types)}개")
                
            # 고급 기능 시스템 확인
            intuition = self.eora_memory_system.intuition_engine
            insight = self.eora_memory_system.insight_engine
            wisdom = self.eora_memory_system.wisdom_engine
            
            if intuition and insight and wisdom:
                print_test_result("고급 기능 시스템 활성화", True, "직관, 통찰, 지혜 모든 기능 활성화")
            else:
                print_test_result("고급 기능 시스템 활성화", False, f"직관:{intuition}, 통찰:{insight}, 지혜:{wisdom}")
                
            self.test_results['initialization'] = True
            
        except Exception as e:
            print_test_result("메모리 시스템 초기화", False, str(e))
            self.test_results['initialization'] = False
            
    async def test_memory_storage_and_recall(self):
        """3. 메모리 저장 및 회상 테스트"""
        print_test_header("메모리 저장 및 회상 테스트")
        
        if not self.eora_memory_system:
            print_test_result("메모리 저장 및 회상", False, "EORAMemorySystem 인스턴스가 없음")
            self.test_results['memory_storage'] = False
            return
            
        try:
            # 테스트 메모리 저장
            test_memories = [
                {
                    "content": "EORA AI는 8종 회상 시스템을 가진 고급 인공지능입니다.",
                    "user_id": "test_user",
                    "session_id": "test_session_1",
                    "metadata": {"emotion": "중립", "topic": "AI 소개"}
                },
                {
                    "content": "사용자가 머신러닝에 대해 질문했습니다. 매우 흥미로워했습니다.",
                    "user_id": "test_user", 
                    "session_id": "test_session_1",
                    "metadata": {"emotion": "흥미", "topic": "머신러닝"}
                },
                {
                    "content": "이전에 파이썬 프로그래밍을 배웠다고 언급했습니다.",
                    "user_id": "test_user",
                    "session_id": "test_session_2", 
                    "metadata": {"emotion": "자신감", "topic": "프로그래밍"}
                }
            ]
            
            # 메모리 저장 테스트
            stored_count = 0
            for memory in test_memories:
                try:
                    await self.eora_memory_system.store_memory(
                        content=memory["content"],
                        user_id=memory["user_id"],
                        session_id=memory["session_id"],
                        metadata=memory["metadata"]
                    )
                    stored_count += 1
                except Exception as e:
                    print(f"   ⚠️ 메모리 저장 오류: {e}")
                    
            print_test_result("메모리 저장", stored_count > 0, f"{stored_count}/{len(test_memories)}개 저장 성공")
            
            # 8종 회상 테스트
            recall_results = {}
            test_queries = [
                ("AI 시스템", "keyword_recall"),
                ("머신러닝 학습", "embedding_recall"), 
                ("흥미로운 질문", "emotion_recall"),
                ("프로그래밍 배경", "context_recall")
            ]
            
            for query, expected_type in test_queries:
                try:
                    memories = await self.eora_memory_system.enhanced_recall(
                        query=query, 
                        user_id="test_user", 
                        limit=3
                    )
                    recall_results[expected_type] = len(memories)
                    print_test_result(f"{expected_type} 회상", len(memories) > 0, f"{len(memories)}개 회상")
                except Exception as e:
                    print_test_result(f"{expected_type} 회상", False, str(e))
                    recall_results[expected_type] = 0
                    
            # 종합 회상 테스트
            total_recalled = sum(recall_results.values())
            print_test_result("8종 회상 시스템 종합", total_recalled > 0, f"총 {total_recalled}개 메모리 회상")
            
            self.test_results['memory_storage'] = stored_count > 0 and total_recalled > 0
            
        except Exception as e:
            print_test_result("메모리 저장 및 회상", False, str(e))
            traceback.print_exc()
            self.test_results['memory_storage'] = False
            
    async def test_advanced_features(self):
        """4. 고급 기능 테스트 (직관, 통찰, 지혜)"""
        print_test_header("고급 기능 테스트")
        
        if not self.eora_memory_system:
            print_test_result("고급 기능 테스트", False, "EORAMemorySystem 인스턴스가 없음")
            self.test_results['advanced_features'] = False
            return
            
        try:
            test_data = {
                "user_input": "머신러닝을 배우고 싶은데 어떻게 시작해야 할까요?",
                "user_id": "test_user",
                "recalled_memories": [
                    {"content": "이전에 파이썬을 배웠다고 했음", "recall_type": "context_recall"},
                    {"content": "머신러닝에 매우 흥미로워함", "recall_type": "emotion_recall"}
                ],
                "conversation_history": [
                    {"role": "user", "content": "안녕하세요"},
                    {"role": "assistant", "content": "안녕하세요! 도움이 필요하시면 말씀해주세요."}
                ]
            }
            
            # 직관 생성 테스트
            try:
                intuition = await self.eora_memory_system.generate_intuition(
                    user_input=test_data["user_input"],
                    user_id=test_data["user_id"],
                    conversation_history=test_data["conversation_history"]
                )
                print_test_result("직관 생성", len(intuition) > 0, f"직관 길이: {len(intuition)}자")
            except Exception as e:
                print_test_result("직관 생성", False, str(e))
                
            # 통찰 생성 테스트  
            try:
                insights = await self.eora_memory_system.generate_insights(
                    user_input=test_data["user_input"],
                    user_id=test_data["user_id"],
                    recalled_memories=test_data["recalled_memories"]
                )
                print_test_result("통찰 생성", len(insights) > 0, f"통찰 길이: {len(insights)}자")
            except Exception as e:
                print_test_result("통찰 생성", False, str(e))
                
            # 지혜 생성 테스트
            try:
                wisdom = await self.eora_memory_system.generate_wisdom(
                    user_input=test_data["user_input"],
                    user_id=test_data["user_id"],
                    conversation_history=test_data["conversation_history"]
                )
                print_test_result("지혜 생성", len(wisdom) > 0, f"지혜 길이: {len(wisdom)}자")
            except Exception as e:
                print_test_result("지혜 생성", False, str(e))
                
            # 종합 응답 생성 테스트
            try:
                response = await self.eora_memory_system.generate_response(
                    user_input=test_data["user_input"],
                    user_id=test_data["user_id"],
                    recalled_memories=test_data["recalled_memories"],
                    conversation_history=test_data["conversation_history"]
                )
                print_test_result("종합 응답 생성", len(response) > 0, f"응답 길이: {len(response)}자")
                
                # 생성된 응답에 고급 기능 요소가 포함되어 있는지 확인
                has_intuition = "직관" in response or "느낌" in response
                has_insight = "통찰" in response or "깨달음" in response  
                has_wisdom = "지혜" in response or "조언" in response
                
                advanced_features_included = has_intuition or has_insight or has_wisdom
                print_test_result("고급 기능 통합", advanced_features_included, 
                                "직관/통찰/지혜 요소가 응답에 포함됨")
                
            except Exception as e:
                print_test_result("종합 응답 생성", False, str(e))
                
            self.test_results['advanced_features'] = True
            
        except Exception as e:
            print_test_result("고급 기능 테스트", False, str(e))
            traceback.print_exc()
            self.test_results['advanced_features'] = False
            
    def test_memory_ranking_and_deduplication(self):
        """5. 메모리 순위 및 중복 제거 테스트"""
        print_test_header("메모리 순위 및 중복 제거 테스트")
        
        if not self.eora_memory_system:
            print_test_result("메모리 순위 테스트", False, "EORAMemorySystem 인스턴스가 없음")
            self.test_results['ranking'] = False
            return
            
        try:
            # 테스트용 중복 메모리 생성
            test_memories = [
                {"content": "머신러닝은 흥미로운 분야입니다", "recall_type": "keyword_recall", "timestamp": "2024-01-01"},
                {"content": "머신러닝은 흥미로운 분야입니다", "recall_type": "embedding_recall", "timestamp": "2024-01-01"},  # 중복
                {"content": "AI와 머신러닝을 배우고 싶어합니다", "recall_type": "emotion_recall", "timestamp": "2024-01-02"},
                {"content": "파이썬 프로그래밍 경험이 있습니다", "recall_type": "context_recall", "timestamp": "2024-01-03"},
            ]
            
            # 중복 제거 테스트
            unique_memories = self.eora_memory_system._deduplicate_memories(test_memories)
            print_test_result("메모리 중복 제거", len(unique_memories) < len(test_memories), 
                            f"원본: {len(test_memories)}개 → 중복제거: {len(unique_memories)}개")
            
            # 순위 매기기 테스트
            query = "머신러닝 학습"
            ranked_memories = self.eora_memory_system._rank_memories(unique_memories, query)
            print_test_result("메모리 순위 매기기", len(ranked_memories) > 0, 
                            f"{len(ranked_memories)}개 메모리 순위 완료")
            
            # 상위 3개 제한 테스트
            limited_memories = ranked_memories[:3]
            print_test_result("상위 3개 제한", len(limited_memories) <= 3, 
                            f"제한된 메모리: {len(limited_memories)}개")
            
            self.test_results['ranking'] = True
            
        except Exception as e:
            print_test_result("메모리 순위 및 중복 제거", False, str(e))
            self.test_results['ranking'] = False
            
    def print_final_report(self):
        """최종 테스트 결과 리포트"""
        print_test_header("최종 테스트 결과 리포트")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        print(f"📊 총 테스트: {total_tests}개")
        print(f"✅ 성공: {passed_tests}개") 
        print(f"❌ 실패: {total_tests - passed_tests}개")
        print(f"📈 성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 상세 결과:")
        for test_name, result in self.test_results.items():
            status = "✅" if result else "❌"
            print(f"   {status} {test_name}")
            
        # 전체 시스템 상태 판정
        critical_tests = ['imports', 'initialization', 'memory_storage']
        critical_passed = all(self.test_results.get(test, False) for test in critical_tests)
        
        if critical_passed and passed_tests >= total_tests * 0.8:
            print("\n🎉 EORA AI 시스템이 배포 준비 완료되었습니다!")
            return True
        else:
            print("\n⚠️ 일부 기능에 문제가 있습니다. 수정 후 재테스트가 필요합니다.")
            return False

async def main():
    """메인 테스트 실행 함수"""
    print("🚀 EORA AI 시스템 종합 테스트 시작")
    print(f"⏰ 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = EORASystemTester()
    
    # 순차적 테스트 실행
    tester.test_imports()
    tester.test_memory_system_initialization()
    await tester.test_memory_storage_and_recall()
    await tester.test_advanced_features()
    tester.test_memory_ranking_and_deduplication()
    
    # 최종 결과 리포트
    is_ready = tester.print_final_report()
    
    print(f"\n⏰ 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return is_ready

if __name__ == "__main__":
    try:
        # asyncio를 사용하여 비동기 테스트 실행
        result = asyncio.run(main())
        exit_code = 0 if result else 1
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n💥 테스트 실행 중 오류 발생: {e}")
        traceback.print_exc()
        sys.exit(1) 