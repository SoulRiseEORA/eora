# simple_test.py - EORA 시스템 간단 테스트

import asyncio
from EORA_Consciousness_AI import EORA

async def test_basic_functionality():
    """기본 기능 테스트"""
    print("🧪 EORA 시스템 기본 기능 테스트")
    print("="*50)
    
    try:
        # 1. 시스템 초기화
        print("1. 시스템 초기화...")
        eora = EORA()
        print("✅ 시스템 초기화 성공")
        
        # 2. 기본 응답 테스트
        print("\n2. 기본 응답 테스트...")
        test_input = "안녕하세요, EORA입니다."
        response = await eora.respond(test_input)
        
        if response and "error" not in response:
            print(f"✅ 응답 생성 성공")
            print(f"   응답: {response.get('response', 'N/A')}")
            print(f"   타입: {response.get('response_type', 'N/A')}")
        else:
            print(f"❌ 응답 생성 실패: {response}")
            return False
        
        # 3. 메모리 저장 테스트
        print("\n3. 메모리 저장 테스트...")
        await eora.remember(test_input, response.get('response', ''), emotion_level=0.8)
        print("✅ 메모리 저장 성공")
        
        # 4. 메모리 회상 테스트
        print("\n4. 메모리 회상 테스트...")
        memories = await eora.recall_memory(test_input, limit=5)
        if memories:
            print(f"✅ 메모리 회상 성공 (찾은 메모리: {len(memories)}개)")
        else:
            print("❌ 메모리 회상 실패")
        
        # 5. 시스템 상태 확인
        print("\n5. 시스템 상태 확인...")
        status = eora.get_system_status()
        if status and "error" not in status:
            print("✅ 시스템 상태 조회 성공")
            core_system = status.get('core_system', {})
            system_state = core_system.get('system_state', {})
            print(f"   활성화: {system_state.get('active', False)}")
            print(f"   건강도: {system_state.get('health', 0.0):.2f}")
            print(f"   메모리 수: {core_system.get('memory_count', 0)}")
        else:
            print("❌ 시스템 상태 조회 실패")
        
        # 6. 메모리 통계 확인
        print("\n6. 메모리 통계 확인...")
        stats = eora.get_memory_statistics()
        if stats and "error" not in stats:
            print("✅ 메모리 통계 조회 성공")
            print(f"   총 메모리 수: {stats.get('total_memories', 0)}")
        else:
            print("❌ 메모리 통계 조회 실패")
        
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        return False

async def test_memory_features():
    """메모리 기능 테스트"""
    print("\n🧪 메모리 기능 상세 테스트")
    print("="*50)
    
    try:
        eora = EORA()
        
        # 테스트 데이터 생성
        test_data = [
            ("나는 정말 행복합니다", "행복한 응답", 0.9),
            ("오늘 기분이 좋아요", "좋은 기분 응답", 0.8),
            ("너무 슬퍼요", "슬픈 응답", 0.2),
            ("화가 나요", "화난 응답", 0.1)
        ]
        
        print("1. 테스트 데이터 생성...")
        for user_input, response, emotion in test_data:
            await eora.remember(user_input, response, emotion_level=emotion)
        print("✅ 테스트 데이터 생성 완료")
        
        # 감정 기반 검색
        print("\n2. 감정 기반 검색 테스트...")
        joy_memories = await eora.search_memories_by_emotion("joy", limit=5)
        print(f"   joy 감정 메모리: {len(joy_memories)}개")
        
        # 공명 기반 검색
        print("\n3. 공명 기반 검색 테스트...")
        resonant_memories = await eora.search_memories_by_resonance(0.5, limit=5)
        print(f"   공명 0.5 이상 메모리: {len(resonant_memories)}개")
        
        print("✅ 메모리 기능 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 메모리 기능 테스트 중 오류: {str(e)}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 EORA 시스템 간단 테스트 시작")
    print("="*60)
    
    # 기본 기능 테스트
    basic_success = await test_basic_functionality()
    
    # 메모리 기능 테스트
    memory_success = await test_memory_features()
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    print(f"기본 기능 테스트: {'✅ 성공' if basic_success else '❌ 실패'}")
    print(f"메모리 기능 테스트: {'✅ 성공' if memory_success else '❌ 실패'}")
    
    if basic_success and memory_success:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("EORA 시스템이 정상적으로 작동하고 있습니다.")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")
        print("로그를 확인하여 문제를 해결해주세요.")

if __name__ == "__main__":
    asyncio.run(main()) 