#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway 배포 전 최종 검증 스크립트
모든 오류 해결 확인
"""

import os
import sys
import importlib
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_imports():
    """필수 모듈 import 확인"""
    logger.info("🔍 필수 모듈 import 확인 중...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'pymongo',
        'jinja2',
        'dotenv',
        'openai',
        'redis',
        'pydantic'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            logger.info(f"✅ {module} import 성공")
        except ImportError as e:
            logger.error(f"❌ {module} import 실패: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        logger.error(f"❌ 실패한 import: {failed_imports}")
        return False
    
    logger.info("✅ 모든 필수 모듈 import 성공")
    return True

def check_files():
    """필수 파일 존재 확인"""
    logger.info("📁 필수 파일 존재 확인 중...")
    
    required_files = [
        'railway_optimized.py',
        'requirements.txt',
        'railway.json',
        'Procfile',
        'home.html',
        'chat.html',
        'dashboard.html'
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            logger.info(f"✅ {file} 존재")
        else:
            logger.error(f"❌ {file} 없음")
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ 누락된 파일: {missing_files}")
        return False
    
    logger.info("✅ 모든 필수 파일 존재")
    return True

def check_railway_config():
    """Railway 설정 확인"""
    logger.info("⚙️ Railway 설정 확인 중...")
    
    # railway.json 확인
    if not Path('railway.json').exists():
        logger.error("❌ railway.json 없음")
        return False
    
    try:
        import json
        with open('railway.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 필수 설정 확인
        if 'deploy' not in config:
            logger.error("❌ railway.json에 deploy 섹션 없음")
            return False
        
        if 'startCommand' not in config['deploy']:
            logger.error("❌ railway.json에 startCommand 없음")
            return False
        
        start_command = config['deploy']['startCommand']
        if 'railway_optimized.py' not in start_command:
            logger.error(f"❌ 잘못된 startCommand: {start_command}")
            return False
        
        logger.info(f"✅ Railway startCommand: {start_command}")
        
    except Exception as e:
        logger.error(f"❌ railway.json 파싱 실패: {e}")
        return False
    
    # Procfile 확인
    if Path('Procfile').exists():
        try:
            with open('Procfile', 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if 'railway_optimized.py' in content:
                logger.info(f"✅ Procfile: {content}")
            else:
                logger.error(f"❌ 잘못된 Procfile: {content}")
                return False
        except Exception as e:
            logger.error(f"❌ Procfile 읽기 실패: {e}")
            return False
    
    logger.info("✅ Railway 설정 완료")
    return True

def check_server_code():
    """서버 코드 문법 확인"""
    logger.info("🔧 서버 코드 문법 확인 중...")
    
    try:
        # 서버 파일 컴파일 테스트
        with open('railway_optimized.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, 'railway_optimized.py', 'exec')
        logger.info("✅ 서버 코드 컴파일 성공")
        
        # 주요 함수 존재 확인
        if 'async def lifespan(' in code:
            logger.info("✅ lifespan 함수 존재")
        else:
            logger.error("❌ lifespan 함수 없음")
            return False
        
        if 'app = FastAPI(' in code:
            logger.info("✅ FastAPI 앱 생성 코드 존재")
        else:
            logger.error("❌ FastAPI 앱 생성 코드 없음")
            return False
        
        if 'uvicorn.run(' in code:
            logger.info("✅ uvicorn 실행 코드 존재")
        else:
            logger.error("❌ uvicorn 실행 코드 없음")
            return False
        
    except SyntaxError as e:
        logger.error(f"❌ 서버 코드 문법 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 서버 코드 확인 실패: {e}")
        return False
    
    logger.info("✅ 서버 코드 문법 완료")
    return True

def check_requirements():
    """requirements.txt 확인"""
    logger.info("📦 requirements.txt 확인 중...")
    
    if not Path('requirements.txt').exists():
        logger.error("❌ requirements.txt 없음")
        return False
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = f.read()
        
        # 필수 패키지 확인
        required_packages = [
            'fastapi',
            'uvicorn',
            'pymongo',
            'jinja2',
            'python-dotenv',
            'openai',
            'redis',
            'pydantic'
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ 누락된 패키지: {missing_packages}")
            return False
        
        logger.info("✅ requirements.txt 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ requirements.txt 확인 실패: {e}")
        return False

def main():
    """메인 검증 함수"""
    logger.info("🚀 Railway 배포 전 최종 검증 시작")
    
    checks = [
        ("필수 파일 확인", check_files),
        ("Railway 설정 확인", check_railway_config),
        ("서버 코드 확인", check_server_code),
        ("requirements.txt 확인", check_requirements),
        ("모듈 import 확인", check_imports)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        logger.info(f"\n{'='*50}")
        logger.info(f"🔍 {check_name}")
        logger.info(f"{'='*50}")
        
        try:
            if check_func():
                passed += 1
                logger.info(f"✅ {check_name} 통과")
            else:
                logger.error(f"❌ {check_name} 실패")
        except Exception as e:
            logger.error(f"❌ {check_name} 오류: {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"📊 검증 결과: {passed}/{total} 통과")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 모든 검증 통과! Railway 배포 준비 완료!")
        logger.info("✅ 다음 단계: git add . && git commit -m 'Railway 배포 준비 완료' && git push")
        return True
    else:
        logger.error(f"❌ {total - passed}개 검증 실패. 배포 전 수정 필요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 