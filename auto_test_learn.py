import requests

learn_url = "http://127.0.0.1:8002/learn"
chat_url = "http://127.0.0.1:8002/chat"
points_url = "http://127.0.0.1:8002/user/points"

def test_learn():
    data = {
        "text": "이것은 MongoDB 연결 자동화 학습 테스트 문장입니다.",
        "user_id": "test_user"
    }
    try:
        response = requests.post(learn_url, json=data, timeout=10)
        print("[학습하기 응답 코드]", response.status_code)
        print("[학습하기 응답 본문]", response.text)
        if response.status_code == 200 and 'memory_id' in response.text:
            print("✅ 학습하기 API(MongoDB) 자동화 테스트 성공!")
        else:
            print("❌ 학습하기 API(MongoDB) 자동화 테스트 실패!")
    except Exception as e:
        print(f"❌ 요청/연결 오류: {e}")

def test_chat():
    data = {
        "message": "테스트 대화 메시지입니다.",
        "user_id": "test_user"
    }
    try:
        response = requests.post(chat_url, json=data, timeout=10)
        print("[대화 API 응답 코드]", response.status_code)
        print("[대화 API 응답 본문]", response.text)
        if response.status_code == 200 and '대화 저장 완료' in response.text:
            print("✅ 대화 API(user_id별) 자동화 테스트 성공!")
        else:
            print("❌ 대화 API(user_id별) 자동화 테스트 실패!")
    except Exception as e:
        print(f"❌ 대화 API 요청/연결 오류: {e}")

def test_points():
    params = {"user_id": "test_user"}
    try:
        response = requests.get(points_url, params=params, timeout=10)
        print("[포인트 API 응답 코드]", response.status_code)
        print("[포인트 API 응답 본문]", response.text)
        if response.status_code == 200 and 'points' in response.text:
            print("✅ 포인트 API(user_id별) 자동화 테스트 성공!")
        else:
            print("❌ 포인트 API(user_id별) 자동화 테스트 실패!")
    except Exception as e:
        print(f"❌ 포인트 API 요청/연결 오류: {e}")

if __name__ == "__main__":
    test_learn()
    test_chat()
    test_points() 