#!/usr/bin/env python3
"""
EORA AI 서버 안정 실행 스크립트
"""

import uvicorn
import os
import sys

def main():
    # Railway 환경변수에서 포트 가져오기 (기본값을 8004로 변경)
    port = int(os.environ.get("PORT", 8004))
    
    print(f"🚀 EORA AI 서버를 안정적으로 시작합니다...")
    print(f"📍 주소: http://127.0.0.1:{port}")
    print(f"📋 사용 가능한 페이지:")
    print(f"   - 홈: http://127.0.0.1:{port}/")
    print(f"   - 디버그: http://127.0.0.1:{port}/debug")
    print(f"   - 채팅: http://127.0.0.1:{port}/chat")
    print(f"   - 상태 확인: http://127.0.0.1:{port}/health")
    print("=" * 50)
    
    # 안정적인 서버 실행 (reload=False)
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=port, 
        reload=False,  # 파일 변경 감지 비활성화
        log_level="info"
    )

if __name__ == "__main__":
    main() 