#!/usr/bin/env python3
"""
EORA AI 서버 안정 실행 스크립트
배포용 서버를 안정적으로 실행합니다.
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    # 현재 디렉토리를 src로 설정
    src_path = Path(__file__).parent
    os.chdir(src_path)
    
    print("🚀 EORA AI 서버를 시작합니다...")
    print(f"📍 작업 디렉토리: {os.getcwd()}")
    print(f"📁 템플릿 경로: {src_path / 'templates'}")
    
    # 환경 변수 확인
    openai_key = os.getenv('OPENAI_API_KEY')
    mongodb_uri = os.getenv('MONGODB_URI')
    port = int(os.getenv('PORT', 8000))
    
    print(f"🔑 OpenAI API Key: {'설정됨' if openai_key else '미설정'}")
    print(f"🗄️ MongoDB URI: {'설정됨' if mongodb_uri else '미설정'}")
    print(f"🌐 포트: {port}")
    
    # 서버 설정 - 배포 안정성 최적화
    config = {
        "app": "main:app",
        "host": "0.0.0.0",  # 모든 인터페이스에서 접근 가능
        "port": port,       # 환경 변수에서 포트 가져오기
        "reload": False,    # 배포 환경에서는 reload 비활성화
        "workers": 1,       # 단일 워커로 안정성 확보
        "log_level": "info",
        "access_log": True,
        "timeout_keep_alive": 60,  # 타임아웃 증가
        "timeout_graceful_shutdown": 60,  # 종료 타임아웃 증가
        "limit_concurrency": 1000,  # 동시 연결 제한
        "limit_max_requests": 10000,  # 최대 요청 수 제한
        "backlog": 2048,  # 백로그 크기 증가
    }
    
    print("⚙️ 서버 설정:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*50)
    print("🌐 서버 시작 중...")
    print(f"📍 접속 주소: http://localhost:{port}")
    print("📋 사용 가능한 페이지:")
    print(f"   - 홈: http://localhost:{port}/")
    print(f"   - 채팅: http://localhost:{port}/chat")
    print(f"   - 대시보드: http://localhost:{port}/dashboard")
    print(f"   - API 테스트: http://localhost:{port}/api_test")
    print(f"   - 헬스 체크: http://localhost:{port}/health")
    print("="*50)
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 서버가 중지되었습니다.")
    except Exception as e:
        print(f"\n❌ 서버 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 