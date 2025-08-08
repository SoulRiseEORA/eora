import os
from dotenv import load_dotenv

def load_openai_api_key():
    """OpenAI API 키를 환경 변수에서 로드"""
    try:
        # Railway 환경이 아닐 때만 .env 파일 로드
        if not os.getenv("RAILWAY_ENVIRONMENT"):
            load_dotenv()
        else:
            print("🚂 Railway 환경 감지 - .env 파일 로드 건너뜀 (환경변수 우선)")
        
        # 여러 가능한 환경변수 이름 시도
        possible_keys = [
            "OPENAI_API_KEY",
            "OPENAI_API_KEY_1", 
            "OPENAI_API_KEY_2",
            "OPENAI_API_KEY_3",
            "OPENAI_API_KEY_4",
            "OPENAI_API_KEY_5"
        ]
        
        for key_name in possible_keys:
            api_key = os.getenv(key_name)
            if api_key and api_key.startswith("sk-") and len(api_key) > 50:
                print(f"✅ OpenAI API 키 로드 완료: {key_name}")
                return api_key
        
        print("⚠️ OpenAI API 키를 찾을 수 없습니다. 서버는 제한된 기능으로 동작합니다.")
        return None
        
    except Exception as e:
        print(f"❌ OpenAI API 키 로드 실패: {str(e)}")
        return None 