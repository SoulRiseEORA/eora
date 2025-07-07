#!/usr/bin/env python3
"""
EORA AI 서버 개발용 실행 스크립트 (자동 재시작)
"""

import uvicorn
import os
import sys

def main():
    # Railway 환경변수에서 포트 가져오기 (기본값을 8002로 변경)
    port = int(os.environ.get("PORT", 8002))
    
    print(f"🚀 EORA AI 개발 서버를 시작합니다...")
    print(f"📍 주소: http://127.0.0.1:{port}")
    print(f"📋 사용 가능한 페이지:")
    print(f"   - 홈: http://127.0.0.1:{port}/")
    print(f"   - 디버그: http://127.0.0.1:{port}/debug")
    print(f"   - 채팅: http://127.0.0.1:{port}/chat")
    print(f"   - 상태 확인: http://127.0.0.1:{port}/health")
    print("🔄 자동 재시작이 활성화되어 있습니다.")
    print("=" * 50)
    
    # 개발용 서버 실행 (reload=True)
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=port, 
        reload=True,  # 파일 변경 감지 활성화
        log_level="info"
    )

if __name__ == "__main__":
    main() 