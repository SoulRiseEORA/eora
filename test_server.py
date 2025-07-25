#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import os

def main():
    # 환경변수 로드
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

    api_key = os.getenv("OPENAI_API_KEY", "")
    
    class MyHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>EORA AI - 테스트 서버</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>🚀 EORA AI 테스트 서버</h1>
    <p><strong>상태:</strong> 정상 작동</p>
    <p><strong>API 키:</strong> {"설정됨" if api_key else "설정되지 않음"}</p>
    <p><strong>접속 주소:</strong> http://127.0.0.1:8000</p>
    <hr>
    <p>본격적인 서버 시작: <code>cd src && python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload</code></p>
</body>
</html>
"""
            self.wfile.write(html.encode('utf-8'))
    
    print("🚀 EORA AI 테스트 서버 시작")
    print("📍 접속 주소: http://127.0.0.1:8000")
    print("=" * 50)
    
    if api_key:
        print(f"✅ API 키: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ API 키: 설정되지 않음")
    
    try:
        with socketserver.TCPServer(("127.0.0.1", 8000), MyHandler) as httpd:
            print("✅ 서버 시작 완료!")
            print("🌐 브라우저에서 http://127.0.0.1:8000 접속하세요")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 서버 종료")
    except Exception as e:
        print(f"❌ 서버 오류: {e}")

if __name__ == "__main__":
    main() 