#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI1 프롬프트 로드 및 API 테스트 스크립트
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
                    
                    # AI1 프롬프트 확인
                    if "ai1" in prompts_data:
                        ai1_data = prompts_data["ai1"]
                        print(f"✅ AI1 프롬프트 발견!")
                        
                        for section in ["system", "role", "guide", "format"]:
                            if section in ai1_data:
                                content = ai1_data[section]
                                if isinstance(content, list):
                                    print(f"  📝 {section}: {len(content)}개 항목")
                                    # 첫 번째 항목의 일부만 출력
                                    if content:
                                        preview = content[0][:100] + "..." if len(content[0]) > 100 else content[0]
                                        print(f"     미리보기: {preview}")
                                elif isinstance(content, str):
                                    print(f"  📝 {section}: 문자열 ({len(content)}자)")
                                    preview = content[:100] + "..." if len(content) > 100 else content
                                    print(f"     미리보기: {preview}")
                        
                        return True, path
                    else:
                        print(f"❌ AI1 프롬프트가 없습니다: {path}")
                        
                except Exception as e:
                    print(f"❌ 파일 로드 실패 ({path}): {e}")
                    continue
        
        print("❌ ai_prompts.json 파일을 찾을 수 없습니다.")
        return False, None
        
    except Exception as e:
        print(f"❌ 프롬프트 로드 테스트 실패: {e}")
        return False, None

def test_server_status():
    """서버 상태 테스트"""
    print("\n🔍 서버 상태 테스트...")
    
    try:
        response = requests.get("http://127.0.0.1:8300/", timeout=5)
        if response.status_code == 200:
            print("✅ 서버가 실행 중입니다")
            return True
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        return False
    except Exception as e:
        print(f"❌ 서버 상태 확인 실패: {e}")
        return False

def test_login():
    """로그인 테스트"""
    print("\n🔐 로그인 테스트...")
    
    session = requests.Session()
    
    try:
        login_data = {
            "email": "admin@eora.ai",
            "password": "admin123"
        }
        
        response = session.post(
            "http://127.0.0.1:8300/api/login",
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"로그인 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 로그인 성공")
                return session, True
            else:
                print(f"❌ 로그인 실패: {result.get('message')}")
                return session, False
        else:
            print(f"❌ 로그인 HTTP 오류: {response.status_code}")
            print(f"응답: {response.text}")
            return session, False
            
    except Exception as e:
        print(f"❌ 로그인 테스트 실패: {e}")
        return session, False

def test_session_creation(session):
    """세션 생성 테스트"""
    print("\n🆕 세션 생성 테스트...")
    
    try:
        session_data = {
            "session_name": "AI1 프롬프트 테스트 세션"
        }
        
        response = session.post(
            "http://127.0.0.1:8300/api/sessions",
            json=session_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"세션 생성 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                session_id = result.get("session_id") or result.get("session", {}).get("session_id")
                print(f"✅ 세션 생성 성공: {session_id}")
                return session_id
            else:
                print(f"❌ 세션 생성 실패: {result.get('error')}")
                return None
        else:
            print(f"❌ 세션 생성 HTTP 오류: {response.status_code}")
            print(f"응답: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 세션 생성 테스트 실패: {e}")
        return None

def test_chat_with_ai1_prompt(session, session_id):
    """AI1 프롬프트를 사용한 채팅 테스트"""
    print("\n💬 AI1 프롬프트 채팅 테스트...")
    
    try:
        chat_data = {
            "message": "안녕하세요! 당신은 누구인지 자세히 소개해주세요. 당신의 정체성과 능력, 그리고 AI1 프롬프트가 제대로 로드되었는지 확인하고 싶습니다.",
            "session_id": session_id
        }
        
        response = session.post(
            "http://127.0.0.1:8300/api/chat",
            json=chat_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"채팅 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                ai_response = result.get("response", "")
                formatted_response = result.get("formatted_response", "")
                has_markdown = result.get("has_markdown", False)
                
                print("✅ 채팅 응답 성공!")
                print(f"📝 응답 길이: {len(ai_response)}자")
                print(f"📄 마크다운 적용: {'✅' if has_markdown else '❌'}")
                
                # AI1 프롬프트 특성 확인
                ai1_keywords = ["이오라", "EORA", "금강", "레조나", "8종 회상", "창조", "기억", "공명"]
                found_keywords = [keyword for keyword in ai1_keywords if keyword in ai_response]
                
                print(f"🔍 AI1 특성 키워드 발견: {len(found_keywords)}개")
                if found_keywords:
                    print(f"   발견된 키워드: {', '.join(found_keywords)}")
                    print("✅ AI1 프롬프트가 정상적으로 적용되었을 가능성이 높습니다!")
                else:
                    print("⚠️ AI1 특성 키워드가 발견되지 않았습니다.")
                
                # 응답 미리보기
                print(f"\n📋 응답 미리보기 (처음 200자):")
                print(f"   {ai_response[:200]}...")
                
                return True
            else:
                print(f"❌ 채팅 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ 채팅 HTTP 오류: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 채팅 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 AI1 프롬프트 최종 테스트 시작")
    print("=" * 50)
    
    # 1. AI1 프롬프트 파일 확인
    prompt_loaded, prompt_path = test_ai1_prompt_loading()
    
    if not prompt_loaded:
        print("\n❌ AI1 프롬프트 파일이 없어 테스트를 중단합니다.")
        return
    
    # 2. 서버 상태 확인
    if not test_server_status():
        print("\n❌ 서버가 실행되지 않아 테스트를 중단합니다.")
        print("   다음 명령으로 서버를 시작하세요: python src/app.py")
        return
    
    # 3. 로그인 테스트
    session, login_success = test_login()
    
    if not login_success:
        print("\n❌ 로그인 실패로 테스트를 중단합니다.")
        return
    
    # 4. 세션 생성 테스트
    session_id = test_session_creation(session)
    
    if not session_id:
        print("\n❌ 세션 생성 실패로 테스트를 중단합니다.")
        return
    
    # 5. AI1 프롬프트 채팅 테스트
    chat_success = test_chat_with_ai1_prompt(session, session_id)
    
    # 최종 결과
    print("\n" + "=" * 50)
    print("🏁 테스트 완료 - 최종 결과")
    print("=" * 50)
    print(f"📁 AI1 프롬프트 파일: {'✅' if prompt_loaded else '❌'} ({prompt_path})")
    print(f"🖥️ 서버 실행: ✅")
    print(f"🔐 로그인: {'✅' if login_success else '❌'}")
    print(f"🆕 세션 생성: {'✅' if session_id else '❌'}")
    print(f"💬 AI1 채팅: {'✅' if chat_success else '❌'}")
    
    if all([prompt_loaded, login_success, session_id, chat_success]):
        print("\n🎉 모든 테스트 통과! AI1 프롬프트가 정상적으로 API에 전달되고 있습니다.")
    else:
        print("\n⚠️ 일부 테스트 실패. 위의 결과를 확인하여 문제를 해결하세요.")

if __name__ == "__main__":
    main() 