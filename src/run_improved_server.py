#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 개선된 서버 실행 스크립트
Railway 환경에서 안정적으로 실행됩니다.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """필요한 의존성 확인"""
    print("🔍 의존성 확인 중...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'jinja2',
        'pymongo',
        'openai',
        'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 설치 필요")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 설치가 필요한 패키지: {', '.join(missing_packages)}")
        print("다음 명령어로 설치하세요:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 모든 의존성이 설치되어 있습니다.")
    return True

def check_environment():
    """환경 변수 확인"""
    print("\n🔍 환경 변수 확인 중...")
    
    env_vars = {
        'OPENAI_API_KEY': 'OpenAI API 키',
        'MONGODB_URL': 'MongoDB 연결 URL',
        'PORT': '서버 포트'
    }
    
    missing_vars = []
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'OPENAI_API_KEY':
                print(f"✅ {description}: {'설정됨' if len(value) > 10 else '잘못된 형식'}")
            else:
                print(f"✅ {description}: {value}")
        else:
            print(f"⚠️ {description}: 설정되지 않음")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ 설정이 필요한 환경 변수: {', '.join(missing_vars)}")
        print("Railway 환경에서 환경 변수를 설정하거나 .env 파일을 생성하세요.")
    
    return len(missing_vars) == 0

def start_server(debug=False, port=None):
    """서버 시작"""
    print(f"\n🚀 EORA AI System 서버 시작 중...")
    
    # 기본 포트 설정
    if port is None:
        port = int(os.getenv('PORT', 8000))
    
    # 명령어 구성
    cmd = [sys.executable, 'app.py', '--host', '0.0.0.0', '--port', str(port)]
    
    if debug:
        cmd.append('--debug')
        print("🔧 디버그 모드로 시작합니다.")
    
    print(f"📡 서버 주소: http://0.0.0.0:{port}")
    print(f"🌐 외부 접속: http://localhost:{port}")
    print("\n" + "="*50)
    
    try:
        # 서버 시작
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 서버가 사용자에 의해 중단되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 서버 시작 실패: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        return False
    
    return True

def main():
    """메인 함수"""
    print("🚀 EORA AI System - 개선된 서버 실행 스크립트")
    print("=" * 50)
    
    # 의존성 확인
    if not check_dependencies():
        print("\n❌ 의존성 문제로 서버를 시작할 수 없습니다.")
        sys.exit(1)
    
    # 환경 변수 확인
    env_ok = check_environment()
    
    # 사용자 입력
    print("\n" + "="*50)
    print("서버 시작 옵션:")
    print("1. 기본 모드 (포트 8000)")
    print("2. 디버그 모드")
    print("3. 사용자 정의 포트")
    print("4. 종료")
    
    while True:
        try:
            choice = input("\n선택하세요 (1-4): ").strip()
            
            if choice == '1':
                start_server(debug=False)
                break
            elif choice == '2':
                start_server(debug=True)
                break
            elif choice == '3':
                try:
                    port = int(input("포트 번호를 입력하세요: "))
                    start_server(debug=False, port=port)
                    break
                except ValueError:
                    print("❌ 올바른 포트 번호를 입력하세요.")
            elif choice == '4':
                print("👋 프로그램을 종료합니다.")
                sys.exit(0)
            else:
                print("❌ 1-4 중에서 선택하세요.")
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다.")
            sys.exit(0)

if __name__ == "__main__":
    main() 