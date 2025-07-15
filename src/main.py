#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EORA AI System - Main Entry Point
Railway 배포용 메인 파일
"""

import os
import sys
import logging
from pathlib import Path
import json

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_env_file():
    """환경변수 파일을 로드합니다."""
    try:
        from dotenv import load_dotenv
        env_file = ".env"
        if os.path.exists(env_file):
            load_dotenv(env_file)
            logger.info(f".env 파일 로드 완료: {env_file}")
        else:
            logger.info(f".env 파일이 존재하지 않습니다: {env_file}")
    except ImportError:
        logger.info("python-dotenv가 설치되지 않았습니다. 환경변수 파일 로드를 건너뜁니다.")
    except Exception as e:
        logger.error(f".env 파일 로드 실패: {e}")

def init_openai_client():
    """OpenAI 클라이언트를 초기화합니다."""
    try:
        logger.info("OpenAI 클라이언트 초기화 시도...")
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY가 설정되지 않았습니다.")
            return None
        
        # 최신 OpenAI SDK에 맞게 초기화
        openai.api_key = api_key
        logger.info("OpenAI 클라이언트 초기화 성공")
        return openai
    except Exception as e:
        logger.error(f"OpenAI 클라이언트 초기화 실패: {e}")
        return None

def load_prompts_data():
    """프롬프트 데이터를 로드합니다."""
    try:
        logger.info("📚 프롬프트 데이터 로드 중...")
        
        # 여러 경로에서 ai_prompts.json 파일을 찾기
        possible_paths = [
            "ai_prompts.json",
            "ai_brain/ai_prompts.json", 
            "templates/ai_prompts.json",
            "prompts/ai_prompts.json"
        ]
        
        prompts_data = None
        loaded_path = None
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        raw_data = json.load(f)
                    
                    # 새로운 JSON 구조 처리 (prompts 키가 있는 경우)
                    if "prompts" in raw_data:
                        prompts_data = raw_data["prompts"]
                        ai_count = len(prompts_data)
                    else:
                        # 기존 구조 처리
                        prompts_data = raw_data
                        ai_count = len(prompts_data.get('ai_list', []))
                    
                    loaded_path = path
                    logger.info(f"✅ ai_prompts.json 파일 로드 완료: {ai_count}개 AI (경로: {loaded_path})")
                    return prompts_data
                except Exception as e:
                    logger.warning(f"파일 로드 실패 ({path}): {e}")
                    continue
        
        logger.warning("❌ ai_prompts.json 파일을 찾을 수 없습니다.")
        return None
            
    except Exception as e:
        logger.error(f"프롬프트 데이터 로드 실패: {e}")
        return None

def check_port_availability(port):
    """포트 사용 가능 여부를 확인합니다."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_available_port(start_port=8081):
    """사용 가능한 포트를 찾습니다."""
    port = start_port
    while port < start_port + 100:  # 최대 100개 포트 시도
        if check_port_availability(port):
            return port
        port += 1
    return None

# app.py에서 FastAPI 앱을 import
try:
    from app import app
    logger.info("✅ app.py 로드 성공")
except Exception as e:
    logger.error(f"❌ app.py 로드 실패: {e}")
    # app이 로드되지 않아도 main.py는 실행 가능하도록 함
    app = None

if __name__ == "__main__":
    # 환경변수 로드
    load_env_file()
    
    # OpenAI 클라이언트 초기화
    openai_client = init_openai_client()
    
    # 프롬프트 데이터 로드
    prompts_data = load_prompts_data()
    
    # app이 로드되지 않았다면 종료
    if app is None:
        logger.error("❌ app.py에서 FastAPI 앱을 로드할 수 없습니다.")
        sys.exit(1)
    
    # uvicorn으로 서버 실행
    import uvicorn
    
    # Railway 환경에서 포트 설정
    default_port = int(os.getenv("PORT", 8081))
    
    # 포트 사용 가능 여부 확인
    if not check_port_availability(default_port):
        logger.warning(f"⚠️ 포트 {default_port}가 이미 사용 중입니다. 다른 포트를 찾습니다.")
        available_port = find_available_port(default_port + 1)
        if available_port:
            port = available_port
            logger.info(f"✅ 사용 가능한 포트 발견: {port}")
        else:
            logger.error("❌ 사용 가능한 포트를 찾을 수 없습니다.")
            sys.exit(1)
    else:
        port = default_port
    
    host = "0.0.0.0"
    
    logger.info(f"🚀 서버 시작: {host}:{port}")
    uvicorn.run(app, host=host, port=port) 