#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - Railway 서버 실행 스크립트
모듈화된 구조로 FastAPI 서버를 실행합니다.
"""

import os
import sys
import uvicorn
import argparse

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 상위 디렉토리를 Python 경로에 추가
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# 기본 환경변수 설정
os.environ.setdefault("DATABASE_NAME", "eora_ai")

# 명령행 인자 파싱
parser = argparse.ArgumentParser(description="EORA AI System - Railway 서버")
parser.add_argument("--host", default="0.0.0.0", help="서버 호스트")
parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)), help="서버 포트")
parser.add_argument("--reload", action="store_true", help="코드 변경 시 자동 재시작")
args = parser.parse_args()

if __name__ == "__main__":
    print(f"🚀 EORA AI System - Railway 서버 시작 중...")
    print(f"🔧 호스트: {args.host}, 포트: {args.port}")
    print(f"🔧 자동 재시작: {'활성화' if args.reload else '비활성화'}")
    print(f"🔧 데이터베이스: {os.environ.get('DATABASE_NAME')}")
    
    # FastAPI 서버 실행
    uvicorn.run(
        "app_modular:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    ) 