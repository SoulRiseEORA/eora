#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Favicon 테스트 스크립트
"""

import requests
import time

def test_favicon():
    """favicon.ico 테스트"""
    try:
        print("🔍 Favicon 테스트 시작...")
        
        # favicon.ico 요청
        response = requests.get("http://127.0.0.1:8001/favicon.ico", timeout=10)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        print(f"📄 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Favicon 로드 성공!")
            print(f"📝 파일 크기: {len(response.content)} 바이트")
            print(f"🎨 Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            # 파일이 실제로 favicon인지 확인
            if response.content.startswith(b'\x00\x00\x01\x00'):
                print("✅ 유효한 ICO 파일 형식 확인")
            else:
                print("⚠️ ICO 파일 형식이 아닐 수 있습니다")
                
        else:
            print(f"❌ Favicon 로드 실패: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

def test_home_with_favicon():
    """홈 페이지에서 favicon 링크 확인"""
    try:
        print("\n🔍 홈 페이지 Favicon 링크 테스트...")
        
        response = requests.get("http://127.0.0.1:8001/", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            if 'favicon.ico' in content:
                print("✅ 홈 페이지에 favicon 링크 발견")
                
                if 'link rel="icon"' in content:
                    print("✅ 올바른 favicon 링크 태그 확인")
                else:
                    print("⚠️ favicon 링크 태그 형식 확인 필요")
                    
            else:
                print("❌ 홈 페이지에 favicon 링크가 없습니다")
                
        else:
            print(f"❌ 홈 페이지 로드 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 홈 페이지 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    print("🎨 EORA AI System Favicon 테스트")
    print("=" * 50)
    
    test_favicon()
    test_home_with_favicon()
    
    print("\n" + "=" * 50)
    print("🏁 Favicon 테스트 완료")
    print("\n💡 브라우저에서 http://127.0.0.1:8001/ 에 접속하여")
    print("   탭에 보라색 그라데이션의 E 아이콘이 표시되는지 확인하세요!") 