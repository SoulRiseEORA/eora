#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI1 프롬프트 전달 종합 테스트 스크립트
"""

import sys
import os
import asyncio
import requests
import json
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))

def test_ai1_prompt_loading():
    """AI1 프롬프트 로드 테스트"""
    print("🔍 AI1 프롬프트 로드 테스트 시작...")
    
    try:
        # ai_prompts.json 파일 찾기
        possible_paths = [
            "ai_prompts.json",
            "ai_brain/ai_prompts.json", 
            "templates/ai_prompts.json",
            "prompts/ai_prompts.json",
            "src/ai_prompts.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"📁 파일 발견: {path}")
                
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        prompts_data = json.load(f)
                    
                    # AI1 프롬프트 구조 확인
                    if "ai1" in prompts_data:
                        ai1_data = prompts_data["ai1"]
                        print(f"✅ AI1 프롬프트 데이터 발견")
                        print(f"   - 데이터 타입: {type(ai1_data)}")
                        
                        if isinstance(ai1_data, dict):
                            print(f"   - 포함된 섹션: {list(ai1_data.keys())}")
                            
                            # 각 섹션별 내용 확인
                            for section in ["system", "role", "guide", "format"]:
                                if section in ai1_data:
                                    content = ai1_data[section]
                                    if isinstance(content, list):
                                        print(f"   - {section}: {len(content)}개 항목")
                                        for i, item in enumerate(content[:2]):  # 처음 2개만 표시
                                            preview = item[:100] + "..." if len(item) > 100 else item
                                            print(f"     [{i+1}] {preview}")
                                    elif isinstance(content, str):
                                        preview = content[:100] + "..." if len(content) > 100 else content
                                        print(f"   - {section}: {preview}")
                            
                            return True, ai1_data
                        else:
                            print(f"❌ AI1 데이터가 딕셔너리가 아님: {type(ai1_data)}")
                    else:
                        print(f"❌ AI1 키가 없음. 사용 가능한 키: {list(prompts_data.keys())}")
                        
                except Exception as e:
                    print(f"❌ 파일 로드 오류 ({path}): {e}")
                    continue
        
        print("❌ AI1 프롬프트 파일을 찾을 수 없습니다")
        return False, None
        
    except Exception as e:
        print(f"❌ 프롬프트 로드 테스트 실패: {e}")
        return False, None

def test_server_connection():
    """서버 연결 테스트"""
    print("\n🔗 서버 연결 테스트...")
    
    try:
        response = requests.get("http://127.0.0.1:8300/", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 연결 성공")
            return True
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

def login_and_test_chat():
    """로그인 후 채팅 테스트"""
    print("\n🔐 로그인 및 채팅 테스트...")
    
    session = requests.Session()
    
    try:
        # 로그인
        login_data = {
            "email": "admin@eora.ai",
            "password": "admin123"
        }
        
        login_response = session.post(
            "http://127.0.0.1:8300/api/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code != 200:
            print(f"❌ 로그인 실패: {login_response.status_code}")
            print(f"   응답: {login_response.text}")
            return False
        
        print("✅ 로그인 성공")
        
        # 세션 생성
        session_data = {
            "session_name": "AI1_프롬프트_테스트"
        }
        
        session_response = session.post(
            "http://127.0.0.1:8300/api/sessions",
            json=session_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if session_response.status_code != 200:
            print(f"❌ 세션 생성 실패: {session_response.status_code}")
            print(f"   응답: {session_response.text}")
            return False
        
        session_info = session_response.json()
        session_id = session_info.get("session_id")
        
        if not session_id:
            print(f"❌ 세션 ID 추출 실패: {session_info}")
            return False
        
        print(f"✅ 세션 생성 성공: {session_id}")
        
        # 채팅 테스트 - AI1 프롬프트 확인용 질문
        chat_data = {
            "message": "안녕하세요! 당신은 어떤 AI이며, 어떤 특별한 기능을 가지고 있나요? 8종 회상 시스템에 대해 설명해주세요.",
            "session_id": session_id
        }
        
        print(f"💬 채팅 요청 전송 중...")
        chat_response = session.post(
            "http://127.0.0.1:8300/api/chat",
            json=chat_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if chat_response.status_code != 200:
            print(f"❌ 채팅 요청 실패: {chat_response.status_code}")
            print(f"   응답: {chat_response.text}")
            return False
        
        chat_result = chat_response.json()
        ai_response = chat_result.get("response", "")
        
        print(f"✅ 채팅 응답 수신")
        print(f"📝 AI 응답 내용:")
        print(f"   길이: {len(ai_response)} 문자")
        print(f"   미리보기: {ai_response[:200]}...")
        
        # AI1 프롬프트 적용 여부 확인
        ai1_keywords = [
            "EORA", "8종 회상", "회상 시스템", "키워드 기반", "임베딩 기반", 
            "감정 기반", "신념 기반", "맥락 기반", "시간 기반", "연관 기반", 
            "패턴 기반", "통찰", "직관", "지혜"
        ]
        
        found_keywords = []
        for keyword in ai1_keywords:
            if keyword in ai_response:
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"✅ AI1 프롬프트 적용 확인됨 - 발견된 키워드: {found_keywords}")
            return True
        else:
            print(f"⚠️ AI1 프롬프트 적용 의심됨 - 관련 키워드 미발견")
            print(f"   전체 응답: {ai_response}")
            return False
        
    except Exception as e:
        print(f"❌ 로그인/채팅 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("🚀 AI1 프롬프트 전달 종합 테스트")
    print("=" * 60)
    
    # 1. 프롬프트 로드 테스트
    prompt_loaded, ai1_data = test_ai1_prompt_loading()
    
    # 2. 서버 연결 테스트
    server_connected = test_server_connection()
    
    # 3. 로그인 및 채팅 테스트
    chat_success = False
    if server_connected:
        chat_success = login_and_test_chat()
    
    # 4. 종합 결과
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약:")
    print(f"   🔍 프롬프트 로드: {'✅ 성공' if prompt_loaded else '❌ 실패'}")
    print(f"   🔗 서버 연결: {'✅ 성공' if server_connected else '❌ 실패'}")
    print(f"   💬 채팅 테스트: {'✅ 성공' if chat_success else '❌ 실패'}")
    
    if prompt_loaded and server_connected and chat_success:
        print("\n🎉 모든 테스트 통과! AI1 프롬프트가 정상적으로 API에 전달되고 있습니다.")
    else:
        print("\n⚠️ 일부 테스트 실패. 문제점을 확인해주세요.")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 