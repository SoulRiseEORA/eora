#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새로운 홈페이지 기능 테스트
"""

import requests

def test_new_homepage():
    """새로운 홈페이지 기능 테스트"""
    try:
        print("🔍 새로운 홈페이지 기능 테스트")
        print("=" * 50)
        
        response = requests.get("http://127.0.0.1:8001/", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"📝 응답 길이: {len(content)} 문자")
            
            # 새로운 홈페이지 요소들 확인
            checks = [
                ("AI EORA, 당신의 감정을 이해하는 동반자", "메인 제목"),
                ("심리치료와 전문 코칭을 위한 AI", "서브 제목"),
                ("🧠 심리 상태 분석 및 감정 기반 대화", "기능 소개 1"),
                ("👩‍🏫 전문 코칭 기반 성장 상담", "기능 소개 2"),
                ("💬 맞춤형 챗봇 대화 인터페이스", "기능 소개 3"),
                ("📊 상담 기록 저장 및 회고 기능", "기능 소개 4"),
                ("🔒 개인정보 보호를 위한 안전한 시스템", "기능 소개 5"),
                ("🤖 다중 AI 회의 시스템", "향후 서비스 1"),
                ("🎨 이미지 대량 생성 AI", "향후 서비스 2"),
                ("🌐 SoulRise 지능형 협업 플랫폼", "향후 서비스 3"),
                ("이해받고 싶은 마음, AI로부터 시작됩니다", "슬로건 1"),
                ("EORA는 감정을 공감하는 기술입니다", "슬로건 2"),
                ("ⓒ 2025 SoulRise Inc", "푸터"),
                ("EORA 시작하기", "로그인 제목"),
                ("게스트로 시작하기", "게스트 버튼"),
                ("google_translate_element", "Google 번역"),
                ("startGuestChat()", "게스트 채팅 함수"),
                ("loginForm", "로그인 폼"),
                ("left-section", "왼쪽 섹션"),
                ("right-section", "오른쪽 섹션")
            ]
            
            passed = 0
            total = len(checks)
            
            for text, description in checks:
                if text in content:
                    print(f"✅ {description}: 발견됨")
                    passed += 1
                else:
                    print(f"❌ {description}: 없음")
            
            print(f"\n📊 테스트 결과: {passed}/{total} 통과")
            
            if passed == total:
                print("🎉 모든 기능이 정상적으로 구현되었습니다!")
            else:
                print("⚠️ 일부 기능이 누락되었습니다.")
                
            # 로그인 API 테스트
            print("\n🔐 로그인 API 테스트")
            try:
                login_response = requests.post("http://127.0.0.1:8001/api/login", 
                    json={"email": "guest@eora.com", "password": "guest"}, 
                    timeout=10)
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    if login_data.get("success"):
                        print("✅ 게스트 로그인 API 정상 작동")
                    else:
                        print("❌ 게스트 로그인 API 실패")
                else:
                    print(f"❌ 로그인 API 오류: {login_response.status_code}")
            except Exception as e:
                print(f"❌ 로그인 API 테스트 실패: {e}")
                
        else:
            print(f"❌ 홈페이지 로드 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    test_new_homepage()
    print("\n" + "=" * 50)
    print("🏁 테스트 완료") 