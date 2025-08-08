import requests
import json

def test_chat_api():
    """채팅 API 테스트"""
    url = "http://localhost:8011/api/chat"
    headers = {
        "Content-Type": "application/json"
    }
    
    # 테스트 메시지들
    test_messages = [
        "안녕하세요",
        "오늘 날씨는 어때요?",
        "EORA AI에 대해 알려주세요",
        "/help"
    ]
    
    for message in test_messages:
        try:
            data = {
                "message": message,
                "session_id": "test_session"
            }
            
            print(f"📤 전송: {message}")
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 응답: {result.get('response', '응답 없음')}")
                print(f"📊 세션 ID: {result.get('session_id', 'N/A')}")
                print(f"👤 사용자 ID: {result.get('user_id', 'N/A')}")
                print(f"⏰ 타임스탬프: {result.get('timestamp', 'N/A')}")
            else:
                print(f"❌ 오류: {response.status_code}")
                print(f"📝 오류 내용: {response.text}")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ 요청 실패: {e}")
            print("-" * 50)

if __name__ == "__main__":
    print("🚀 EORA AI 채팅 API 테스트 시작")
    print("=" * 50)
    test_chat_api()
    print("✅ 테스트 완료") 