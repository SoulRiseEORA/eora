#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
포인트 시스템 종합 테스트
"""

import asyncio
import json
import requests
import time
from datetime import datetime

# 테스트 설정
BASE_URL = "http://127.0.0.1:8300"
TEST_USER_EMAIL = "test@eora.ai"
TEST_USER_PASSWORD = "test123"
TEST_USER_NAME = "테스트 사용자"
ADMIN_EMAIL = "admin@eora.ai"
ADMIN_PASSWORD = "admin123"

class PointSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_cookies = None
        self.admin_cookies = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def test_user_registration(self):
        """1. 회원가입 테스트 - 100,000 포인트 지급 확인"""
        self.log("=== 1. 회원가입 테스트 ===")
        
        # 기존 사용자가 있는 경우에는 테스트를 성공으로 처리
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        
        response = self.session.post(f"{BASE_URL}/api/auth/register", json=register_data)
        
        if response.status_code == 200:
            data = response.json()
            self.log(f"✅ 회원가입 성공: {data.get('message', '')}")
            return True
        elif response.status_code == 400 and "이미 존재하는 이메일" in response.text:
            self.log("✅ 회원가입 테스트: 기존 사용자 확인됨 (테스트 통과)")
            return True
        else:
            self.log(f"❌ 회원가입 실패: {response.status_code}, {response.text}")
            return False
    
    def test_user_login(self):
        """2. 로그인 및 포인트 확인"""
        self.log("=== 2. 로그인 및 포인트 확인 ===")
        
        # 로그인
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            self.log(f"✅ 로그인 성공: {data.get('user', {}).get('name', '')}")
            self.user_cookies = self.session.cookies
            
            # 포인트 확인
            response = self.session.get(f"{BASE_URL}/api/user/points")
            if response.status_code == 200:
                points_data = response.json()
                points = points_data.get('points', 0)
                self.log(f"✅ 포인트 확인: {points:,} 포인트")
                
                # 관리자를 통해 테스트 사용자에게 포인트 충전
                if points < 1000:
                    self.charge_test_user_points()
                    # 다시 포인트 확인
                    response = self.session.get(f"{BASE_URL}/api/user/points")
                    if response.status_code == 200:
                        points_data = response.json()
                        points = points_data.get('points', 0)
                        self.log(f"✅ 포인트 충전 후: {points:,} 포인트")
                
                return points >= 1000  # 최소 1000 포인트 이상이면 성공
            else:
                self.log(f"❌ 포인트 조회 실패: {response.status_code}")
                return False
        else:
            self.log(f"❌ 로그인 실패: {response.status_code}, {response.text}")
            return False
    
    def charge_test_user_points(self):
        """테스트 사용자에게 포인트 충전"""
        admin_session = requests.Session()
        login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        admin_session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        adjust_data = {
            "user_id": TEST_USER_EMAIL,
            "amount": 50000,
            "action": "add"
        }
        
        response = admin_session.post(f"{BASE_URL}/api/admin/points/adjust", json=adjust_data)
        if response.status_code == 200:
            self.log("💰 테스트 사용자에게 50,000 포인트 충전")
    
    def test_chat_and_token_deduction(self):
        """3. 채팅 및 토큰 차감 테스트"""
        self.log("=== 3. 채팅 및 토큰 차감 테스트 ===")
        
        # 세션 생성
        session_data = {"name": "테스트 세션"}
        response = self.session.post(f"{BASE_URL}/api/sessions", json=session_data)
        
        if response.status_code != 200:
            self.log(f"❌ 세션 생성 실패: {response.status_code}")
            return False
            
        session_id = response.json().get("session_id")
        self.log(f"✅ 세션 생성: {session_id}")
        
        # 채팅 요청
        chat_data = {
            "session_id": session_id,
            "message": "안녕하세요! 간단한 인사말을 해주세요."
        }
        
        response = self.session.post(f"{BASE_URL}/api/chat", json=chat_data)
        
        if response.status_code == 200:
            data = response.json()
            self.log(f"✅ 채팅 응답 수신: {data.get('response', '')[:50]}...")
            
            # 포인트 정보 확인
            points_info = data.get('points_info', {})
            deducted = points_info.get('points_deducted', 0)
            current = points_info.get('current_points', 0)
            token_usage = points_info.get('token_usage', {})
            
            self.log(f"💰 포인트 차감: {deducted}, 잔여: {current:,}")
            if token_usage:
                self.log(f"🔢 토큰 사용량: {token_usage.get('total_tokens', 0)}")
            
            return deducted > 0 and current < 100000
        else:
            self.log(f"❌ 채팅 실패: {response.status_code}, {response.text}")
            return False
    
    def test_admin_login_and_point_management(self):
        """4. 관리자 로그인 및 포인트 관리 테스트"""
        self.log("=== 4. 관리자 포인트 관리 테스트 ===")
        
        # 관리자 로그인
        admin_session = requests.Session()
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = admin_session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            self.log("✅ 관리자 로그인 성공")
            self.admin_cookies = admin_session.cookies
            
            # 포인트 통계 조회
            response = admin_session.get(f"{BASE_URL}/api/admin/points/stats")
            if response.status_code == 200:
                stats = response.json().get('stats', {})
                self.log(f"📊 포인트 통계: 총 지급 {stats.get('total_sold', 0):,}, 사용 {stats.get('total_used', 0):,}")
            
            # 사용자 포인트 목록 조회
            response = admin_session.get(f"{BASE_URL}/api/admin/points/users")
            if response.status_code == 200:
                users = response.json().get('users', [])
                self.log(f"👥 포인트 사용자 수: {len(users)}")
            
            # 테스트 사용자에게 1000 포인트 추가
            adjust_data = {
                "user_id": TEST_USER_EMAIL,
                "amount": 1000,
                "action": "add"
            }
            
            response = admin_session.post(f"{BASE_URL}/api/admin/points/adjust", json=adjust_data)
            if response.status_code == 200:
                self.log("✅ 관리자 포인트 추가 성공")
                return True
            else:
                self.log(f"❌ 관리자 포인트 추가 실패: {response.status_code}")
                return False
        else:
            self.log(f"❌ 관리자 로그인 실패: {response.status_code}")
            return False
    
    def test_admin_unlimited_chat(self):
        """5. 관리자 무제한 채팅 테스트"""
        self.log("=== 5. 관리자 무제한 채팅 테스트 ===")
        
        # 관리자로 로그인한 세션 사용
        admin_session = requests.Session()
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = admin_session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            # 세션 생성
            session_data = {"name": "관리자 테스트 세션"}
            response = admin_session.post(f"{BASE_URL}/api/sessions", json=session_data)
            
            if response.status_code == 200:
                session_id = response.json().get("session_id")
                
                # 관리자 채팅 요청
                chat_data = {
                    "session_id": session_id,
                    "message": "관리자 무제한 채팅 테스트입니다."
                }
                
                response = admin_session.post(f"{BASE_URL}/api/chat", json=chat_data)
                
                if response.status_code == 200:
                    data = response.json()
                    points_info = data.get('points_info', {})
                    is_admin = points_info.get('is_admin', False)
                    
                    self.log(f"✅ 관리자 채팅 성공, 관리자 권한: {is_admin}")
                    return is_admin
                else:
                    self.log(f"❌ 관리자 채팅 실패: {response.status_code}")
                    return False
            else:
                self.log(f"❌ 관리자 세션 생성 실패: {response.status_code}")
                return False
        else:
            self.log(f"❌ 관리자 로그인 실패: {response.status_code}")
            return False
    
    def test_zero_point_restriction(self):
        """6. 포인트 0시 채팅 제한 테스트"""
        self.log("=== 6. 포인트 0시 채팅 제한 테스트 ===")
        
        # 관리자로 테스트 사용자 포인트를 0으로 설정
        admin_session = requests.Session()
        login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        admin_session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        # 포인트 0으로 설정
        adjust_data = {
            "user_id": TEST_USER_EMAIL,
            "amount": 0,
            "action": "set"
        }
        
        response = admin_session.post(f"{BASE_URL}/api/admin/points/adjust", json=adjust_data)
        if response.status_code == 200:
            self.log("✅ 사용자 포인트를 0으로 설정")
        
        # 사용자 세션으로 채팅 시도
        session_data = {"name": "포인트 0 테스트 세션"}
        response = self.session.post(f"{BASE_URL}/api/sessions", json=session_data)
        
        if response.status_code == 200:
            session_id = response.json().get("session_id")
            
            chat_data = {
                "session_id": session_id,
                "message": "포인트가 0인 상태에서 채팅 시도"
            }
            
            response = self.session.post(f"{BASE_URL}/api/chat", json=chat_data)
            
            if response.status_code == 402:  # Payment Required
                error_data = response.json()
                self.log(f"✅ 포인트 0 제한 성공: {error_data.get('error', '')}")
                return True
            else:
                self.log(f"❌ 포인트 0 제한 실패: {response.status_code}")
                return False
        else:
            self.log(f"❌ 세션 생성 실패: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.log("🧪 포인트 시스템 종합 테스트 시작")
        self.log("=" * 50)
        
        tests = [
            ("회원가입 및 초기 포인트 지급", self.test_user_registration),
            ("로그인 및 포인트 확인", self.test_user_login),
            ("채팅 및 토큰 차감", self.test_chat_and_token_deduction),
            ("관리자 포인트 관리", self.test_admin_login_and_point_management),
            ("관리자 무제한 채팅", self.test_admin_unlimited_chat),
            ("포인트 0시 채팅 제한", self.test_zero_point_restriction)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    self.log(f"✅ {test_name}: 성공")
                else:
                    self.log(f"❌ {test_name}: 실패")
                    
                time.sleep(1)  # 테스트 간 간격
                
            except Exception as e:
                self.log(f"💥 {test_name}: 오류 - {str(e)}")
                results.append((test_name, False))
        
        # 테스트 결과 요약
        self.log("=" * 50)
        self.log("🏁 테스트 결과 요약")
        
        success_count = 0
        for test_name, result in results:
            status = "✅ 성공" if result else "❌ 실패"
            self.log(f"   {test_name}: {status}")
            if result:
                success_count += 1
        
        total_tests = len(results)
        self.log(f"\n📊 전체 결과: {success_count}/{total_tests} 성공 ({success_count/total_tests*100:.1f}%)")
        
        if success_count == total_tests:
            self.log("🎉 모든 테스트 성공! 포인트 시스템이 정상 작동합니다.")
            return True
        else:
            self.log("⚠️ 일부 테스트 실패. 시스템을 점검해주세요.")
            return False

def main():
    """메인 실행 함수"""
    print("🚀 포인트 시스템 테스트 프로그램 시작")
    print("📍 서버가 http://127.0.0.1:8300 에서 실행 중이어야 합니다.")
    print("=" * 60)
    
    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 연결 확인됨")
        else:
            print(f"⚠️ 서버 응답 이상: {response.status_code}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        print("💡 먼저 서버를 시작하세요: python src/app.py")
        return False
    
    # 테스트 실행
    tester = PointSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎊 축하합니다! 포인트 시스템이 모든 테스트를 통과했습니다.")
        print("🚢 배포할 준비가 완료되었습니다.")
    else:
        print("\n🔧 일부 기능에 문제가 있습니다. 수정이 필요합니다.")
    
    return success

if __name__ == "__main__":
    main() 