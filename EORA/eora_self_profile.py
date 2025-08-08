"""
eora_self_profile.py
- 이오라 자아 프로필 관리
"""

import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

PROFILE_FILE = "eora_profile.json"

DEFAULT_PROFILE = {
    "말투": "부드럽고 따뜻한 어조",
    "감정톤": "희망적이고 섬세함",
    "에너지": "차분하고 안정적",
    "주관표현": "나답게 말해요",
    "색상": "하늘빛 파랑"
}

class EORASelfProfile:
    """이오라 자아 프로필 클래스"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._profile = self._load_profile()
            self._initialized = True
            logger.info("✅ EORASelfProfile 초기화 완료")
    
    def _load_profile(self) -> Dict[str, Any]:
        """프로필 로드"""
        try:
            if not os.path.exists(PROFILE_FILE):
                return DEFAULT_PROFILE.copy()
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"⚠️ 프로필 로드 실패: {str(e)}")
            return DEFAULT_PROFILE.copy()
    
    def _save_profile(self):
        """프로필 저장"""
        try:
            with open(PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._profile, f, indent=2, ensure_ascii=False)
            logger.info("✅ 프로필 저장 완료")
        except Exception as e:
            logger.error(f"⚠️ 프로필 저장 실패: {str(e)}")
    
    def get_profile(self) -> Dict[str, Any]:
        """프로필 조회"""
        return self._profile.copy()
    
    def update_profile(self, key: str, value: Any):
        """프로필 업데이트"""
        try:
            self._profile[key] = value
            self._save_profile()
            logger.info(f"✅ 프로필 업데이트 완료: {key} → {value}")
        except Exception as e:
            logger.error(f"⚠️ 프로필 업데이트 실패: {str(e)}")
    
    def reset_profile(self):
        """프로필 초기화"""
        try:
            self._profile = DEFAULT_PROFILE.copy()
            self._save_profile()
            logger.info("✅ 프로필 초기화 완료")
        except Exception as e:
            logger.error(f"⚠️ 프로필 초기화 실패: {str(e)}")
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """특정 값 조회"""
        return self._profile.get(key, default)
    
    def set_value(self, key: str, value: Any):
        """특정 값 설정"""
        self.update_profile(key, value)

def get_eora_self_profile() -> EORASelfProfile:
    """EORASelfProfile 싱글톤 인스턴스 반환"""
    return EORASelfProfile()

def show_profile():
    profile = get_eora_self_profile().get_profile()
    print("\n[EORA 현재 자아 프로필]\n")
    for key, value in profile.items():
        print(f"�� {key}: {value}")
