"""
ai_core.utils
- 유틸리티 함수 모듈
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """설정 로드
    
    Args:
        config_path (str, optional): 설정 파일 경로
        
    Returns:
        dict: 설정 데이터
    """
    try:
        load_dotenv()
        config = {
            'model_name': os.getenv('MODEL_NAME', 'gpt-3.5-turbo'),
            'temperature': float(os.getenv('TEMPERATURE', '0.7')),
            'max_tokens': int(os.getenv('MAX_TOKENS', '2000')),
            'api_key': os.getenv('OPENAI_API_KEY', '')
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
        
        return config
    except Exception as e:
        logger.error(f"⚠️ 설정 로드 실패: {str(e)}")
        return {}

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """설정 저장
    
    Args:
        config (dict): 설정 데이터
        config_path (str): 설정 파일 경로
        
    Returns:
        bool: 성공 여부
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"⚠️ 설정 저장 실패: {str(e)}")
        return False

def get_logger(name: str) -> logging.Logger:
    """로거 반환
    
    Args:
        name (str): 로거 이름
        
    Returns:
        logging.Logger: 로거 객체
    """
    return logging.getLogger(name)

def setup_logging(log_level: int = logging.INFO) -> None:
    """로깅 설정
    
    Args:
        log_level (int): 로그 레벨
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_config(config: Dict[str, Any]) -> bool:
    """설정 유효성 검사
    
    Args:
        config (dict): 설정 데이터
        
    Returns:
        bool: 유효성 여부
    """
    try:
        required_keys = ['model_name', 'temperature', 'max_tokens', 'api_key']
        return all(key in config for key in required_keys)
    except Exception as e:
        logger.error(f"⚠️ 설정 유효성 검사 실패: {str(e)}")
        return False

def get_environment() -> Dict[str, str]:
    """환경 변수 반환
    
    Returns:
        dict: 환경 변수
    """
    try:
        load_dotenv()
        return {
            'MODEL_NAME': os.getenv('MODEL_NAME', 'gpt-3.5-turbo'),
            'TEMPERATURE': os.getenv('TEMPERATURE', '0.7'),
            'MAX_TOKENS': os.getenv('MAX_TOKENS', '2000'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', '')
        }
    except Exception as e:
        logger.error(f"⚠️ 환경 변수 로드 실패: {str(e)}")
        return {} 