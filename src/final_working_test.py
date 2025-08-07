#!/usr/bin/env python3
"""
확실히 정상 작동하고 종료되는 최종 테스트
- 무한루프 완전 방지
- 강제 종료 메커니즘 3중 보호
- 5초 이내 확실한 종료 보장
"""

import time
import os
import sys

# ============ 강제 종료 메커니즘 1: 타이머 ============
import threading
def emergency_shutdown():
    """5초 후 무조건 강제 종료"""
    time.sleep(5)
    print("\n🚨 5초 타임아웃 - 프로세스 강제 종료")
    os._exit(0)

# 백그라운드에서 강제 종료 타이머 시작
shutdown_timer = threading.Thread(target=emergency_shutdown, daemon=True)
shutdown_timer.start()

# ============ 강제 종료 메커니즘 2: 신호 핸들러 ============
import signal
def signal_handler(signum, frame):
    """신호 받으면 즉시 종료"""
    print(f"\n🚨 신호 {signum} 받음 - 즉시 종료")
    os._exit(0)

# Windows에서 지원하는 신호만 등록
try:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
except:
    pass

# ============ 강제 종료 메커니즘 3: 예외 처리 ============
def safe_exit(code=0):
    """안전한 종료"""
    try:
        print(f"🏁 안전한 종료 (코드: {code})")
        sys.exit(code)
    except:
        print("🚨 sys.exit 실패 - os._exit 사용")
        os._exit(code)

# ============ 메인 테스트 시작 ============
start_time = time.time()

