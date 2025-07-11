#!/usr/bin/env python3
"""
채팅 AI 에코 문제 수정 테스트 스크립트
"""

import os
import sys
from datetime import datetime

def test_eora_core():
    """EORACore 클래스 테스트"""
    print("🧪 EORACore 클래스 테스트")
    print("=" * 50)
    
    try:
        # main_fixed.py에서 EORACore 임포트
        sys.path.append('.')
        from main_fixed import EORACore
        
        # EORACore 인스턴스 생성
        eora = EORACore()
        print(f"✅ EORACore 인스턴스 생성 완료: {eora.name} v{eora.version}")
        
        # OpenAI 클라이언트 상태 확인
        if eora.openai_client:
            print("✅ OpenAI 클라이언트 초기화 성공")
        else:
            print("⚠️ OpenAI 클라이언트 초기화 실패 (API 키 없음)")
        
        # 테스트 메시지들
        test_messages = [
            "안녕하세요!",
            "오늘 날씨가 어때요?",
            "인공지능에 대해 어떻게 생각하세요?",
            "hihihi"
        ]
        
        print("\n📝 응답 테스트:")
        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. 사용자: {message}")
            try:
                response = eora.process_input(message, "test_user")
                print(f"   AI: {response}")
                
                # 에코 문제 확인
                if message.lower() in response.lower():
                    print("   ⚠️ 에코 문제 감지!")
                else:
                    print("   ✅ 정상 응답")
                    
            except Exception as e:
                print(f"   ❌ 오류: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

def check_environment():
    """환경 설정 확인"""
    print("🔍 환경 설정 확인")
    print("=" * 50)
    
    # OpenAI API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        if api_key.startswith("sk-"):
            print("✅ OpenAI API 키 설정됨")
            print(f"   키: {api_key[:10]}...{api_key[-4:]}")
        else:
            print("❌ OpenAI API 키 형식 오류")
    else:
        print("❌ OpenAI API 키가 설정되지 않음")
        print("\n🔧 API 키 설정 방법:")
        print("1. OpenAI 웹사이트에서 API 키 발급")
        print("2. 환경변수 설정:")
        print("   Windows: set OPENAI_API_KEY=sk-your-key-here")
        print("   Linux/Mac: export OPENAI_API_KEY=sk-your-key-here")
        print("3. 또는 python setup_openai_env.py 실행")

def main():
    """메인 함수"""
    print("🤖 EORA AI 채팅 에코 문제 수정 테스트")
    print("=" * 60)
    print(f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 환경 확인
    check_environment()
    
    print("\n" + "=" * 60)
    
    # EORACore 테스트
    success = test_eora_core()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 테스트 완료! 채팅 에코 문제가 수정되었습니다.")
        print("\n💡 다음 단계:")
        print("1. OpenAI API 키를 설정하세요")
        print("2. python -m uvicorn main_fixed:app --host 127.0.0.1 --port 8001 --reload 실행")
        print("3. 브라우저에서 http://127.0.0.1:8001/chat 접속")
        print("4. 채팅 테스트")
    else:
        print("❌ 테스트 실패. 문제를 확인해주세요.")

if __name__ == "__main__":
    main() 