#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import requests

def start_server():
    """EORA AI 서버를 시작하고 상태를 확인합니다"""
    
    print("🚀 EORA AI 서버 시작 중...")
    
    # 1. src 디렉토리로 이동
    os.chdir("src")
    print(f"📁 작업 디렉토리: {os.getcwd()}")
    
    # 2. 환경변수 확인
    from dotenv import load_dotenv
    load_dotenv("../.env")
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        print(f"✅ API 키 로드됨: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ API 키가 설정되지 않았습니다")
    
    # 3. 서버 시작
    try:
        print("🔄 uvicorn 서버 시작 중...")
        
        # uvicorn 명령어 실행
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "127.0.0.1", 
            "--port", "8001", 
            "--reload"
        ]
        
        print(f"📝 실행 명령어: {' '.join(cmd)}")
        
        # 서버 프로세스 시작
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 5초 대기
        print("⏳ 서버 시작 대기 중... (5초)")
        time.sleep(5)
        
        # 4. 서버 상태 확인
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=5)
            if response.status_code == 200:
                print("✅ 서버가 정상적으로 시작되었습니다!")
                print(f"🌐 접속 주소: http://127.0.0.1:8001")
                print(f"🔧 관리자 페이지: http://127.0.0.1:8001/admin")
                print(f"📊 응답: {response.json()}")
                
                # 프로세스를 계속 실행시키기 위해 대기
                print("\n💡 서버가 실행 중입니다. 종료하려면 Ctrl+C를 누르세요.")
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 서버를 종료합니다...")
                    process.terminate()
                    
            else:
                print(f"❌ 서버 응답 오류: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 서버 연결 실패: {e}")
            
            # 프로세스 로그 확인
            stdout, stderr = process.communicate(timeout=1)
            if stdout:
                print(f"📝 서버 출력:\n{stdout}")
            if stderr:
                print(f"❌ 서버 오류:\n{stderr}")
                
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")

if __name__ == "__main__":
    start_server() 