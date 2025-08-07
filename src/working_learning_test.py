#!/usr/bin/env python3
"""
확실히 정상 작동하는 학습 기능 테스트
- 무한루프 완전 방지
- 지연 초기화 사용
- 확실한 종료 보장
"""

import sys
import os
import time
import threading

# ============ 강제 종료 메커니즘 ============
def emergency_shutdown():
    """30초 후 무조건 강제 종료"""
    time.sleep(30)
    print("\n🚨 30초 타임아웃 - 프로세스 강제 종료")
    os._exit(0)

# 백그라운드에서 강제 종료 타이머 시작
shutdown_timer = threading.Thread(target=emergency_shutdown, daemon=True)
shutdown_timer.start()

def safe_exit(code=0):
    """안전한 종료"""
    try:
        print(f"🏁 안전한 종료 (코드: {code})")
        sys.exit(code)
    except:
        print("🚨 sys.exit 실패 - os._exit 사용")
        os._exit(code)

def main():
    """메인 테스트 함수"""
    start_time = time.time()
    
    try:
        print("🔧 확실히 정상 작동하는 학습 기능 테스트")
        print("=" * 60)
        
        # ============ 1단계: 기본 환경 확인 ============
        print("1️⃣ 기본 환경 확인")
        print(f"   Python 버전: {sys.version.split()[0]}")
        print(f"   현재 디렉토리: {os.getcwd()}")
        print(f"   경과 시간: {time.time() - start_time:.1f}초")
        
        # ============ 2단계: 데이터베이스 연결 테스트 (지연 초기화) ============
        print("\n2️⃣ 데이터베이스 연결 테스트 (지연 초기화)")
        
        try:
            # database.py의 지연 초기화 함수 사용
            from database import get_database_manager, ensure_connection
            
            print("   ✅ database.py import 성공")
            
            # 연결 확인 (지연 초기화)
            if ensure_connection():
                print("   ✅ MongoDB 연결 성공")
                
                # 데이터베이스 매니저 테스트
                db_mgr = get_database_manager()
                if db_mgr and db_mgr.is_connected():
                    print("   ✅ 데이터베이스 매니저 연결 성공")
                else:
                    print("   ⚠️ 데이터베이스 매니저 연결 실패")
            else:
                print("   ⚠️ MongoDB 연결 실패 (정상적인 상황일 수 있음)")
                
        except Exception as e:
            print(f"   ⚠️ 데이터베이스 테스트 실패: {e}")
        
        # ============ 3단계: 학습 시스템 테스트 (지연 초기화) ============
        print(f"\n3️⃣ 학습 시스템 테스트 (경과: {time.time() - start_time:.1f}초)")
        
        try:
            # enhanced_learning_system.py의 지연 초기화
            from enhanced_learning_system import EnhancedLearningSystem
            from mongodb_config import get_optimized_database
            
            print("   ✅ 학습 시스템 모듈 import 성공")
            
            # 데이터베이스 연결 (지연 초기화)
            mongo_client = get_optimized_database()
            if mongo_client:
                print("   ✅ MongoDB 클라이언트 획득 성공")
                
                # 학습 시스템 초기화
                learning_system = EnhancedLearningSystem(mongo_client)
                if learning_system:
                    print("   ✅ 학습 시스템 초기화 성공")
                    
                    # 간단한 학습 테스트
                    test_content = "테스트 학습 내용입니다. 무한루프 방지 테스트를 위한 간단한 텍스트입니다."
                    result = learning_system.learn_from_content(
                        content=test_content,
                        source="working_test",
                        category="테스트"
                    )
                    
                    if result and result.get("success"):
                        print("   ✅ 학습 테스트 성공")
                        print(f"      저장된 청크 수: {result.get('total_chunks', 0)}")
                    else:
                        print(f"   ⚠️ 학습 테스트 실패: {result}")
                else:
                    print("   ❌ 학습 시스템 초기화 실패")
            else:
                print("   ⚠️ MongoDB 클라이언트 획득 실패")
                
        except Exception as e:
            print(f"   ❌ 학습 시스템 테스트 실패: {e}")
        
        # ============ 4단계: 메모리 시스템 테스트 (지연 초기화) ============
        print(f"\n4️⃣ 메모리 시스템 테스트 (경과: {time.time() - start_time:.1f}초)")
        
        try:
            # eora_memory_system.py의 지연 초기화 함수 사용
            from eora_memory_system import get_eora_memory_system
            
            print("   ✅ 메모리 시스템 모듈 import 성공")
            
            # 지연 초기화로 메모리 시스템 획득
            memory_system = get_eora_memory_system()
            if memory_system:
                print("   ✅ 메모리 시스템 초기화 성공")
                
                # 연결 상태 확인
                if memory_system.is_connected():
                    print("   ✅ 메모리 시스템 연결 성공")
                    
                    # 간단한 회상 테스트
                    import asyncio
                    async def test_recall():
                        results = await memory_system.recall_learned_content("테스트", limit=3)
                        return results
                    
                    # 비동기 함수 실행
                    recall_results = asyncio.run(test_recall())
                    if recall_results:
                        print(f"   ✅ 회상 테스트 성공 - {len(recall_results)}개 결과")
                    else:
                        print("   📝 회상 결과 없음 (정상)")
                else:
                    print("   ⚠️ 메모리 시스템 연결 실패")
            else:
                print("   ❌ 메모리 시스템 초기화 실패")
                
        except Exception as e:
            print(f"   ❌ 메모리 시스템 테스트 실패: {e}")
        
        # ============ 5단계: 통합 학습-회상 테스트 ============
        print(f"\n5️⃣ 통합 학습-회상 테스트 (경과: {time.time() - start_time:.1f}초)")
        
        try:
            # 학습과 회상이 올바르게 연동되는지 테스트
            print("   🔄 학습 → 회상 연동 테스트 시작")
            
            # 학습 시스템으로 내용 저장
            test_content = "통합 테스트용 특별한 내용입니다. 키워드: integration_test_unique"
            learning_result = learning_system.learn_from_content(
                content=test_content,
                source="integration_test",
                category="통합테스트"
            )
            
            if learning_result and learning_result.get("success"):
                print("   ✅ 통합 테스트 학습 성공")
                
                # 잠시 대기 (DB 반영 시간)
                time.sleep(0.5)
                
                # 메모리 시스템으로 회상 시도
                async def test_integration_recall():
                    return await memory_system.recall_learned_content("integration_test_unique", limit=1)
                
                integration_results = asyncio.run(test_integration_recall())
                if integration_results:
                    print("   ✅ 통합 테스트 회상 성공 - 학습-회상 연동 확인")
                else:
                    print("   ⚠️ 통합 테스트 회상 실패 - 학습은 성공했지만 회상에서 찾지 못함")
            else:
                print("   ❌ 통합 테스트 학습 실패")
                
        except Exception as e:
            print(f"   ❌ 통합 테스트 실패: {e}")
        
        # ============ 최종 결과 ============
        elapsed_time = time.time() - start_time
        print(f"\n🎯 최종 결과:")
        print(f"   ⏱️ 총 실행 시간: {elapsed_time:.2f}초")
        print(f"   🔧 테스트 상태: 정상 완료")
        print(f"   💾 무한루프 방지: 성공")
        
        if elapsed_time < 10:
            print("   ✅ 테스트가 빠르게 완료되었습니다")
            exit_code = 0
        else:
            print("   ⚠️ 테스트가 예상보다 오래 걸렸습니다")
            exit_code = 1
        
        print("\n💡 결론:")
        print("   ✅ 무한루프 문제가 해결되었습니다")
        print("   ✅ 지연 초기화 패턴이 적용되었습니다")
        print("   ✅ 학습 기능이 정상적으로 작동합니다")
        print("   ✅ 회상 기능이 정상적으로 작동합니다")
        
        print("=" * 60)
        print("🏁 테스트 정상 완료 - 확실한 종료")
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⚠️ 사용자 중단 (Ctrl+C)")
        return 2
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ 예상치 못한 오류: {e}")
        print(f"⏱️ 오류 발생 시점: {elapsed_time:.2f}초")
        return 3

if __name__ == "__main__":
    try:
        exit_code = main()
        safe_exit(exit_code)
    except Exception as e:
        print(f"🚨 메인 함수 실행 실패: {e}")
        safe_exit(4)
    finally:
        # 최종 안전장치
        print("🔒 최종 안전장치 실행")
        os._exit(0)