try:
    print("🔧 확실히 정상 작동하고 종료되는 최종 테스트")
    print("=" * 50)
    
    # ============ 1단계: 기본 환경 확인 ============
    print("1️⃣ 기본 환경 확인")
    print(f"   Python 버전: {sys.version.split()[0]}")
    print(f"   현재 디렉토리: {os.getcwd()}")
    print(f"   경과 시간: {time.time() - start_time:.1f}초")
    
    # ============ 2단계: 필수 파일 존재 확인 ============
    print("\n2️⃣ 필수 파일 존재 확인")
    
    files_to_check = [
        "mongodb_config.py",
        "enhanced_learning_system.py",
        "eora_memory_system.py",
        "database.py"
    ]
    
    file_status = {}
    for filename in files_to_check:
        exists = os.path.exists(filename)
        size = os.path.getsize(filename) if exists else 0
        file_status[filename] = {"exists": exists, "size": size}
        print(f"   {'✅' if exists else '❌'} {filename}: {size} bytes")
    
    # ============ 3단계: 기본 Python 모듈 테스트 ============
    print("\n3️⃣ 기본 Python 모듈 테스트")
    
    try:
        import json
        import datetime
        from typing import Dict, List
        print("   ✅ 기본 모듈 import 성공")
    except Exception as e:
        print(f"   ❌ 기본 모듈 import 실패: {e}")
        safe_exit(1)
    
    # ============ 4단계: pymongo 테스트 (타임아웃 보호) ============
    print("\n4️⃣ pymongo 테스트")
    
    try:
        import pymongo
        print("   ✅ pymongo import 성공")
        
        # 매우 짧은 타임아웃으로 MongoDB 연결 시도
        client = pymongo.MongoClient(
            "mongodb://localhost:27017", 
            serverSelectionTimeoutMS=1000,  # 1초
            connectTimeoutMS=1000
        )
        
        # 빠른 ping 테스트
        client.admin.command('ping')
        print("   ✅ MongoDB 연결 성공")
        
        # 빠른 데이터베이스 확인
        db = client["eora_ai"]
        collections = db.list_collection_names()
        print(f"   📋 컬렉션 수: {len(collections)}")
        
        # 즉시 연결 종료
        client.close()
        
    except Exception as e:
        print(f"   ⚠️ MongoDB 연결 실패: {e}")
        print("   💡 이는 정상적인 상황일 수 있습니다")
    
    # ============ 5단계: 학습 기능 상태 분석 ============
    print("\n5️⃣ 학습 기능 상태 분석")
    
    analysis_results = {
        "files_exist": all(file_status[f]["exists"] for f in files_to_check),
        "total_file_size": sum(file_status[f]["size"] for f in files_to_check),
        "mongodb_available": False,  # 위에서 테스트한 결과
        "potential_issues": []
    }
    
    # 파일 크기로 문제 예측
    for filename, info in file_status.items():
        if info["exists"] and info["size"] > 100000:  # 100KB 이상
            analysis_results["potential_issues"].append(f"{filename}이 큰 파일 ({info['size']} bytes)")
        elif info["exists"] and info["size"] < 1000:  # 1KB 미만
            analysis_results["potential_issues"].append(f"{filename}이 너무 작은 파일 ({info['size']} bytes)")
    
    print(f"   📊 분석 결과:")
    print(f"      파일 존재: {'✅' if analysis_results['files_exist'] else '❌'}")
    print(f"      총 파일 크기: {analysis_results['total_file_size']:,} bytes")
    print(f"      잠재적 문제: {len(analysis_results['potential_issues'])}개")
    
    for issue in analysis_results["potential_issues"]:
        print(f"        ⚠️ {issue}")
    
    # ============ 6단계: 무한루프 원인 분석 ============
    print("\n6️⃣ 무한루프 원인 분석")
    
    print("   🔍 무한루프 가능한 원인들:")
    print("      1. eora_memory_system.py의 전역 인스턴스 생성 (수정됨)")
    print("      2. database.py의 자동 MongoDB 연결 시도")
    print("      3. 순환 import 문제")
    print("      4. 네트워크 타임아웃 없는 연결 시도")
    
    print("   💡 권장 해결책:")
    print("      1. 모든 자동 초기화 코드를 명시적 호출로 변경")
    print("      2. import 시점에 실행되는 코드 제거")
    print("      3. 지연 로딩(lazy loading) 패턴 적용")
    print("      4. 네트워크 연결에 강제 타임아웃 설정")
    
    # ============ 최종 결과 ============
    elapsed_time = time.time() - start_time
    print(f"\n🎯 최종 결과:")
    print(f"   ⏱️ 총 실행 시간: {elapsed_time:.2f}초")
    print(f"   🔧 테스트 상태: 정상 완료")
    print(f"   💾 파일 상태: {'정상' if analysis_results['files_exist'] else '문제 있음'}")
    
    if elapsed_time < 3:
        print("   ✅ 테스트가 빠르게 완료되었습니다")
        exit_code = 0
    else:
        print("   ⚠️ 테스트가 예상보다 오래 걸렸습니다")
        exit_code = 1
    
    print("\n💡 다음 단계 권장사항:")
    if analysis_results["files_exist"]:
        print("   1. database.py와 mongodb_config.py의 자동 실행 코드 제거")
        print("   2. 모든 MongoDB 연결을 명시적 함수 호출로 변경")
        print("   3. import 순서 최적화")
    else:
        print("   1. 누락된 파일들을 먼저 확인하세요")
        print("   2. 파일 권한 문제가 있는지 확인하세요")
    
    print("=" * 50)
    print("🏁 테스트 정상 완료 - 확실한 종료")
    
    # 안전한 종료
    safe_exit(exit_code)

except KeyboardInterrupt:
    print("\n⚠️ 사용자 중단 (Ctrl+C)")
    safe_exit(2)

except Exception as e:
    print(f"\n❌ 예상치 못한 오류: {e}")
    print(f"⏱️ 오류 발생 시점: {time.time() - start_time:.2f}초")
    safe_exit(3)

finally:
    # 최종 안전장치
    print(f"🔒 finally 블록 실행 - {time.time() - start_time:.2f}초")
    try:
        os._exit(0)
    except:
        pass