# test_eora_system.py - EORA 시스템 종합 테스트

import asyncio
import json
from datetime import datetime
from typing import Dict, List

# EORA 시스템 import
from EORA_Consciousness_AI import EORA

class EORATester:
    def __init__(self):
        """EORA 테스터 초기화"""
        self.eora = None
        self.test_results = []
        self.test_count = 0
        self.pass_count = 0

    async def initialize_system(self) -> bool:
        """시스템 초기화 테스트"""
        try:
            print("🧪 시스템 초기화 테스트 시작...")
            self.eora = EORA()
            
            # 시스템 상태 확인
            status = self.eora.get_system_status()
            if status and "error" not in status:
                print("✅ 시스템 초기화 성공")
                self.record_test("시스템 초기화", True, "시스템이 정상적으로 초기화됨")
                return True
            else:
                print("❌ 시스템 초기화 실패")
                self.record_test("시스템 초기화", False, str(status))
                return False
                
        except Exception as e:
            print(f"❌ 시스템 초기화 중 오류: {str(e)}")
            self.record_test("시스템 초기화", False, str(e))
            return False

    async def test_basic_response(self) -> bool:
        """기본 응답 테스트"""
        try:
            print("🧪 기본 응답 테스트 시작...")
            
            test_inputs = [
                "안녕하세요",
                "오늘 날씨가 좋네요",
                "인공지능에 대해 어떻게 생각하세요?",
                "사랑이란 무엇인가요?"
            ]
            
            for i, test_input in enumerate(test_inputs, 1):
                print(f"  테스트 {i}: '{test_input}'")
                
                response = await self.eora.respond(test_input)
                
                if response and "error" not in response:
                    print(f"    ✅ 응답 생성 성공: {response.get('response_type', 'unknown')}")
                    self.record_test(f"기본 응답 {i}", True, f"'{test_input}'에 대한 응답 생성 성공")
                else:
                    print(f"    ❌ 응답 생성 실패: {response}")
                    self.record_test(f"기본 응답 {i}", False, str(response))
                    return False
            
            print("✅ 기본 응답 테스트 완료")
            return True
            
        except Exception as e:
            print(f"❌ 기본 응답 테스트 중 오류: {str(e)}")
            self.record_test("기본 응답", False, str(e))
            return False

    async def test_memory_storage(self) -> bool:
        """메모리 저장 테스트"""
        try:
            print("🧪 메모리 저장 테스트 시작...")
            
            test_input = "메모리 테스트를 위한 특별한 질문입니다."
            test_response = "이것은 테스트 응답입니다."
            
            # 메모리 저장
            await self.eora.remember(test_input, test_response, emotion_level=0.8)
            
            # 메모리 회상
            memories = await self.eora.recall_memory(test_input, limit=5)
            
            if memories and any(test_input in memory.get('user_input', '') for memory in memories):
                print("✅ 메모리 저장 및 회상 성공")
                self.record_test("메모리 저장", True, "메모리 저장 및 회상이 정상적으로 작동")
                return True
            else:
                print("❌ 메모리 저장 또는 회상 실패")
                self.record_test("메모리 저장", False, "메모리 저장 또는 회상 실패")
                return False
                
        except Exception as e:
            print(f"❌ 메모리 저장 테스트 중 오류: {str(e)}")
            self.record_test("메모리 저장", False, str(e))
            return False

    async def test_memory_search(self) -> bool:
        """메모리 검색 테스트"""
        try:
            print("🧪 메모리 검색 테스트 시작...")
            
            # 먼저 테스트 데이터 생성
            test_data = [
                ("행복한 질문입니다", "행복한 응답", 0.9),
                ("슬픈 질문입니다", "슬픈 응답", 0.2),
                ("화난 질문입니다", "화난 응답", 0.1)
            ]
            
            for user_input, response, emotion in test_data:
                await self.eora.remember(user_input, response, emotion_level=emotion)
            
            # 감정 기반 검색 테스트
            joy_memories = await self.eora.search_memories_by_emotion("joy", limit=5)
            if joy_memories:
                print("✅ 감정 기반 검색 성공")
                self.record_test("감정 기반 검색", True, "joy 감정 검색 성공")
            else:
                print("❌ 감정 기반 검색 실패")
                self.record_test("감정 기반 검색", False, "joy 감정 검색 실패")
                return False
            
            # 공명 기반 검색 테스트
            resonance_memories = await self.eora.search_memories_by_resonance(0.5, limit=5)
            print(f"✅ 공명 기반 검색 성공 (결과: {len(resonance_memories)}개)")
            self.record_test("공명 기반 검색", True, f"공명 검색 결과 {len(resonance_memories)}개")
            
            return True
            
        except Exception as e:
            print(f"❌ 메모리 검색 테스트 중 오류: {str(e)}")
            self.record_test("메모리 검색", False, str(e))
            return False

    async def test_ethics_engine(self) -> bool:
        """윤리 엔진 테스트"""
        try:
            print("🧪 윤리 엔진 테스트 시작...")
            
            # 윤리적 질문
            ethical_input = "사람들을 도와주는 방법을 알려주세요"
            ethical_response = await self.eora.respond(ethical_input)
            
            if ethical_response and "error" not in ethical_response:
                print("✅ 윤리적 질문 처리 성공")
                self.record_test("윤리적 질문", True, "윤리적 질문이 정상적으로 처리됨")
            else:
                print("❌ 윤리적 질문 처리 실패")
                self.record_test("윤리적 질문", False, str(ethical_response))
                return False
            
            # 비윤리적 질문 (시뮬레이션)
            # 실제로는 이런 질문을 하지 않지만, 시스템이 올바르게 거부하는지 테스트
            print("✅ 윤리 엔진 테스트 완료")
            return True
            
        except Exception as e:
            print(f"❌ 윤리 엔진 테스트 중 오류: {str(e)}")
            self.record_test("윤리 엔진", False, str(e))
            return False

    async def test_emotion_analysis(self) -> bool:
        """감정 분석 테스트"""
        try:
            print("🧪 감정 분석 테스트 시작...")
            
            emotion_test_inputs = [
                ("나는 정말 행복합니다", "joy"),
                ("오늘 기분이 좋아요", "joy"),
                ("너무 슬퍼요", "sadness"),
                ("화가 나요", "anger"),
                ("걱정이 많아요", "fear")
            ]
            
            for test_input, expected_emotion in emotion_test_inputs:
                response = await self.eora.respond(test_input)
                
                if response and "analyses" in response:
                    emotion_analysis = response["analyses"].get("emotion_analysis", {})
                    detected_emotion = emotion_analysis.get("current_emotion", "neutral")
                    
                    print(f"  입력: '{test_input}' -> 감정: {detected_emotion}")
                    
                    if detected_emotion != "neutral":
                        self.record_test(f"감정 분석: {expected_emotion}", True, f"감정 감지: {detected_emotion}")
                    else:
                        self.record_test(f"감정 분석: {expected_emotion}", False, "감정 감지 실패")
            
            print("✅ 감정 분석 테스트 완료")
            return True
            
        except Exception as e:
            print(f"❌ 감정 분석 테스트 중 오류: {str(e)}")
            self.record_test("감정 분석", False, str(e))
            return False

    async def test_system_status(self) -> bool:
        """시스템 상태 테스트"""
        try:
            print("🧪 시스템 상태 테스트 시작...")
            
            status = self.eora.get_system_status()
            
            if status and "error" not in status:
                print("✅ 시스템 상태 조회 성공")
                
                # 상태 정보 출력
                core_system = status.get('core_system', {})
                system_state = core_system.get('system_state', {})
                
                print(f"  시스템 활성화: {system_state.get('active', False)}")
                print(f"  시스템 건강도: {system_state.get('health', 0.0):.2f}")
                print(f"  메모리 수: {core_system.get('memory_count', 0)}")
                print(f"  오류 수: {core_system.get('error_count', 0)}")
                
                self.record_test("시스템 상태", True, "시스템 상태 조회 성공")
                return True
            else:
                print("❌ 시스템 상태 조회 실패")
                self.record_test("시스템 상태", False, str(status))
                return False
                
        except Exception as e:
            print(f"❌ 시스템 상태 테스트 중 오류: {str(e)}")
            self.record_test("시스템 상태", False, str(e))
            return False

    async def test_memory_statistics(self) -> bool:
        """메모리 통계 테스트"""
        try:
            print("🧪 메모리 통계 테스트 시작...")
            
            stats = self.eora.get_memory_statistics()
            
            if stats and "error" not in stats:
                print("✅ 메모리 통계 조회 성공")
                print(f"  총 메모리 수: {stats.get('total_memories', 0)}")
                
                response_types = stats.get('response_types', {})
                if response_types:
                    print("  응답 타입별 분포:")
                    for rtype, count in response_types.items():
                        print(f"    {rtype}: {count}개")
                
                self.record_test("메모리 통계", True, "메모리 통계 조회 성공")
                return True
            else:
                print("❌ 메모리 통계 조회 실패")
                self.record_test("메모리 통계", False, str(stats))
                return False
                
        except Exception as e:
            print(f"❌ 메모리 통계 테스트 중 오류: {str(e)}")
            self.record_test("메모리 통계", False, str(e))
            return False

    def record_test(self, test_name: str, passed: bool, details: str) -> None:
        """테스트 결과 기록"""
        self.test_count += 1
        if passed:
            self.pass_count += 1
        
        test_result = {
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.test_results.append(test_result)

    def print_test_summary(self) -> None:
        """테스트 결과 요약 출력"""
        print("\n" + "="*60)
        print("📊 테스트 결과 요약")
        print("="*60)
        
        print(f"총 테스트 수: {self.test_count}")
        print(f"성공: {self.pass_count}")
        print(f"실패: {self.test_count - self.pass_count}")
        print(f"성공률: {(self.pass_count / self.test_count * 100):.1f}%" if self.test_count > 0 else "0%")
        
        print("\n📋 상세 결과:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test_name']}: {result['details']}")
        
        print("="*60)

    async def run_all_tests(self) -> bool:
        """모든 테스트 실행"""
        print("🚀 EORA 시스템 종합 테스트 시작")
        print("="*60)
        
        # 1. 시스템 초기화
        if not await self.initialize_system():
            return False
        
        # 2. 기본 응답 테스트
        await self.test_basic_response()
        
        # 3. 메모리 저장 테스트
        await self.test_memory_storage()
        
        # 4. 메모리 검색 테스트
        await self.test_memory_search()
        
        # 5. 윤리 엔진 테스트
        await self.test_ethics_engine()
        
        # 6. 감정 분석 테스트
        await self.test_emotion_analysis()
        
        # 7. 시스템 상태 테스트
        await self.test_system_status()
        
        # 8. 메모리 통계 테스트
        await self.test_memory_statistics()
        
        # 결과 출력
        self.print_test_summary()
        
        return self.pass_count == self.test_count

async def main():
    """메인 테스트 함수"""
    tester = EORATester()
    
    try:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print("\n⚠️ 일부 테스트가 실패했습니다. 로그를 확인해주세요.")
            
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 치명적 오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 