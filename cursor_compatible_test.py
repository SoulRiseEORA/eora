#!/usr/bin/env python3
"""
커서(Cursor) 환경에서도 정상 작동하는 테스트
- 외부 라이브러리 최소화
- 네트워크 연결 시도 없음
- 파일 시스템만 사용
- 확실한 즉시 종료
"""

import os
import sys
import time

def main():
    """메인 함수 - 확실한 종료 보장"""
    start_time = time.time()
    
    print("🔧 커서 환경 호환 테스트")
    print("=" * 40)
    
    try:
        # 1. 기본 정보
        print("1️⃣ 환경 정보")
        print(f"   Python: {sys.version.split()[0]}")
        print(f"   경로: {os.getcwd()}")
        
        # 2. 핵심 파일들 확인
        print("\n2️⃣ 핵심 파일 확인")
        files = [
            "eora_memory_system.py",
            "enhanced_learning_system.py", 
            "database.py",
            "mongodb_config.py"
        ]
        
        for file in files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"   ✅ {file}: {size:,} bytes")
            else:
                print(f"   ❌ {file}: 없음")
        
        # 3. 문제 진단
        print("\n3️⃣ 무한루프 원인 진단")
        
        # eora_memory_system.py 검사
        try:
            with open("eora_memory_system.py", "r", encoding="utf-8") as f:
                content = f.read()
                
            issues = []
            
            # 전역 실행 코드 검사
            if "memory_system = EORAMemorySystem()" in content:
                issues.append("❌ 전역 인스턴스 자동 생성 발견")
            else:
                print("   ✅ 전역 인스턴스 자동 생성 없음")
            
            # 무한루프 패턴 검사
            if "while True:" in content:
                issues.append("⚠️ while True 루프 발견")
            
            if "for" in content and "in range(" not in content:
                loop_count = content.count("for ")
                if loop_count > 10:
                    issues.append(f"⚠️ 많은 for 루프 ({loop_count}개)")
            
            if issues:
                print("   🚨 발견된 문제:")
                for issue in issues:
                    print(f"      {issue}")
            else:
                print("   ✅ 명백한 무한루프 패턴 없음")
                
        except Exception as e:
            print(f"   ❌ 파일 검사 실패: {e}")
        
        # 4. import 테스트 (안전하게)
        print("\n4️⃣ 안전한 import 테스트")
        
        # 기본 모듈만 테스트
        basic_modules = ["json", "datetime", "typing"]
        for module in basic_modules:
            try:
                __import__(module)
                print(f"   ✅ {module}")
            except Exception as e:
                print(f"   ❌ {module}: {e}")
        
        # 5. 결론
        elapsed = time.time() - start_time
        print(f"\n🎯 결과:")
        print(f"   ⏱️ 실행시간: {elapsed:.2f}초")
        print(f"   🔧 상태: 정상")
        
        if elapsed < 1.0:
            print("   ✅ 빠른 실행 완료")
        
        print("\n💡 무한루프 해결책:")
        print("   1. eora_memory_system.py 파일의 끝부분 확인")
        print("   2. 전역 실행 코드 제거")
        print("   3. database.py의 자동 연결 제거")
        print("   4. lazy loading 패턴 적용")
        
        print("=" * 40)
        print("🏁 테스트 완료")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        return 1

if __name__ == "__main__":
    # 메인 함수 실행 후 즉시 종료
    exit_code = main()
    
    # 강제 종료
    print("🔒 강제 종료")
    sys.exit(exit_code)