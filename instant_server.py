#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 1. .env 파일 내용 직접 로드
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

# 2. MongoDB 연결 테스트 함수
def test_mongodb():
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
        db = client["eora_ai"]
        memories = db["memories"]
        total = memories.count_documents({})
        learning = memories.count_documents({"memory_type": "learning_material"})
        client.close()
        return {"total": total, "learning": learning, "status": "connected"}
    except Exception as e:
        return {"total": 0, "learning": 0, "status": f"error: {e}"}

# 3. HTTP 서버 생성
import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "EORA AI System is running",
                "status": "healthy",
                "api_key": "configured" if os.getenv("OPENAI_API_KEY") else "missing"
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        elif path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "api_key": os.getenv("OPENAI_API_KEY", "")[:10] + "..." if os.getenv("OPENAI_API_KEY") else "missing"
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        elif path == "/memory":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            mongo_result = test_mongodb()
            response = {
                "success": True,
                "stats": mongo_result
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        elif path == "/admin":
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            mongo_result = test_mongodb()
            api_key = os.getenv("OPENAI_API_KEY", "")
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>EORA AI - 관리자</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .card {{ background: white; padding: 30px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .success {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .warning {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .error {{ background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        h1 {{ color: #333; text-align: center; }}
        h2 {{ color: #007bff; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 EORA AI 시스템 상태</h1>
        
        <div class="card">
            <h2>📊 현재 상태</h2>
            <div class="success">✅ HTTP 서버: 정상 작동</div>
            <div class="{'success' if api_key else 'error'}">
                🔑 OpenAI API 키: {"설정됨" if api_key else "설정되지 않음"}
                {f"({api_key[:10]}...{api_key[-4:]})" if api_key else ""}
            </div>
        </div>
        
        <div class="card">
            <h2>💾 MongoDB 상태</h2>
            <div class="{'success' if mongo_result['status'] == 'connected' else 'error'}">
                📊 연결 상태: {mongo_result['status']}
            </div>
            {f'<div class="success">📚 총 메모리: {mongo_result["total"]:,}개</div>' if mongo_result['status'] == 'connected' else ''}
            {f'<div class="success">📖 학습 자료: {mongo_result["learning"]:,}개</div>' if mongo_result['status'] == 'connected' else ''}
        </div>
        
        <div class="card">
            <h2>🔧 다음 단계</h2>
            {'<div class="success">✅ API 키 설정 완료 - 재학습 가능</div>' if api_key else '<div class="error">❌ OpenAI API 키 설정 필요</div>'}
            {'<div class="success">✅ MongoDB 연결 완료 - 데이터 저장 가능</div>' if mongo_result['status'] == 'connected' else '<div class="error">❌ MongoDB 연결 필요</div>'}
            
            {f'<div class="warning">⚠️ 학습된 데이터: {mongo_result["learning"]}개 - 재학습 권장</div>' if mongo_result.get('learning', 0) == 0 else f'<div class="success">✅ 학습 완료: {mongo_result["learning"]}개 저장됨</div>'}
        </div>
        
        <div class="card">
            <h2>📝 사용 안내</h2>
            <p><strong>현재 상황:</strong> 간단한 HTTP 서버가 실행 중입니다.</p>
            <p><strong>API 키 문제:</strong> {"해결됨" if api_key else "fix_api_key.py 실행 필요"}</p>
            <p><strong>재학습 방법:</strong> API 키 문제 해결 후 원본 서버로 금강2.docx 재학습</p>
        </div>
    </div>
</body>
</html>
"""
            self.wfile.write(html.encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        pass  # 로그 출력 안함

if __name__ == "__main__":
    print("🚀 EORA AI 즉시 서버 시작 중...")
    print("📍 접속 주소: http://127.0.0.1:8003")
    print("🔧 관리자 페이지: http://127.0.0.1:8003/admin")
    print("=" * 50)
    
    # API 키 상태 미리 확인
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        print(f"✅ API 키: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ API 키: 설정되지 않음")
    
    # MongoDB 상태 미리 확인
    mongo_result = test_mongodb()
    print(f"📊 MongoDB: {mongo_result['status']}")
    if mongo_result['status'] == 'connected':
        print(f"💾 총 메모리: {mongo_result['total']:,}개")
        print(f"📚 학습 자료: {mongo_result['learning']:,}개")
    
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("127.0.0.1", 8003), MyHandler) as httpd:
            print("✅ 서버 시작 완료!")
            print("🌐 브라우저에서 http://127.0.0.1:8003/admin 접속하세요")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 서버 종료")
    except Exception as e:
        print(f"❌ 서버 오류: {e}") 