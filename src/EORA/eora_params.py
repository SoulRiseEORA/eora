import logging
from typing import Dict, Any, Optional
import json
import os

logger = logging.getLogger(__name__)

class EORAParams:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.params_file = "eora_params.json"
            self.params = self._load_params()
            self._initialized = True
    
    def _load_params(self) -> Dict[str, Any]:
        """파라미터 로드"""
        try:
            if os.path.exists(self.params_file):
                with open(self.params_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self._get_default_params()
        except Exception as e:
            logger.error(f"파라미터 로드 실패: {str(e)}")
            return self._get_default_params()
    
    def _get_default_params(self) -> Dict[str, Any]:
        """기본 파라미터"""
        return {
            "model": {
                "name": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "memory": {
                "max_tokens": 4000,
                "chunk_size": 5000
            },
            "emotion": {
                "enabled": True,
                "threshold": 0.5
            },
            "wisdom": {
                "enabled": True,
                "depth": 3
            },
            "truth": {
                "enabled": True,
                "threshold": 0.7
            }
        }
    
    async def get_current_params(self) -> Dict[str, Any]:
        """현재 파라미터 반환"""
        return self.params
    
    async def update_params(self, new_params: Dict[str, Any]) -> bool:
        """파라미터 업데이트"""
        try:
            # 기존 파라미터와 병합
            self.params.update(new_params)
            
            # 파일에 저장
            with open(self.params_file, 'w', encoding='utf-8') as f:
                json.dump(self.params, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            logger.error(f"파라미터 업데이트 실패: {str(e)}")
            return False
    
    async def reset_params(self) -> bool:
        """파라미터 초기화"""
        try:
            self.params = self._get_default_params()
            
            # 파일에 저장
            with open(self.params_file, 'w', encoding='utf-8') as f:
                json.dump(self.params, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            logger.error(f"파라미터 초기화 실패: {str(e)}")
            return False 