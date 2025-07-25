#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
프롬프트 관리 시스템 수정사항 테스트 스크립트
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_prompts_api():
    """프롬프트 API 테스트"""
    print("\n=== 프롬프트 API 테스트 ===")
    
    try:
        # 1. 프롬프트 조회
        response = requests.get(f"{BASE_URL}/api/prompts")
        if response.status_code == 200:
            data = response.json()
            prompts = data.get("prompts", {})
            print(f"✅ 프롬프트 조회 성공: {len(prompts)}개 AI 발견")
            
            # ai1의 프롬프트 구조 확인
            if "ai1" in prompts:
                ai1_data = prompts["ai1"]
                print(f"\n📋 AI1 프롬프트 구조:")
                for category in ["system", "role", "guide", "format"]:
                    if category in ai1_data:
                        items = ai1_data[category]
                        if isinstance(items, list):
                            print(f"  - {category}: 리스트 ({len(items)}개 항목)")
                            if items and len(str(items[0])) > 50:
                                print(f"    첫 번째 항목 미리보기: {str(items[0])[:50]}...")
                        else:
                            print(f"  - {category}: {type(items).__name__}")
            else:
                print("⚠️ AI1 프롬프트를 찾을 수 없습니다")
        else:
            print(f"❌ 프롬프트 조회 실패: {response.status_code}")
            
    except requests.ConnectionError:
        print("❌ 서버 연결 실패. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def test_chat_with_ai1():
    """AI1을 사용한 채팅 테스트"""
    print("\n=== AI1 채팅 테스트 ===")
    
    try:
        # 세션 ID 생성 (실제로는 쿠키에서 가져와야 함)
        import uuid
        session_id = str(uuid.uuid4())
        
        # 채팅 요청
        chat_data = {
            "message": "안녕하세요! 당신은 누구인가요?",
            "session_id": session_id
        }
        
        # AI1 선택하여 요청
        response = requests.post(
            f"{BASE_URL}/api/chat?ai=ai1",
            json=chat_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                print("✅ AI1 응답 성공:")
                print(f"   {data['response'][:100]}..." if len(data['response']) > 100 else f"   {data['response']}")
            else:
                print(f"⚠️ 응답에 오류가 있습니다: {data}")
        else:
            print(f"❌ 채팅 요청 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def test_prompt_management_page():
    """프롬프트 관리 페이지 접근 테스트"""
    print("\n=== 프롬프트 관리 페이지 테스트 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/prompt_management")
        if response.status_code == 200:
            print("✅ 프롬프트 관리 페이지 접근 성공")
            # HTML에서 ai1 관련 코드 확인
            if "ai1" in response.text and "ai1_system_0" in response.text:
                print("✅ AI1 특별 처리 코드 확인됨")
            else:
                print("⚠️ AI1 특별 처리 코드를 찾을 수 없습니다")
        else:
            print(f"❌ 페이지 접근 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def test_ai_prompts_file():
    """ai_prompts.json 파일 직접 확인"""
    print("\n=== ai_prompts.json 파일 확인 ===")
    
    try:
        with open("src/ai_prompts.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if "ai1" in data:
            ai1_data = data["ai1"]
            print("✅ AI1 데이터 발견")
            
            # system 필드 확인
            if "system" in ai1_data:
                system_data = ai1_data["system"]
                print(f"📋 AI1 system 필드 타입: {type(system_data).__name__}")
                if isinstance(system_data, list):
                    print(f"   - 리스트 항목 수: {len(system_data)}")
                    print(f"   - 전체 길이: {sum(len(s) for s in system_data)} 문자")
                else:
                    print(f"   - 문자열 길이: {len(system_data)} 문자")
        else:
            print("⚠️ AI1 데이터를 찾을 수 없습니다")
            
    except FileNotFoundError:
        print("❌ ai_prompts.json 파일을 찾을 수 없습니다")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    print("🔧 프롬프트 관리 시스템 테스트 시작")
    print(f"📍 테스트 서버: {BASE_URL}")
    print("=" * 50)
    
    # 파일 직접 확인
    test_ai_prompts_file()
    
    # API 테스트
    test_prompts_api()
    
    # 페이지 테스트
    test_prompt_management_page()
    
    # 채팅 테스트 (OpenAI API 키가 필요함)
    # test_chat_with_ai1()
    
    print("\n✅ 테스트 완료!") 