#!/usr/bin/env python3
"""
Railway 환경변수 확인 스크립트
Railway 배포 환경에서 환경변수가 제대로 설정되었는지 확인
"""

import os
import sys

def check_railway_environment():
    """Railway 환경변수 상태 확인"""
    print("🔍 Railway 환경변수 상태 확인")
    print("=" * 50)
    
    # Railway 관련 환경변수들
    railway_vars = [
        "OPENAI_API_KEY",
        "MONGO_PUBLIC_URL", 
        "MONGO_URL",
        "MONGO_INITDB_ROOT_PASSWORD",
        "MONGO_INITDB_ROOT_USERNAME",
        "RAILWAY_TCP_PROXY_DOMAIN",
        "RAILWAY_TCP_PROXY_PORT",
        "RAILWAY_PRIVATE_DOMAIN"
    ]
    
    print("📋 환경변수 목록:")
    for var in railway_vars:
        value = os.getenv(var)
        if value:
            # 민감한 정보는 일부만 표시
            if "API_KEY" in var or "PASSWORD" in var:
                display_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
            else:
                display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: 설정되지 않음")
    
    print("\n" + "=" * 50)
    
    # OpenAI API 키 특별 확인
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        if openai_key.startswith("sk-"):
            print("✅ OpenAI API 키가 올바르게 설정되어 있습니다!")
            return True
        else:
            print("❌ OpenAI API 키 형식이 올바르지 않습니다. 'sk-'로 시작해야 합니다.")
            return False
    else:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        print("🔧 Railway 대시보드 > Service > Variables에서 설정해주세요.")
        return False

def test_openai_connection():
    """OpenAI 연결 테스트"""
    print("\n🧪 OpenAI 연결 테스트")
    print("=" * 30)
    
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
    print("🚀 Railway 환경변수 확인 도구")
    print("=" * 60)
    
    # 환경변수 확인
    env_ok = check_railway_environment()
    
    if env_ok:
        print("\n✅ 환경변수가 올바르게 설정되어 있습니다!")
        
        # OpenAI 연결 테스트
        test_choice = input("\nOpenAI 연결 테스트를 실행하시겠습니까? (y/n): ").lower()
        if test_choice == 'y':
            test_openai_connection()
    else:
        print("\n❌ 환경변수 설정에 문제가 있습니다.")
        print("\n🔧 해결 방법:")
        print("1. Railway 대시보드에 로그인")
        print("2. 해당 프로젝트 선택")
        print("3. Service 탭 클릭")
        print("4. Variables 탭 클릭")
        print("5. OPENAI_API_KEY 추가/수정")
        print("6. 서비스 재배포")

if __name__ == "__main__":
    main() 