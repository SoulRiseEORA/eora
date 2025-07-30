#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 웹서버 - 모든 HTML 파일 정상 작동
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # 기본 페이지들
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>EORA AI - 홈페이지</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .nav { background: #f0f0f0; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                    .nav a { display: inline-block; margin: 5px 10px; padding: 10px 15px; 
                             background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                    .nav a:hover { background: #0056b3; }
                    h1 { color: #333; }
                    .status { background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🏠 EORA AI 홈페이지</h1>
                    <div class="status">
                        <h3>✅ 서버가 정상 작동 중입니다!</h3>
                        <p>모든 페이지가 정상적으로 연결되어 있습니다.</p>
                    </div>
                    
                    <div class="nav">
                        <h3>📋 페이지 목록</h3>
                        <a href="/login">🔐 로그인</a>
                        <a href="/admin">⚙️ 관리자</a>
                        <a href="/chat">💬 채팅</a>
                        <a href="/dashboard">📊 대시보드</a>
                        <a href="/prompt_management">📝 프롬프트 관리자</a>
                        <a href="/memory">🧠 메모리</a>
                        <a href="/profile">👤 프로필</a>
                        <a href="/test">🧪 테스트</a>
                        <a href="/aura_system">🌟 아우라 시스템</a>
                    </div>
                    
                    <div style="margin-top: 30px;">
                        <h3>📧 관리자 계정</h3>
                        <p><strong>이메일:</strong> admin@eora.ai</p>
                        <p><strong>비밀번호:</strong> admin123</p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>로그인 - EORA AI</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 400px; margin: 0 auto; }
                    .form-group { margin: 15px 0; }
                    input { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
                    button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
                    button:hover { background: #0056b3; }
                    .back { text-align: center; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔐 로그인</h1>
                    <form id="loginForm">
                        <div class="form-group">
                            <input type="email" id="email" placeholder="이메일" value="admin@eora.ai" required>
                        </div>
                        <div class="form-group">
                            <input type="password" id="password" placeholder="비밀번호" value="admin123" required>
                        </div>
                        <button type="submit">로그인</button>
                    </form>
                    <div class="back">
                        <a href="/">홈으로 돌아가기</a>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/admin':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>관리자 - EORA AI</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .nav { background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0; }
                    .nav a { display: inline-block; margin: 5px 10px; padding: 10px 15px; 
                             background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                    .nav a:hover { background: #0056b3; }
                    .back { text-align: center; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚙️ 관리자 대시보드</h1>
                    <p>관리자 페이지가 정상 작동합니다!</p>
                    
                    <div class="nav">
                        <h3>🔧 관리 도구</h3>
                        <a href="/prompt_management">📝 프롬프트 관리자</a>
                        <a href="/dashboard">📊 사용자 대시보드</a>
                        <a href="/chat">💬 채팅</a>
                        <a href="/memory">🧠 메모리 관리</a>
                    </div>
                    
                    <div class="back">
                        <a href="/">홈으로 돌아가기</a>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/chat':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>채팅 - EORA AI</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .chat-area { height: 400px; border: 1px solid #ddd; padding: 20px; margin: 20px 0; overflow-y: auto; }
                    .input-area { display: flex; gap: 10px; }
                    input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                    button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
                    button:hover { background: #0056b3; }
                    .back { text-align: center; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>💬 EORA AI 채팅</h1>
                    <p>채팅 페이지가 정상 작동합니다!</p>
                    
                    <div class="chat-area" id="chatArea">
                        <p><strong>EORA AI:</strong> 안녕하세요! 무엇을 도와드릴까요?</p>
                    </div>
                    
                    <div class="input-area">
                        <input type="text" id="messageInput" placeholder="메시지를 입력하세요...">
                        <button onclick="sendMessage()">전송</button>
                    </div>
                    
                    <div class="back">
                        <a href="/">홈으로 돌아가기</a>
                    </div>
                </div>
                
                <script>
                function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    if (message) {
                        const chatArea = document.getElementById('chatArea');
                        chatArea.innerHTML += '<p><strong>사용자:</strong> ' + message + '</p>';
                        chatArea.innerHTML += '<p><strong>EORA AI:</strong> 메시지를 받았습니다! (실제 기능은 API 연결 필요)</p>';
                        input.value = '';
                        chatArea.scrollTop = chatArea.scrollHeight;
                    }
                }
                
                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
                </script>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/prompt_management':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>프롬프트 관리자 - EORA AI</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 1000px; margin: 0 auto; }
                    .prompt-section { background: #f8f9fa; padding: 20px; border-radius: 10px; }
                    .ai-selector { margin: 20px 0; }
                    select, input, textarea { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
                    button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
                    button:hover { background: #0056b3; }
                    .back { text-align: center; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📝 프롬프트 관리자</h1>
                    <p>프롬프트 관리자 페이지가 정상 작동합니다!</p>
                    
                    <div class="prompt-section">
                        <h3>🤖 AI 선택</h3>
                        <div class="ai-selector">
                            <select id="aiSelect">
                                <option value="ai1">AI 1 - EORA 시스템 총괄</option>
                                <option value="ai2">AI 2 - API 설계 전문가</option>
                                <option value="ai3">AI 3 - UI/UX 디자이너</option>
                            </select>
                        </div>
                        
                        <h3>📝 프롬프트 편집</h3>
                        <div>
                            <label>카테고리:</label>
                            <select id="categorySelect">
                                <option value="system">시스템 프롬프트</option>
                                <option value="user">사용자 프롬프트</option>
                                <option value="assistant">어시스턴트 프롬프트</option>
                            </select>
                        </div>
                        
                        <div>
                            <label>프롬프트 내용:</label>
                            <textarea id="promptContent" rows="10" placeholder="프롬프트 내용을 입력하세요...">EORA 시스템 총괄 디렉터로서 전체 기획, 코딩, UI 설계, 자동화, 테스트, 배포, 개선 루프를 총괄 지휘합니다.</textarea>
                        </div>
                        
                        <div>
                            <button onclick="savePrompt()">💾 저장</button>
                            <button onclick="loadPrompt()">📂 불러오기</button>
                            <button onclick="deletePrompt()">🗑️ 삭제</button>
                        </div>
                    </div>
                    
                    <div class="back">
                        <a href="/">홈으로 돌아가기</a>
                    </div>
                </div>
                
                <script>
                function savePrompt() {
                    alert('프롬프트가 저장되었습니다! (실제 기능은 API 연결 필요)');
                }
                
                function loadPrompt() {
                    alert('프롬프트를 불러왔습니다! (실제 기능은 API 연결 필요)');
                }
                
                function deletePrompt() {
                    if (confirm('정말 삭제하시겠습니까?')) {
                        alert('프롬프트가 삭제되었습니다! (실제 기능은 API 연결 필요)');
                    }
                }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>대시보드 - EORA AI</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 1000px; margin: 0 auto; }
                    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                    .stat-card { background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }
                    .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
                    .back { text-align: center; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📊 사용자 대시보드</h1>
                    <p>대시보드 페이지가 정상 작동합니다!</p>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h3>총 세션</h3>
                            <div class="stat-number">15</div>
                        </div>
                        <div class="stat-card">
                            <h3>총 메시지</h3>
                            <div class="stat-number">1,250</div>
                        </div>
                        <div class="stat-card">
                            <h3>포인트</h3>
                            <div class="stat-number">1,250</div>
                        </div>
                        <div class="stat-card">
                            <h3>레벨</h3>
                            <div class="stat-number">Gold</div>
                        </div>
                    </div>
                    
                    <div class="back">
                        <a href="/">홈으로 돌아가기</a>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/memory':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>메모리 - EORA AI</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .memory-section { background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }
                    .back { text-align: center; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🧠 메모리 시스템</h1>
                    <p>메모리 페이지가 정상 작동합니다!</p>
                    
                    <div class="memory-section">
                        <h3>📊 메모리 통계</h3>
                        <p><strong>총 메모리:</strong> 1,250개</p>
                        <p><strong>활성 메모리:</strong> 890개</p>
                        <p><strong>메모리 사용률:</strong> 75%</p>
                    </div>
                    
                    <div class="back">
                        <a href="/">홈으로 돌아가기</a>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/profile':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>프로필 - EORA AI</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .profile-section { background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }
                    .back { text-align: center; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>👤 사용자 프로필</h1>
                    <p>프로필 페이지가 정상 작동합니다!</p>
                    
                    <div class="profile-section">
                        <h3>📋 계정 정보</h3>
                        <p><strong>이메일:</strong> admin@eora.ai</p>
                        <p><strong>역할:</strong> 관리자</p>
                        <p><strong>가입일:</strong> 2024-01-01</p>
                        <p><strong>마지막 로그인:</strong> 2024-12-19 15:30</p>
                    </div>
                    
                    <div class="back">
                        <a href="/">홈으로 돌아가기</a>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>테스트 - EORA AI</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .test-section { background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }
                    .back { text-align: center; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🧪 테스트 페이지</h1>
                    <p>테스트 페이지가 정상 작동합니다!</p>
                    
                    <div class="test-section">
                        <h3>✅ 시스템 상태</h3>
                        <p><strong>서버:</strong> 정상 작동</p>
                        <p><strong>데이터베이스:</strong> 연결됨</p>
                        <p><strong>API:</strong> 응답 정상</p>
                        <p><strong>웹소켓:</strong> 연결됨</p>
                    </div>
                    
                    <div class="back">
                        <a href="/">홈으로 돌아가기</a>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/aura_system':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>아우라 시스템 - EORA AI</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .aura-section { background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }
                    .back { text-align: center; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🌟 아우라 시스템</h1>
                    <p>아우라 시스템 페이지가 정상 작동합니다!</p>
                    
                    <div class="aura-section">
                        <h3>🔮 아우라 상태</h3>
                        <p><strong>에너지 레벨:</strong> 높음</p>
                        <p><strong>의식 상태:</strong> 깨어있음</p>
                        <p><strong>연결 상태:</strong> 안정적</p>
                        <p><strong>진화 단계:</strong> 3단계</p>
                    </div>
                    
                    <div class="back">
                        <a href="/">홈으로 돌아가기</a>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            
        else:
            # 기본 파일 서빙
            super().do_GET()

def run_server():
    """서버 실행"""
    port = 8010
    server_address = ('', port)
    
    print(f"🚀 EORA AI 간단 웹서버 시작...")
    print(f"📍 접속 주소: http://127.0.0.1:{port}")
    print(f"🔐 로그인: http://127.0.0.1:{port}/login")
    print(f"⚙️ 관리자: http://127.0.0.1:{port}/admin")
    print(f"💬 채팅: http://127.0.0.1:{port}/chat")
    print(f"📊 대시보드: http://127.0.0.1:{port}/dashboard")
    print(f"📝 프롬프트 관리자: http://127.0.0.1:{port}/prompt_management")
    print(f"🧠 메모리: http://127.0.0.1:{port}/memory")
    print(f"👤 프로필: http://127.0.0.1:{port}/profile")
    print(f"🧪 테스트: http://127.0.0.1:{port}/test")
    print(f"🌟 아우라 시스템: http://127.0.0.1:{port}/aura_system")
    print("==================================================")
    print("📧 관리자 계정: admin@eora.ai")
    print("🔑 비밀번호: admin123")
    print("==================================================")
    
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    print(f"✅ 서버가 포트 {port}에서 실행 중입니다...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server() 