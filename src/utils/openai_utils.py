import os
import threading
from typing import Optional, List
from dotenv import load_dotenv
from openai import OpenAI

# 프로세스 시작 시 1회 로딩 (.env는 로컬에서만)
if not os.getenv("RAILWAY_ENVIRONMENT"):
    try:
        load_dotenv()
    except Exception:
        pass


def get_clean_key(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    key = key.strip()
    return key if key.startswith("sk-") and len(key) > 60 else None


def _collect_keys() -> List[str]:
    names = [
        "OPENAI_API_KEY",
        "OPENAI_API_KEY_1",
        "OPENAI_API_KEY_2",
        "OPENAI_API_KEY_3",
        "OPENAI_API_KEY_4",
        "OPENAI_API_KEY_5",
    ]
    keys: List[str] = []
    for n in names:
        k = get_clean_key(os.getenv(n))
        if k:
            keys.append(k)
    # 단일 키가 환경 변수에만 있는 경우도 지원
    if not keys and get_clean_key(os.getenv("OPENAI_API_KEY")):
        keys.append(os.getenv("OPENAI_API_KEY"))
    return keys


_client_lock = threading.Lock()
_clients: List[OpenAI] = []
_rr_idx = 0


def _build_clients_if_needed():
    global _clients
    if _clients:
        return
    keys = _collect_keys()
    if not keys:
        print("⚠️ OpenAI API 키 없음")
        return
    # 타임아웃/재시도는 보수적으로 설정
    _clients = [OpenAI(api_key=k, timeout=30.0, max_retries=2) for k in keys]
    print(f"✅ OpenAI 클라이언트 준비: {len(_clients)}개")


def get_openai_client() -> OpenAI:
    """재사용 가능한 클라이언트 하나를 반환 (키가 여러 개면 라운드로빈)"""
    global _rr_idx
    with _client_lock:
        _build_clients_if_needed()
        if not _clients:
            raise RuntimeError("OpenAI 키/클라이언트가 준비되지 않았습니다.")
        cli = _clients[_rr_idx % len(_clients)]
        _rr_idx += 1
        return cli

import os
from dotenv import load_dotenv

def load_openai_api_key():
    """OpenAI API 키를 환경 변수에서 로드"""
    try:
        # Railway 환경이 아닐 때만 .env 파일 로드
        if not os.getenv("RAILWAY_ENVIRONMENT"):
            load_dotenv()
        else:
            print("🚂 Railway 환경 감지 - .env 파일 로드 건너뜀 (환경변수 우선)")
        
        # 여러 가능한 환경변수 이름 시도
        possible_keys = [
            "OPENAI_API_KEY",
            "OPENAI_API_KEY_1", 
            "OPENAI_API_KEY_2",
            "OPENAI_API_KEY_3",
            "OPENAI_API_KEY_4",
            "OPENAI_API_KEY_5"
        ]
        
        for key_name in possible_keys:
            api_key = os.getenv(key_name)
            if api_key and api_key.startswith("sk-") and len(api_key) > 50:
                print(f"✅ OpenAI API 키 로드 완료: {key_name}")
                return api_key
        
        print("⚠️ OpenAI API 키를 찾을 수 없습니다. 서버는 제한된 기능으로 동작합니다.")
        return None
        
    except Exception as e:
        print(f"❌ OpenAI API 키 로드 실패: {str(e)}")
        return None 