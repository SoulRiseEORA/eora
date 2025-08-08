#!/usr/bin/env python3
"""
Railway 배포 사이트 상세 기능 테스트
세션 삭제, 홈 버튼, 포인트 시스템 등의 문제를 진단합니다.
"""

import requests
import json
import time
from datetime import datetime

def test_session_management():
    """세션 관리 기능 테스트"""
    print("🔄 세션 관리 기능 테스트")
    print("=" * 30)
    
    base_url = "https://web-production-40c0.up.railway.app"
    
    # 1. 세션 생성 테스트
    try:
        print("📝 1. 세션 생성 테스트...")
        create_payload = {
            "name": "테스트 세션",
            "user_id": "test_user"
        }
        
        response = requests.post(f"{base_url}/api/sessions", 
                               json=create_payload, 
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('_id') or data.get('session_id')
            print(f"   ✅ 세션 생성 성공: {session_id}")
            
            # 2. 세션 목록 조회
            print("📋 2. 세션 목록 조회 테스트...")
            list_response = requests.get(f"{base_url}/api/sessions", timeout=10)
            if list_response.status_code == 200:
                sessions = list_response.json()
                print(f"   ✅ 세션 목록 조회 성공: {len(sessions)}개 세션")
            else:
                print(f"   ❌ 세션 목록 조회 실패: {list_response.status_code}")
            
            # 3. 세션 삭제 테스트
            if session_id:
                print("🗑️ 3. 세션 삭제 테스트...")
                delete_response = requests.delete(f"{base_url}/api/sessions/{session_id}", 
                                                timeout=10)
                if delete_response.status_code == 200:
                    print("   ✅ 세션 삭제 성공")
                else:
                    print(f"   ❌ 세션 삭제 실패: {delete_response.status_code}")
                    print(f"   응답: {delete_response.text}")
            
        else:
            print(f"   ❌ 세션 생성 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 세션 관리 테스트 오류: {e}")

def test_points_system():
    """포인트 시스템 테스트"""
    print("\n💰 포인트 시스템 테스트")
    print("=" * 30)
    
    base_url = "https://web-production-40c0.up.railway.app"
    
    endpoints = [
        ("/api/user/points", "사용자 포인트 조회"),
        ("/api/points/packages", "포인트 패키지 조회"),
        ("/api/user/stats", "사용자 통계")
    ]
    
    for endpoint, description in endpoints:
        try:
            print(f"📊 {description} 테스트... ({endpoint})")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {description} 성공")
                try:
                    data = response.json()
                    if 'points' in data:
                        print(f"   📈 포인트: {data['points']}")
                except:
                    pass
            else:
                print(f"   ❌ {description} 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {description} 오류: {e}")

def test_navigation_apis():
    """네비게이션 관련 API 테스트"""
    print("\n🧭 네비게이션 API 테스트")
    print("=" * 30)
    
    base_url = "https://web-production-40c0.up.railway.app"
    
    pages = [
        ("/", "홈 페이지"),
        ("/dashboard", "대시보드"),
        ("/memory", "기억 관리"),
        ("/prompts", "프롬프트 관리")
    ]
    
    for page, description in pages:
        try:
            print(f"🏠 {description} 접속 테스트... ({page})")
            response = requests.get(f"{base_url}{page}", timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {description} 접속 성공")
            elif response.status_code == 404:
                print(f"   ⚠️ {description} 페이지 없음 (404)")
            else:
                print(f"   ❌ {description} 접속 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {description} 오류: {e}")

def test_static_files():
    """정적 파일 로딩 테스트"""
    print("\n📁 정적 파일 로딩 테스트")
    print("=" * 30)
    
    base_url = "https://web-production-40c0.up.railway.app"
    
    # JavaScript 및 CSS 파일들 확인
    static_files = [
        "/static/css/main.css",
        "/static/js/main.js", 
        "/static/js/chat.js"
    ]
    
    for file_path in static_files:
        try:
            print(f"📄 정적 파일 확인... ({file_path})")
            response = requests.get(f"{base_url}{file_path}", timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ 파일 로딩 성공 ({len(response.content)} bytes)")
            elif response.status_code == 404:
                print(f"   ⚠️ 파일 없음 (404)")
            else:
                print(f"   ❌ 파일 로딩 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 파일 로딩 오류: {e}")

def check_cors_and_headers():
    """CORS 및 헤더 확인"""
    print("\n🔒 CORS 및 헤더 확인")
    print("=" * 30)
    
    try:
        base_url = "https://web-production-40c0.up.railway.app"
        response = requests.get(f"{base_url}/chat", timeout=10)
        
        headers = response.headers
        print("📋 응답 헤더:")
        
        important_headers = [
            'Content-Security-Policy',
            'X-Frame-Options', 
            'Access-Control-Allow-Origin',
            'Content-Type'
        ]
        
        for header in important_headers:
            value = headers.get(header, "없음")
            print(f"   {header}: {value}")
            
    except Exception as e:
        print(f"❌ 헤더 확인 오류: {e}")

def main():
    """메인 함수"""
    print("🔍 Railway 배포 사이트 상세 진단")
    print("=" * 50)
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 각 기능별 테스트 실행
    test_session_management()
    test_points_system()
    test_navigation_apis()
    test_static_files()
    check_cors_and_headers()
    
    print("\n" + "=" * 50)
    print("💡 문제 해결 방법:")
    print("1. 브라우저 개발자 도구(F12) > Console 탭에서 JavaScript 오류 확인")
    print("2. Network 탭에서 실패한 요청들 확인")
    print("3. Railway 대시보드 > Service > Variables에서 환경변수 재확인")
    print("4. Railway 대시보드 > Service > Deployments > Logs에서 서버 오류 확인")
    print("=" * 50)

if __name__ == "__main__":
    main() 