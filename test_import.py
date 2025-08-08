#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모듈 import 테스트 스크립트
"""

import os
import sys
import logging

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """모듈 import 테스트"""
    logger.info("모듈 import 테스트 시작")
    
    # API 라우터 import 테스트
    try:
        import api.routes
        logger.info("✅ API 라우터 import 성공")
    except Exception as e:
        logger.error(f"❌ API 라우터 import 실패: {e}")
    
    # 모델 import 테스트
    try:
        import models.session
        import models.auth
        logger.info("✅ 모델 import 성공")
    except Exception as e:
        logger.error(f"❌ 모델 import 실패: {e}")
    
    # 서비스 import 테스트
    try:
        import services.openai_service
        logger.info("✅ 서비스 import 성공")
    except Exception as e:
        logger.error(f"❌ 서비스 import 실패: {e}")
    
    # 데이터베이스 import 테스트
    try:
        import database
        logger.info("✅ 데이터베이스 import 성공")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 import 실패: {e}")
    
    # 인증 시스템 import 테스트
    try:
        import auth_system
        logger.info("✅ 인증 시스템 import 성공")
    except Exception as e:
        logger.error(f"❌ 인증 시스템 import 실패: {e}")
    
    logger.info("모듈 import 테스트 완료")

if __name__ == "__main__":
    test_imports() 