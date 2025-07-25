#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import subprocess
import time

def check_port(port):
    """포트 사용 여부 확인"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}"', 
            shell=True, 
            capture_output=True, 
            text=True
        )
        return len(result.stdout.strip()) > 0
    except:
        return False

def test_server(port, path=""):
    """서버 연결 테스트"""
    try:
        url = f"http://127.0.0.1:{port}{path}"
        response = requests.get(url, timeout=3)
        return {
            "status": "✅ 연결 성공",
            "status_code": response.status_code,
            "url": url
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "❌ 연결 실패",
            "status_code": None,
            "url": f"http://127.0.0.1:{port}{path}"
        }
    except Exception as e:
        return {
            "status": f"❌ 오류: {e}",
            "status_code": None,
            "url": f"http://127.0.0.1:{port}{path}"
        }

def main():
    print("🔍 EORA AI 서버 상태 확인 중...")
    print("=" * 50)
    
    # 확인할 포트 목록
    ports_to_check = [8000, 8001, 8002, 8003, 8080]
    
    active_servers = []
    
    for port in ports_to_check:
        print(f"📍 포트 {port} 확인 중...", end=" ")
        
        if check_port(port):
            # 포트가 사용 중인 경우 연결 테스트
            test_result = test_server(port)
            print(test_result["status"])
            
            if test_result["status_code"] == 200:
                active_servers.append({
                    "port": port,
                    "url": test_result["url"],
                    "admin": f"http://127.0.0.1:{port}/admin",
                    "health": f"http://127.0.0.1:{port}/health"
                })
        else:
            print("⚪ 사용 안함")
    
    print("=" * 50)
    
    if active_servers:
        print("✅ 사용 가능한 서버:")
        for server in active_servers:
            print(f"  📍 포트 {server['port']}:")
            print(f"     🌐 메인: {server['url']}")
            print(f"     🔧 관리자: {server['admin']}")
            print(f"     📊 상태: {server['health']}")
            print()
        
        print("💡 브라우저에서 위 주소들을 클릭해서 접속하세요!")
        
        # 첫 번째 서버의 상태 확인
        first_server = active_servers[0]
        print(f"\n🚀 {first_server['url']} 상세 상태 확인:")
        health_result = test_server(first_server['port'], "/health")
        if health_result["status_code"] == 200:
            print("✅ 서버 정상 작동 중!")
        
    else:
        print("❌ 실행 중인 서버가 없습니다.")
        print("💡 start_final.bat을 실행하여 서버를 시작하세요.")

if __name__ == "__main__":
    main()
    input("\n아무 키나 누르면 종료합니다...") 