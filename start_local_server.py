#!/usr/bin/env python3
"""
EORA AI 로컬 서버 시작 스크립트
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path

def setup_environment():
    """환경 설정"""
    print("🔧 EORA AI 로컬 서버 환경 설정...")
    
    # 현재 디렉토리 확인
    current_dir = Path.cwd()
    print(f"📁 현재 디렉토리: {current_dir}")
    
    # app.py 파일 확인
    app_file = current_dir / "app.py"
    if not app_file.exists():
        print("❌ app.py 파일을 찾을 수 없습니다.")
        print("💡 src 디렉토리에서 실행해주세요.")
        return False
    
    print("✅ app.py 파일 발견")
    
    # 환경변수 확인
    env_file = current_dir.parent / ".env"
    if env_file.exists():
        print("✅ .env 파일 발견")
    else:
        print("⚠️ .env 파일이 없습니다. (선택사항)")
    
    return True

def start_server():
    """서버 시작"""
    print("\n🚀 EORA AI 로컬 서버를 시작합니다...")
    print("=" * 60)
    print("📍 서버 주소: http://localhost:8000")
    print("📍 관리자 페이지: http://localhost:8000/admin")
    print("📍 API 문서: http://localhost:8000/docs")
    print("=" * 60)
    print("🛑 서버를 중지하려면 Ctrl+C를 누르세요")
    print("=" * 60)
    
    try:
        # uvicorn으로 서버 실행
        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=8000,
            reload=True,  # 개발 모드
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 서버가 중지되었습니다.")
    except Exception as e:
        print(f"\n❌ 서버 실행 중 오류: {e}")

def main():
    """메인 함수"""
    print("🌟 EORA AI 로컬 서버 시작 도구")
    print("=" * 60)
    
    # 환경 설정
    if not setup_environment():
        sys.exit(1)
    
    # 서버 시작
    start_server()

if __name__ == "__main__":
    main()