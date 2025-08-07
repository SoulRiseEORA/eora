#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🚀 EORA AI 즉시 서버 시작...")

import http.server
import socketserver
import os
import webbrowser
from threading import Timer

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
        
        if self.path == "/admin" or self.path == "/":
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🚀 EORA AI - 즉시 서버</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .card {{ background: white; padding: 30px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .success {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .warning {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .btn {{ background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }}
        .btn:hover {{ background: #0056b3; }}
        h1 {{ color: #333; text-align: center; }}
        h2 {{ color: #007bff; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 EORA AI 즉시 서버</h1>
        
        <div class="card">
            <h2>📊 시스템 상태</h2>
            <div class="success">✅ HTTP 서버: 정상 작동</div>
            <div class="{'success' if api_key else 'warning'}">
                🔑 OpenAI API 키: {"설정됨" if api_key else "설정 필요"}
                {f"({api_key[:10]}...{api_key[-4:]})" if api_key else ""}
            </div>
        </div>
        
        <div class="card">
            <h2>🌐 접속 정보</h2>
            <div class="success">📍 현재 주소: http://127.0.0.1:8080</div>
            <div class="success">🔧 관리자 페이지: http://127.0.0.1:8080/admin</div>
        </div>
        
        <div class="card">
            <h2>🔧 다음 단계</h2>
            <p><strong>본격적인 서버 시작 방법:</strong></p>
            <ol>
                <li><code>cd src</code></li>
                <li><code>python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload</code></li>
            </ol>
            {'<div class="success">✅ API 키 설정 완료 - 재학습 가능</div>' if api_key else '<div class="warning">⚠️ OpenAI API 키 설정 필요</div>'}
        </div>
        
        <div class="card">
            <h2>🛠️ 문제 해결</h2>
            <p>본격적인 서버가 시작되지 않는 경우:</p>
            <ul>
                <li>PowerShell에서 <code>&&</code> 대신 <code>;</code> 사용</li>
                <li>포트 충돌 시 <code>taskkill /F /IM python.exe</code></li>
                <li>직접 실행: <code>cd src; python app.py</code></li>
            </ul>
        </div>
        
        <div class="card">
            <h2>📱 빠른 액션</h2>
            <a href="javascript:alert('서버 정상 작동 중!')" class="btn">상태 확인</a>
            <a href="javascript:window.location.reload()" class="btn">새로고침</a>
        </div>
    </div>
    
    <script>
        console.log("🚀 EORA AI 즉시 서버 로드 완료");
    </script>
</body>
</html>
"""
        else:
            html = "<h1>404 - 페이지를 찾을 수 없습니다</h1><p><a href='/'>홈으로 돌아가기</a></p>"
        
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # 로그 출력 억제

def open_browser():
    webbrowser.open('http://127.0.0.1:8080')

if __name__ == "__main__":
    PORT = 8080
    
    print("=" * 50)
    print(f"📍 접속 주소: http://127.0.0.1:{PORT}")
    print(f"🔧 관리자 페이지: http://127.0.0.1:{PORT}/admin")
    
    if api_key:
        print(f"✅ API 키: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ API 키: 설정되지 않음")
    
    print("=" * 50)
    print("🌐 3초 후 브라우저가 자동으로 열립니다...")
    
    # 3초 후 브라우저 자동 열기
    Timer(3.0, open_browser).start()
    
    try:
        with socketserver.TCPServer(("127.0.0.1", PORT), MyHandler) as httpd:
            print("✅ 서버 시작 완료!")
            print("🛑 종료하려면 Ctrl+C를 누르세요")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 서버 종료")
    except Exception as e:
        print(f"❌ 서버 오류: {e}")
        print("💡 다른 포트를 시도하거나 관리자 권한으로 실행해보세요") 