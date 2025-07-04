#!/usr/bin/env python3
"""
OpenAI API 키 환경변수 설정 도우미
Railway 환경변수 설정을 위한 가이드 스크립트
"""

import os
import sys

def check_openai_api_key():
    """현재 OpenAI API 키 상태 확인"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    print("🔍 OpenAI API 키 상태 확인")
    print("=" * 50)
    
    if not api_key:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        return False
    
    if api_key == "your-openai-api-key-here":
        print("❌ 기본값이 설정되어 있습니다. 실제 API 키를 설정해주세요.")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ API 키 형식이 올바르지 않습니다. 'sk-'로 시작해야 합니다.")
        return False
    
    print("✅ OpenAI API 키가 올바르게 설정되어 있습니다.")
    print(f"📝 API 키: {api_key[:10]}...{api_key[-4:]}")
    return True

def setup_railway_instructions():
    """Railway 환경변수 설정 가이드"""
    print("\n🚀 Railway 환경변수 설정 가이드")
    print("=" * 50)
    print("1. Railway 대시보드에 로그인")
    print("2. 해당 프로젝트 선택")
    print("3. Service 탭 클릭")
    print("4. Variables 탭 클릭")
    print("5. 'New Variable' 버튼 클릭")
    print("6. 다음 정보 입력:")
    print("   - Key: OPENAI_API_KEY")
    print("   - Value: sk-your-actual-api-key-here")
    print("7. 'Add' 버튼 클릭")
    print("8. 서비스 재배포 (자동 또는 수동)")
    print("\n💡 팁: API 키는 'sk-'로 시작하는 긴 문자열입니다.")

def setup_local_env():
    """로컬 환경변수 설정 (개발용)"""
    print("\n💻 로컬 환경변수 설정 (개발용)")
    print("=" * 50)
    
    api_key = input("OpenAI API 키를 입력하세요 (sk-로 시작): ").strip()
    
    if not api_key:
        print("❌ API 키를 입력하지 않았습니다.")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ API 키 형식이 올바르지 않습니다.")
        return False
    
    # Windows PowerShell용 명령어
    print("\n🔧 Windows PowerShell에서 실행할 명령어:")
    print(f'$env:OPENAI_API_KEY = "{api_key}"')
    print("python final_server.py")
    
    # Windows CMD용 명령어
    print("\n🔧 Windows CMD에서 실행할 명령어:")
    print(f'set OPENAI_API_KEY={api_key}')
    print("python final_server.py")
    
    # Linux/Mac용 명령어
    print("\n🔧 Linux/Mac에서 실행할 명령어:")
    print(f'export OPENAI_API_KEY="{api_key}"')
    print("python final_server.py")
    
    return True

def test_openai_connection():
    """OpenAI 연결 테스트"""
    print("\n🧪 OpenAI 연결 테스트")
    print("=" * 50)
    
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ API 키가 설정되지 않았습니다.")
            return False
        
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        
        # 간단한 테스트 요청
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API 연결 성공!")
        print(f"📝 테스트 응답: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API 연결 실패: {str(e)}")
        return False

def main():
    """메인 함수"""
    print("🤖 EORA AI - OpenAI API 키 설정 도우미")
    print("=" * 60)
    
    # 현재 상태 확인
    current_status = check_openai_api_key()
    
    if current_status:
        print("\n✅ API 키가 이미 설정되어 있습니다!")
        test_choice = input("연결 테스트를 실행하시겠습니까? (y/n): ").lower()
        if test_choice == 'y':
            test_openai_connection()
    else:
        print("\n🔧 API 키 설정이 필요합니다.")
        print("\n선택하세요:")
        print("1. Railway 환경변수 설정 가이드 보기")
        print("2. 로컬 환경변수 설정 (개발용)")
        print("3. 연결 테스트")
        print("4. 종료")
        
        choice = input("\n선택 (1-4): ").strip()
        
        if choice == "1":
            setup_railway_instructions()
        elif choice == "2":
            setup_local_env()
        elif choice == "3":
            test_openai_connection()
        elif choice == "4":
            print("👋 종료합니다.")
        else:
            print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main() 