import os
from dotenv import load_dotenv

def load_openai_api_key():
    """OpenAI API 키를 환경 변수에서 로드"""
    try:
        # .env 파일 로드
        load_dotenv()
        
        # API 키 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
            
        print("✅ OpenAI API 키 로드 완료")
        return api_key
        
    except Exception as e:
        print(f"❌ OpenAI API 키 로드 실패: {str(e)}")
        raise 