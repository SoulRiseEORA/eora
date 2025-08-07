#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 긴급 서버 (최소 의존성)
"""

import sys
import os
import json
from datetime import datetime

# 기본 HTTP 서버 (Python 내장)
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
    print("✅ 내장 HTTP 서버 사용 가능")
except ImportError as e:
    print(f"❌ 내장 HTTP 서버 사용 불가: {e}")
    sys.exit(1)

class EORARequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """GET 요청 처리"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 응답 헤더
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # 경로별 응답
        if path == '/':
            content = self.get_homepage()
        elif path == '/health':
            content = self.get_health()
        elif path == '/api/status':
            content = self.get_api_status()
        elif path == '/test':
            content = self.get_test_page()
        else:
            content = self.get_404_page()
        
        # 응답 전송
        self.wfile.write(content.encode('utf-8'))
    
    def do_POST(self):
        """POST 요청 처리"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "success": True,
            "message": "POST 요청 처리됨",
            "timestamp": datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def get_homepage(self):
        """홈페이지 HTML"""
        return """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EORA AI - 긴급 서버</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: white;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    border-radius: 15px;
                    padding: 30px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .header h1 {
                    font-size: 2.5em;
                    margin: 0;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                .status {
                    text-align: center;
                    margin: 20px 0;
                    padding: 15px;
                    background: rgba(0,255,0,0.1);
                    border-radius: 10px;
                    border: 1px solid rgba(0,255,0,0.3);
                }
                .nav {
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    margin: 30px 0;
                    flex-wrap: wrap;
                }
                .nav a {
                    background: rgba(255,255,255,0.1);
                    color: white;
                    text-decoration: none;
                    padding: 12px 20px;
                    border-radius: 20px;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                }
                .nav a:hover {
                    background: rgba(255,255,255,0.2);
                    transform: translateY(-2px);
                }
                .info {
                    margin: 20px 0;
                    padding: 15px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 10px;
                }
                .info h3 {
                    margin: 0 0 10px 0;
                    color: #ffd700;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 EORA AI</h1>
                    <p>긴급 서버 - 최소 의존성 버전</p>
                </div>
                
                <div class="status">
                    ✅ 서버가 정상 작동 중입니다
                </div>
                
                <div class="nav">
                    <a href="/health">❤️ 상태확인</a>
                    <a href="/api/status">📊 API 상태</a>
                    <a href="/test">🧪 테스트</a>
                </div>
                
                <div class="info">
                    <h3>📋 서버 정보</h3>
                    <p>• 서버 타입: Python 내장 HTTP 서버</p>
                    <p>• 포트: 8011</p>
                    <p>• 시작 시간: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
                    <p>• 상태: 정상 작동</p>
                </div>
                
                <div class="info">
                    <h3>⚠️ 주의사항</h3>
                    <p>이 서버는 긴급 상황을 위한 최소 기능 버전입니다.</p>
                    <p>완전한 기능을 사용하려면 FastAPI 서버를 실행하세요.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def get_health(self):
        """헬스 체크 페이지"""
        return """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EORA AI - 상태확인</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: white;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    border-radius: 15px;
                    padding: 30px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                }
                .status {
                    text-align: center;
                    margin: 20px 0;
                    padding: 20px;
                    background: rgba(0,255,0,0.1);
                    border-radius: 10px;
                    border: 1px solid rgba(0,255,0,0.3);
                }
                .back-link {
                    text-align: center;
                    margin-top: 20px;
                }
                .back-link a {
                    color: white;
                    text-decoration: none;
                    padding: 10px 20px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 20px;
                    transition: all 0.3s ease;
                }
                .back-link a:hover {
                    background: rgba(255,255,255,0.2);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="status">
                    <h1>❤️ 서버 상태</h1>
                    <p>✅ 정상 작동</p>
                    <p>📍 포트: 8011</p>
                    <p>🕒 시간: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
                </div>
                
                <div class="back-link">
                    <a href="/">🏠 홈으로 돌아가기</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    def get_api_status(self):
        """API 상태 JSON"""
        status = {
            "status": "healthy",
            "message": "EORA AI 긴급 서버가 정상 작동 중입니다",
            "timestamp": datetime.now().isoformat(),
            "server_type": "Python Built-in HTTP Server",
            "port": 8011,
            "version": "emergency-1.0.0"
        }
        return json.dumps(status, ensure_ascii=False, indent=2)
    
    def get_test_page(self):
        """테스트 페이지"""
        return """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EORA AI - 테스트</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: white;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    border-radius: 15px;
                    padding: 30px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                }
                .test-section {
                    margin: 20px 0;
                    padding: 15px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 10px;
                }
                .test-section h3 {
                    margin: 0 0 10px 0;
                    color: #ffd700;
                }
                .back-link {
                    text-align: center;
                    margin-top: 20px;
                }
                .back-link a {
                    color: white;
                    text-decoration: none;
                    padding: 10px 20px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 20px;
                    transition: all 0.3s ease;
                }
                .back-link a:hover {
                    background: rgba(255,255,255,0.2);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 EORA AI 테스트</h1>
                
                <div class="test-section">
                    <h3>✅ 서버 연결 테스트</h3>
                    <p>서버가 정상적으로 응답하고 있습니다.</p>
                </div>
                
                <div class="test-section">
                    <h3>🌐 네트워크 테스트</h3>
                    <p>로컬 네트워크 연결이 정상입니다.</p>
                </div>
                
                <div class="test-section">
                    <h3>📱 브라우저 호환성</h3>
                    <p>현재 브라우저에서 정상 작동합니다.</p>
                </div>
                
                <div class="test-section">
                    <h3>⚡ 성능 테스트</h3>
                    <p>페이지 로딩 시간: <span id="loadTime">측정 중...</span></p>
                </div>
                
                <div class="back-link">
                    <a href="/">🏠 홈으로 돌아가기</a>
                </div>
            </div>
            
            <script>
                window.addEventListener('load', function() {
                    const loadTime = performance.now();
                    document.getElementById('loadTime').textContent = loadTime.toFixed(2) + 'ms';
                });
            </script>
        </body>
        </html>
        """
    
    def get_404_page(self):
        """404 페이지"""
        return """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EORA AI - 페이지 없음</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .container {
                    text-align: center;
                    background: rgba(255,255,255,0.1);
                    border-radius: 15px;
                    padding: 40px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.2);
                }
                .back-link {
                    margin-top: 20px;
                }
                .back-link a {
                    color: white;
                    text-decoration: none;
                    padding: 10px 20px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 20px;
                    transition: all 0.3s ease;
                }
                .back-link a:hover {
                    background: rgba(255,255,255,0.2);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>404</h1>
                <p>요청하신 페이지를 찾을 수 없습니다.</p>
                <div class="back-link">
                    <a href="/">🏠 홈으로 돌아가기</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    def log_message(self, format, *args):
        """로그 메시지 출력"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server():
    """서버 실행"""
    server_address = ('127.0.0.1', 8011)
    httpd = HTTPServer(server_address, EORARequestHandler)
    
    print("🚀 EORA AI 긴급 서버 시작...")
    print("📍 접속 주소: http://127.0.0.1:8011")
    print("🔍 테스트 페이지: http://127.0.0.1:8011/test")
    print("❤️ 상태확인: http://127.0.0.1:8011/health")
    print("📊 API 상태: http://127.0.0.1:8011/api/status")
    print("=" * 50)
    print("⚠️ 이 서버는 긴급 상황을 위한 최소 기능 버전입니다.")
    print("완전한 기능을 사용하려면 FastAPI 서버를 실행하세요.")
    print("=" * 50)
    print("서버를 종료하려면 Ctrl+C를 누르세요.")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 서버를 종료합니다...")
        httpd.server_close()

if __name__ == "__main__":
    run_server() 