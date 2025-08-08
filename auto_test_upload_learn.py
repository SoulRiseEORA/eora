import requests

url = "http://127.0.0.1:8002/upload-learn"
file_path = "test_upload.txt"

def make_test_file():
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("테스트 파일입니다. 첨부학습 자동화 테스트.")

def test_upload_learn():
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "text/plain")}
        data = {"description": "자동화 테스트"}
        response = requests.post(url, files=files, data=data)
        print("[응답 코드]", response.status_code)
        print("[응답 본문]", response.text)
        if response.status_code == 200 and 'ok' in response.text:
            print("✅ 첨부학습 API 자동화 테스트 성공!")
        else:
            print("❌ 첨부학습 API 자동화 테스트 실패!")

if __name__ == "__main__":
    make_test_file()
    test_upload_learn() 