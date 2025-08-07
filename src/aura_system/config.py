import os
import json
import configparser
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from aura_system.logger import logger

class Config:
    _instance = None
    _config = None
    _json_config = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.config_path = Path(__file__).parent / "config.json"
        self._load_config()
        self._load_ini_config()

    def _load_config(self):
        """JSON 설정 파일을 로드합니다."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._json_config = json.load(f)
            else:
                self._create_default_config()
                
            logger.info("✅ JSON 설정 로드 완료")
            
        except Exception as e:
            logger.error(f"❌ JSON 설정 로드 실패: {str(e)}")
            self._create_default_config()

    def _get_mongodb_uri(self):
        """Railway 환경에 맞는 MongoDB URI를 반환합니다."""
        # Railway 환경 감지
        is_railway = any([
            os.getenv("RAILWAY_ENVIRONMENT"),
            os.getenv("RAILWAY_PROJECT_ID"),
            os.getenv("RAILWAY_SERVICE_ID")
        ])
        
        if is_railway:
            # Railway 환경에서 MongoDB URL 찾기
            railway_urls = [
                os.getenv("MONGODB_URL"),
                os.getenv("MONGO_URL"),
                # 개별 변수로 구성된 URL
                f"mongodb://{os.getenv('MONGOUSER')}:{os.getenv('MONGOPASSWORD')}@{os.getenv('MONGOHOST')}:{os.getenv('MONGOPORT')}" if all([
                    os.getenv('MONGOUSER'), os.getenv('MONGOPASSWORD'), 
                    os.getenv('MONGOHOST'), os.getenv('MONGOPORT')
                ]) else None,
                os.getenv("MONGODB_URI")
            ]
            
            for url in railway_urls:
                if url and url.strip():
                    return url.strip()
            
            # Railway 환경에서도 URL을 찾을 수 없으면 기본값
            return "mongodb://localhost:27017"
        else:
            # 로컬 환경
            return os.getenv("MONGODB_URI", "mongodb://localhost:27017")

    def _create_default_config(self):
        """기본 JSON 설정을 생성합니다."""
        try:
            self._json_config = {
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "base_url": "https://api.openai.com/v1",
                    "embedding_model": "text-embedding-3-small",
                    "embedding_dimensions": 1536,
                    "embedding_batch_size": 100
                },
                "mongodb": {
                    "uri": self._get_mongodb_uri(),
                    "db_name": "aura_db",
                    "max_pool_size": 100,
                    "min_pool_size": 10
                },
                "redis": {
                    "host": os.getenv("REDIS_HOST", "localhost"),
                    "port": int(os.getenv("REDIS_PORT", "6379")),
                    "db": int(os.getenv("REDIS_DB", "0"))
                },
                "memory": {
                    "recall_threshold": 0.7,
                    "min_response_length": 50,
                    "max_context_size": 2000
                },
                "logging": {
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            }

            # 설정 파일 저장
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._json_config, f, indent=4, ensure_ascii=False)
                
            logger.info("✅ 기본 JSON 설정 생성 완료")
            
        except Exception as e:
            logger.error(f"❌ 기본 JSON 설정 생성 실패: {str(e)}")
            raise

    def _load_ini_config(self):
        """INI 설정 파일을 로드합니다."""
        logger.info("INI 설정 로드 시작...")
        try:
            self._config = configparser.ConfigParser()
            logger.info("ConfigParser 초기화 완료.")
            
            # 기본 설정
            self._config['DEFAULT'] = {
                'mongo_uri': self._json_config['mongodb']['uri'],
                'redis_uri': f"redis://{self._json_config['redis']['host']}:{self._json_config['redis']['port']}/{self._json_config['redis']['db']}",
                'vector_store_path': './vector_store',
                'log_level': self._json_config['logging']['level']
            }
            logger.info("기본 INI 설정 완료.")

            # 설정 파일 경로
            config_paths = [
                os.path.join(os.path.dirname(__file__), 'config.ini'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini'),
                os.path.expanduser('~/.aura/config.ini')
            ]

            # 설정 파일 로드
            for path in config_paths:
                if os.path.exists(path):
                    try:
                        self._config.read(path)
                        logger.info(f"✅ INI 설정 파일 로드됨: {path}")
                        break
                    except Exception as e:
                        logger.error(f"❌ INI 설정 파일 로드 실패: {path}, error: {e}")
            
            logger.info("INI 설정 로드 완료.")

        except Exception as e:
            logger.critical(f"❌ INI 설정 초기화 중 치명적인 오류 발생: {e}", exc_info=True)
            # INI 로드에 실패해도 프로그램이 완전히 죽지 않도록, 비어 있는 config 객체를 생성할 수 있습니다.
            self._config = configparser.ConfigParser()

    def get(self, key: str, default: Any = None) -> Any:
        """JSON 설정값 조회"""
        try:
            keys = key.split('.')
            value = self._json_config
            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
                    
                if value is None:
                    return default
                    
            return value
            
        except Exception as e:
            logger.error(f"❌ JSON 설정 조회 실패: {str(e)}")
            return default

    def set(self, key: str, value: Any) -> bool:
        """JSON 설정값 저장"""
        try:
            keys = key.split('.')
            config = self._json_config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
                
            config[keys[-1]] = value
            
            # 설정 파일 저장
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._json_config, f, indent=4, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ JSON 설정 저장 실패: {str(e)}")
            return False

    def update(self, updates: Dict[str, Any]) -> bool:
        """JSON 설정 일괄 업데이트"""
        try:
            self._json_config.update(updates)
            
            # 설정 파일 저장
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._json_config, f, indent=4, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ JSON 설정 업데이트 실패: {str(e)}")
            return False

    def get_mongo_uri(self) -> str:
        """MongoDB URI를 반환합니다."""
        return os.getenv('MONGO_URI') or self._config['DEFAULT']['mongo_uri']

    def get_redis_uri(self) -> str:
        """Redis URI를 반환합니다."""
        return os.getenv('REDIS_URI') or self._config['DEFAULT']['redis_uri']

    def get_vector_store_path(self) -> str:
        """Vector Store 경로를 반환합니다."""
        return os.getenv('VECTOR_STORE_PATH') or self._config['DEFAULT']['vector_store_path']

    def get_log_level(self) -> str:
        """로그 레벨을 반환합니다."""
        return os.getenv('LOG_LEVEL') or self._config['DEFAULT']['log_level']

# 전역 인스턴스
_config = None

def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.get_instance()
    return _config

def get_mongo_uri() -> str:
    """MongoDB URI를 반환합니다."""
    return get_config().get_mongo_uri()

def get_redis_uri() -> str:
    """Redis URI를 반환합니다."""
    return get_config().get_redis_uri()

def get_vector_store_path() -> str:
    """Vector Store 경로를 반환합니다."""
    return get_config().get_vector_store_path()

def get_log_level() -> str:
    """로그 레벨을 반환합니다."""
    return get_config().get_log_level() 