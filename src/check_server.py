#!/usr/bin/env python3
"""
서버 상태 확인 스크립트
"""

import socket
import sys
import os

def check_port(host, port):
    """포트가 사용 중인지 확인합니다."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def check_server_status():
    """서버 상태를 확인합니다."""
    host = "127.0.0.1"
    ports = [8080, 8081, 8082, 8000, 8001]
    
    print("🔍 서버 상태 확인 중...")
    print(f"📍 호스트: {host}")
    print()
    
    for port in ports:
        if check_port(host, port):
            print(f"✅ 포트 {port}: 사용 중 (서버 실행 중)")
        else:
            print(f"❌ 포트 {port}: 사용 안함")
    
    print()
    print("💡 권장 포트: 8081")
    print("🚀 서버 시작 명령어:")
    print("   python -m uvicorn main:app --host 127.0.0.1 --port 8081 --reload")
    print("   또는")
    print("   .\\start_server.ps1")

if __name__ == "__main__":
    check_server_status() 