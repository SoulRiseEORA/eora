#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI1 프롬프트 전달 테스트 스크립트
ai_prompts.json의 ai1 프롬프트가 API에 정상적으로 전달되는지 확인
"""

import asyncio
import json
import os
import sys
import requests
import time
from pathlib import Path

# 프로젝트 루트 설정
project_root = Path(__file__).parent
sys.path.append(str(project_root / "src"))

def test_ai_prompts_file():
    """ai_prompts.json 파일 확인 및 ai1 프롬프트 내용 검증"""
    print("\n=== AI 프롬프트 파일 검증 ===")
    
    # ai_prompts.json 파일 찾기
    possible_paths = [
        "ai_prompts.json",
        "src/ai_prompts.json", 
        "src/templates/ai_prompts.json",
        "src/ai_brain/ai_prompts.json"
    ]
    
    ai_prompts_file = None
    for path in possible_paths:
        if os.path.exists(path):
            ai_prompts_file = path
            print(f"✅ AI 프롬프트 파일 발견: {path}")
            break
    
    if not ai_prompts_file:
        print("❌ ai_prompts.json 파일을 찾을 수 없습니다")
        return False
    
    # 파일 내용 로드
    try:
        with open(ai_prompts_file, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)
        
        print(f"📄 파일 크기: {os.path.getsize(ai_prompts_file)} bytes")
        print(f"📋 전체 AI 수: {len(prompts_data)}")
        print(f"📝 AI 목록: {list(prompts_data.keys())}")
        
        # ai1 프롬프트 확인
        if "ai1" in prompts_data:
            ai1_data = prompts_data["ai1"]
            print(f"\n🎯 AI1 프롬프트 구조:")
            print(f"   📂 카테고리 수: {len(ai1_data)}")
            print(f"   📂 카테고리 목록: {list(ai1_data.keys())}")
            
            # 각 카테고리별 크기 확인
            for category, content in ai1_data.items():
                if isinstance(content, list):
                    total_chars = sum(len(str(item)) for item in content)
                    print(f"   📝 {category}: {len(content)}개 항목, {total_chars}자")
                else:
                    print(f"   📝 {category}: {len(str(content))}자")
            
            # system 프롬프트 샘플 출력
            if "system" in ai1_data:
                system_content = ai1_data["system"]
                if isinstance(system_content, list):
                    system_text = "\n".join(system_content)
                else:
                    system_text = str(system_content)
                print(f"\n📖 System 프롬프트 미리보기 (처음 200자):")
                print(f"   {system_text[:200]}...")
            
            return True
        else:
            print("❌ ai1 프롬프트가 파일에 없습니다")
            return False
            
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        return False

def test_server_status():
    """서버 상태 확인"""
    print("\n=== 서버 상태 확인 ===")
    base_url = "http://127.0.0.1:8300"
    
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 실행 중")
            return True
        else:
            print(f"⚠️ 서버 응답 상태: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 서버 연결 실패: {e}")
        print("💡 서버를 먼저 실행해주세요: python app.py")
        return False

def test_openai_service_prompt_loading():
    """OpenAI 서비스의 프롬프트 로딩 테스트"""
    print("\n=== OpenAI 서비스 프롬프트 로딩 테스트 ===")
    
    try:
        # services.openai_service 모듈 테스트
        from services.openai_service import load_prompts_data, prompts_data
        
        print("🔄 프롬프트 데이터 로드 중...")
        result = asyncio.run(load_prompts_data())
        
        if result:
            print("✅ 프롬프트 데이터 로드 성공")
            
            if prompts_data and "prompts" in prompts_data:
                ai_list = list(prompts_data["prompts"].keys())
                print(f"📋 로드된 AI: {ai_list}")
                
                if "ai1" in prompts_data["prompts"]:
                    ai1_data = prompts_data["prompts"]["ai1"]
                    print(f"✅ ai1 프롬프트 확인: {len(ai1_data)}개 카테고리")
                    print(f"📂 ai1 카테고리: {list(ai1_data.keys())}")
                    return True
                else:
                    print("❌ ai1 프롬프트가 로드되지 않음")
                    return False
            else:
                print("❌ 프롬프트 데이터 구조 이상")
                return False
        else:
            print("❌ 프롬프트 데이터 로드 실패")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI 서비스 테스트 실패: {e}")
        return False

def test_ai1_prompt_function():
    """get_ai1_system_prompt 함수 테스트"""
    print("\n=== AI1 프롬프트 함수 테스트 ===")
    
    try:
        # app.py의 get_ai1_system_prompt 함수 테스트
        sys.path.append('src')
        from app import get_ai1_system_prompt
        
        print("🔄 ai1 시스템 프롬프트 로드 중...")
        prompt = asyncio.run(get_ai1_system_prompt())
        
        if prompt:
            print(f"✅ ai1 프롬프트 로드 성공: {len(prompt)}자")
            
            # 프롬프트 내용 분석
            sections = prompt.split("===")
            print(f"📂 프롬프트 섹션 수: {len(sections)}")
            
            # 각 섹션 확인
            for i, section in enumerate(sections):
                if section.strip():
                    lines = section.strip().split('\n')
                    if lines:
                        section_title = lines[0].strip()
                        print(f"   📝 섹션 {i}: {section_title} ({len(section)}자)")
            
            # 프롬프트 미리보기
            print(f"\n📖 AI1 프롬프트 미리보기 (처음 300자):")
            print(f"   {prompt[:300]}...")
            
            return True
        else:
            print("❌ ai1 프롬프트가 비어있음")
            return False
            
    except Exception as e:
        print(f"❌ AI1 프롬프트 함수 테스트 실패: {e}")
        import traceback
        print(f"상세 오류: {traceback.format_exc()}")
        return False

def test_chat_api_with_prompt():
    """채팅 API를 통한 프롬프트 전달 테스트"""
    print("\n=== 채팅 API 프롬프트 전달 테스트 ===")
    base_url = "http://127.0.0.1:8300"
    
    try:
        # 테스트 메시지 전송
        test_message = "안녕하세요! AI1 프롬프트가 정상적으로 전달되었는지 확인하기 위한 테스트입니다. 당신은 누구인가요?"
        
        chat_data = {
            "message": test_message,
            "user_id": "test_user",
            "session_id": "test_session"
        }
        
        print("🔄 채팅 API 호출 중...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/api/chat",
            json=chat_data,
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ 채팅 API 응답 성공 ({response_time:.2f}초)")
            print(f"📄 응답 길이: {len(result.get('response', ''))}자")
            
            ai_response = result.get('response', '')
            if ai_response:
                print(f"\n🤖 AI 응답 미리보기:")
                print(f"   {ai_response[:200]}...")
                
                # ai1 특징적인 키워드 확인
                ai1_keywords = [
                    "이오라", "EORA", "금강", "레조나", 
                    "8종 회상", "직관", "통찰", "지혜",
                    "윤종석", "창조", "생성", "기억"
                ]
                
                found_keywords = [kw for kw in ai1_keywords if kw in ai_response]
                if found_keywords:
                    print(f"✅ AI1 특징적 키워드 발견: {found_keywords}")
                    print("✅ AI1 프롬프트가 정상적으로 전달된 것으로 보입니다!")
                    return True
                else:
                    print("⚠️ AI1 특징적 키워드가 응답에서 발견되지 않음")
                    print("⚠️ 기본 프롬프트가 사용되었을 가능성")
                    return False
            else:
                print("❌ AI 응답이 비어있음")
                return False
        else:
            print(f"❌ 채팅 API 오류: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 채팅 API 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🧪 AI1 프롬프트 전달 테스트 시작")
    print("=" * 50)
    
    # 테스트 단계별 실행
    tests = [
        ("AI 프롬프트 파일 검증", test_ai_prompts_file),
        ("서버 상태 확인", test_server_status),
        ("OpenAI 서비스 프롬프트 로딩", test_openai_service_prompt_loading),
        ("AI1 프롬프트 함수", test_ai1_prompt_function),
        ("채팅 API 프롬프트 전달", test_chat_api_with_prompt)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name}: 통과")
                passed += 1
            else:
                print(f"❌ {test_name}: 실패")
        except Exception as e:
            print(f"❌ {test_name}: 예외 발생 - {e}")
    
    # 최종 결과
    print(f"\n{'='*50}")
    print(f"🧪 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! AI1 프롬프트가 정상적으로 전달됩니다.")
        return True
    else:
        print("⚠️ 일부 테스트 실패. 문제를 확인해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 