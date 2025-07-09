#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
홈 페이지 템플릿 렌더링 테스트
"""

import requests
import time

def test_home_page():
    """홈 페이지 테스트"""
    try:
        print("🔍 홈 페이지 테스트 시작...")
        
        # 서버가 시작될 때까지 잠시 대기
        time.sleep(3)
        
        # 홈 페이지 요청
        response = requests.get("http://127.0.0.1:8001/", timeout=10)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        print(f"📄 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 홈 페이지 로드 성공!")
            print(f"📝 응답 내용 길이: {len(response.text)} 문자")
            
            # HTML 내용 확인
            if "EORA AI System" in response.text:
                print("✅ EORA AI System 텍스트 발견")
            else:
                print("⚠️ EORA AI System 텍스트를 찾을 수 없음")
                
            if "home.html" in response.text:
                print("✅ home.html 템플릿 내용 발견")
            else:
                print("⚠️ home.html 템플릿 내용을 찾을 수 없음")
                
        else:
            print(f"❌ 홈 페이지 로드 실패: {response.status_code}")
            print(f"📝 오류 내용: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

def test_health_endpoint():
    """헬스 엔드포인트 테스트"""
    try:
        print("\n🔍 헬스 엔드포인트 테스트...")
        
        response = requests.get("http://127.0.0.1:8001/health", timeout=10)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 헬스 엔드포인트 정상!")
            data = response.json()
            print(f"📝 서비스 상태: {data}")
        else:
            print(f"❌ 헬스 엔드포인트 오류: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 헬스 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    print("🚀 EORA AI System 홈 페이지 테스트")
    print("=" * 50)
    
    test_health_endpoint()
    test_home_page()
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료") 