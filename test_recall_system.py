#!/usr/bin/env python3
"""
고급 회상 시스템 테스트 스크립트
EORA AI의 메모리 회상 기능을 테스트합니다.
"""

import asyncio
import json
import requests
from datetime import datetime

# 테스트 설정
BASE_URL = "http://127.0.0.1:8002"  # 로컬 서버
# BASE_URL = "https://web-production-40c0.up.railway.app"  # Railway 서버

class RecallSystemTester:
    def __init__(self):
        self.session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.user_id = "test_user"
        
    def test_basic_recall(self):
        """기본 회상 기능 테스트"""
        print("🔍 기본 회상 기능 테스트")
        print("=" * 50)
        
        # 1. 메모리 통계 확인
        try:
            response = requests.get(f"{BASE_URL}/api/aura/memory/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ 메모리 통계: {stats}")
            else:
                print(f"❌ 메모리 통계 조회 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 메모리 통계 조회 오류: {e}")
        
        # 2. 회상 테스트
        test_queries = [
            "안녕하세요",
            "프로그래밍",
            "자동화",
            "AI",
            "테스트"
        ]
        
        for query in test_queries:
            try:
                response = requests.get(f"{BASE_URL}/api/aura/recall", params={
                    "query": query,
                    "recall_type": "normal"
                })
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 회상 결과 ({query}): {len(result.get('memories', []))}개 메모리")
                    for i, memory in enumerate(result.get('memories', [])[:2]):
                        print(f"   {i+1}. {memory.get('message', '')[:50]}...")
                else:
                    print(f"❌ 회상 실패 ({query}): {response.status_code}")
            except Exception as e:
                print(f"❌ 회상 오류 ({query}): {e}")
        
        print()
    
    def test_advanced_recall(self):
        """고급 회상 기능 테스트"""
        print("🚀 고급 회상 기능 테스트")
        print("=" * 50)
        
        # 다양한 회상 타입 테스트
        recall_types = ["normal", "semantic", "emotional", "contextual"]
        
        for recall_type in recall_types:
            try:
                response = requests.get(f"{BASE_URL}/api/aura/recall", params={
                    "query": "AI 시스템",
                    "recall_type": recall_type
                })
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {recall_type} 회상: {len(result.get('memories', []))}개 메모리")
                else:
                    print(f"❌ {recall_type} 회상 실패: {response.status_code}")
            except Exception as e:
                print(f"❌ {recall_type} 회상 오류: {e}")
        
        print()
    
    def test_chat_with_recall(self):
        """회상이 포함된 채팅 테스트"""
        print("💬 회상 포함 채팅 테스트")
        print("=" * 50)
        
        # 1. 먼저 몇 개의 메시지를 저장
        test_messages = [
            "안녕하세요! AI 시스템에 대해 궁금한 것이 있어요.",
            "프로그래밍 자동화에 대해 설명해주세요.",
            "메모리 시스템이 어떻게 작동하나요?",
            "고급 회상 기능을 테스트하고 싶어요."
        ]
        
        for i, message in enumerate(test_messages):
            try:
                response = requests.post(f"{BASE_URL}/api/chat", json={
                    "message": message,
                    "session_id": self.session_id,
                    "user_id": self.user_id,
                    "recall_type": "normal"
                })
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 메시지 {i+1} 전송: {result.get('response', '')[:100]}...")
                else:
                    print(f"❌ 메시지 {i+1} 전송 실패: {response.status_code}")
            except Exception as e:
                print(f"❌ 메시지 {i+1} 전송 오류: {e}")
        
        # 2. 회상이 포함된 질문
        recall_questions = [
            "앞서 말씀하신 AI 시스템에 대해 더 자세히 설명해주세요.",
            "프로그래밍 자동화와 관련해서 추가 질문이 있어요.",
            "메모리 시스템의 작동 원리를 다시 한번 설명해주세요."
        ]
        
        for i, question in enumerate(recall_questions):
            try:
                response = requests.post(f"{BASE_URL}/api/chat", json={
                    "message": question,
                    "session_id": self.session_id,
                    "user_id": self.user_id,
                    "recall_type": "contextual"
                })
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 회상 질문 {i+1}: {result.get('response', '')[:150]}...")
                else:
                    print(f"❌ 회상 질문 {i+1} 실패: {response.status_code}")
            except Exception as e:
                print(f"❌ 회상 질문 {i+1} 오류: {e}")
        
        print()
    
    def test_memory_list(self):
        """메모리 목록 조회 테스트"""
        print("📋 메모리 목록 조회 테스트")
        print("=" * 50)
        
        try:
            response = requests.get(f"{BASE_URL}/api/aura/memory")
            if response.status_code == 200:
                memories = response.json()
                print(f"✅ 메모리 목록: {len(memories.get('memories', []))}개")
                for i, memory in enumerate(memories.get('memories', [])[:5]):
                    print(f"   {i+1}. {memory.get('message', '')[:50]}...")
            else:
                print(f"❌ 메모리 목록 조회 실패: {response.status_code}")
        except Exception as e:
            print(f"❌ 메모리 목록 조회 오류: {e}")
        
        print()
    
    def test_prompt_integration(self):
        """프롬프트 통합 테스트"""
        print("🎯 프롬프트 통합 테스트")
        print("=" * 50)
        
        # 프롬프트가 제대로 적용되는지 테스트
        test_messages = [
            "당신은 누구인가요?",
            "EORA 시스템에 대해 설명해주세요.",
            "AI1의 역할은 무엇인가요?",
            "금강과 레조나에 대해 알려주세요."
        ]
        
        for i, message in enumerate(test_messages):
            try:
                response = requests.post(f"{BASE_URL}/api/chat", json={
                    "message": message,
                    "session_id": self.session_id,
                    "user_id": self.user_id,
                    "recall_type": "normal"
                })
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    print(f"✅ 프롬프트 테스트 {i+1}: {response_text[:200]}...")
                    
                    # EORA 관련 키워드 확인
                    eora_keywords = ['EORA', '이오라', '금강', '레조나', 'AI1', '자아']
                    found_keywords = [kw for kw in eora_keywords if kw in response_text]
                    if found_keywords:
                        print(f"   🎯 발견된 키워드: {found_keywords}")
                    else:
                        print(f"   ⚠️ EORA 키워드가 발견되지 않음")
                else:
                    print(f"❌ 프롬프트 테스트 {i+1} 실패: {response.status_code}")
            except Exception as e:
                print(f"❌ 프롬프트 테스트 {i+1} 오류: {e}")
        
        print()
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 EORA 고급 회상 시스템 종합 테스트")
        print("=" * 60)
        print(f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 서버 URL: {BASE_URL}")
        print(f"👤 테스트 사용자: {self.user_id}")
        print(f"💬 세션 ID: {self.session_id}")
        print("=" * 60)
        print()
        
        # 서버 상태 확인
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ 서버 상태: 정상")
            else:
                print(f"⚠️ 서버 상태: {response.status_code}")
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            return
        
        print()
        
        # 테스트 실행
        self.test_basic_recall()
        self.test_advanced_recall()
        self.test_chat_with_recall()
        self.test_memory_list()
        self.test_prompt_integration()
        
        print("🎉 모든 테스트 완료!")
        print("=" * 60)

def main():
    """메인 함수"""
    tester = RecallSystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 