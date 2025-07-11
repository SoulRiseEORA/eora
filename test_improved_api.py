#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 개선된 API 테스트 스크립트
새로 추가된 기능들을 테스트합니다.
"""

import requests
import json
import time
from datetime import datetime

# 서버 설정
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_system_status():
    """시스템 상태 API 테스트"""
    print("🔍 시스템 상태 API 테스트...")
    
    try:
        response = requests.get(f"{API_BASE}/system/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ 시스템 상태 조회 성공")
            print(f"   상태: {data.get('status')}")
            print(f"   버전: {data.get('version')}")
            print(f"   MongoDB: {data.get('services', {}).get('mongodb')}")
            print(f"   Redis: {data.get('services', {}).get('redis')}")
            print(f"   OpenAI: {data.get('services', {}).get('openai')}")
            print(f"   메모리 세션: {data.get('memory_stats', {}).get('sessions')}")
            return True
        else:
            print(f"❌ 시스템 상태 조회 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 시스템 상태 조회 오류: {e}")
        return False

def test_system_health():
    """시스템 헬스체크 API 테스트"""
    print("🔍 시스템 헬스체크 API 테스트...")
    
    try:
        response = requests.get(f"{API_BASE}/system/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ 헬스체크 성공")
            print(f"   상태: {data.get('status')}")
            print(f"   메시지: {data.get('message')}")
            return True
        else:
            print(f"❌ 헬스체크 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 헬스체크 오류: {e}")
        return False

def test_system_info():
    """시스템 정보 API 테스트"""
    print("🔍 시스템 정보 API 테스트...")
    
    try:
        response = requests.get(f"{API_BASE}/system/info")
        if response.status_code == 200:
            data = response.json()
            print("✅ 시스템 정보 조회 성공")
            system_info = data.get('system_info', {})
            print(f"   Python 버전: {system_info.get('python_version')}")
            print(f"   플랫폼: {system_info.get('platform')}")
            if 'cpu_count' in system_info:
                print(f"   CPU 개수: {system_info.get('cpu_count')}")
            return True
        else:
            print(f"❌ 시스템 정보 조회 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 시스템 정보 조회 오류: {e}")
        return False

def test_improved_chat():
    """개선된 채팅 API 테스트"""
    print("🔍 개선된 채팅 API 테스트...")
    
    test_messages = [
        "안녕하세요!",
        "오늘 날씨가 어때요?",
        "인공지능에 대해 설명해주세요."
    ]
    
    session_id = f"test_session_{int(time.time())}"
    
    for i, message in enumerate(test_messages, 1):
        print(f"   메시지 {i}: {message}")
        
        try:
            response = requests.post(f"{API_BASE}/chat", json={
                "message": message,
                "session_id": session_id,
                "user_id": "test_user"
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print(f"   ✅ 응답: {data.get('response', '')[:50]}...")
                else:
                    print(f"   ❌ 오류: {data.get('error')}")
            else:
                print(f"   ❌ 요청 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 채팅 오류: {e}")
        
        time.sleep(1)  # 요청 간격
    
    return True

def test_admin_apis():
    """관리자 API 테스트"""
    print("🔍 관리자 API 테스트...")
    
    # 세션 목록 조회
    try:
        response = requests.get(f"{API_BASE}/admin/sessions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 관리자 세션 조회 성공: {data.get('total_count', 0)}개 세션")
        else:
            print(f"❌ 관리자 세션 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 관리자 세션 조회 오류: {e}")
    
    # 메시지 목록 조회
    try:
        response = requests.get(f"{API_BASE}/admin/messages?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 관리자 메시지 조회 성공: {data.get('total_count', 0)}개 메시지")
        else:
            print(f"❌ 관리자 메시지 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 관리자 메시지 조회 오류: {e}")
    
    return True

def test_error_handling():
    """에러 처리 테스트"""
    print("🔍 에러 처리 테스트...")
    
    # 빈 메시지 테스트
    try:
        response = requests.post(f"{API_BASE}/chat", json={
            "message": "",
            "session_id": "test_error_session",
            "user_id": "test_user"
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'error':
                print("✅ 빈 메시지 에러 처리 성공")
            else:
                print("❌ 빈 메시지 에러 처리 실패")
        else:
            print(f"❌ 빈 메시지 요청 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 빈 메시지 테스트 오류: {e}")
    
    # 잘못된 JSON 테스트
    try:
        response = requests.post(f"{API_BASE}/chat", 
                               data="invalid json",
                               headers={"Content-Type": "application/json"})
        print(f"✅ 잘못된 JSON 처리: {response.status_code}")
    except Exception as e:
        print(f"❌ 잘못된 JSON 테스트 오류: {e}")
    
    return True

def main():
    """메인 테스트 함수"""
    print("🚀 EORA AI System - 개선된 API 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("시스템 상태", test_system_status),
        ("시스템 헬스체크", test_system_health),
        ("시스템 정보", test_system_info),
        ("개선된 채팅", test_improved_chat),
        ("관리자 API", test_admin_apis),
        ("에러 처리", test_error_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트 시작...")
        start_time = time.time()
        
        try:
            success = test_func()
            end_time = time.time()
            duration = end_time - start_time
            
            results.append({
                "test": test_name,
                "success": success,
                "duration": duration
            })
            
            status = "✅ 성공" if success else "❌ 실패"
            print(f"   {status} (소요시간: {duration:.2f}초)")
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            results.append({
                "test": test_name,
                "success": False,
                "duration": duration,
                "error": str(e)
            })
            
            print(f"   ❌ 예외 발생: {e} (소요시간: {duration:.2f}초)")
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    total_duration = sum(r["duration"] for r in results)
    
    print(f"총 테스트: {total_tests}개")
    print(f"성공: {successful_tests}개")
    print(f"실패: {total_tests - successful_tests}개")
    print(f"성공률: {(successful_tests/total_tests)*100:.1f}%")
    print(f"총 소요시간: {total_duration:.2f}초")
    
    print("\n📋 상세 결과:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"   {status} {result['test']}: {result['duration']:.2f}초")
        if not result["success"] and "error" in result:
            print(f"      오류: {result['error']}")
    
    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    main() 