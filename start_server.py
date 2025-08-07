#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - 서버 시작 스크립트
"""

import os
import sys
import subprocess
import platform

# 현재 디렉토리 출력
print("현재 디렉토리:", os.getcwd())
print("스크립트 위치:", os.path.dirname(os.path.abspath(__file__)))

# src 디렉토리 경로 설정
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
print("src 디렉토리:", src_dir)

# 작업 디렉토리 변경
os.chdir(src_dir)
print("작업 디렉토리를 변경했습니다:", os.getcwd())

# 환경 변수 설정
os.environ["OPENAI_API_KEY"] = "sk-test-api-key-for-testing-only"

# 서버 시작 메시지
print("🚀 EORA AI System - 서버 시작 중...")
print("🔧 호스트: 0.0.0.0, 포트: 8011")
print("🔧 데이터베이스: eora_ai")

# 기존 프로세스 종료 시도
if platform.system() == "Windows":
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
    except:
        pass

# 서버 실행
import uvicorn
uvicorn.run(
    "app_modular:app", 
    host="0.0.0.0", 
    port=8011, 
    reload=False,
    log_level="info"
) 