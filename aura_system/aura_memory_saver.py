import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List

from aura_system.memory_structurer import create_memory_atom
from aura_system.aura_selector import load_config
from pymongo import MongoClient
import redis

MEMORY_JSON_PATH = Path(__file__).parent.parent / "memory" / "memory_db.json"

async def auto_store_memory(user_input: str, response: str, tags: List[str] = None) -> bool:
    """메모리 자동 저장
    
    Args:
        user_input (str): 사용자 입력
        response (str): AI 응답
        tags (List[str], optional): 태그 목록
        
    Returns:
        bool: 저장 성공 여부
    """
    try:
        if tags is None:
            tags = []
            
        # 감정 추정
        emotion = await estimate_emotion(user_input)
        if emotion:
            tags.append(emotion)
            
        # 메모리 원자 생성
        atom = create_memory_atom(
            content=user_input,
            response=response,
            tags=tags
        )
        
        if not atom:
            return False
            
        # 메모리 저장
        success = await insert_atom(atom)
        return success
    except Exception as e:
        logger.error(f"⚠️ 메모리 저장 실패: {str(e)}")
        return False

def auto_store_memory(user_input, gpt_response):
    # 대화 블록 기반 메모리 생성
    atom = create_memory_atom(user_input, gpt_response)
    
    config = load_config()
    storage = config.get("storage", "json")

    if storage == "mongo":
        try:
            client = MongoClient("mongodb://localhost:27017")
            db = client["eora"]
            db["memory_atoms"].insert_one(atom)
        except Exception as e:
            print(f"[MongoDB 저장 실패]: {e}")
    elif storage == "redis":
        try:
            r = redis.Redis()
            key = f"memory:{atom['timestamp']}"
            r.set(key, json.dumps(atom, ensure_ascii=False))
        except Exception as e:
            print(f"[Redis 저장 실패]: {e}")
    else:
        try:
            if MEMORY_JSON_PATH.exists():
                with open(MEMORY_JSON_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []
            data.append(atom)
            with open(MEMORY_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[JSON 저장 실패]: {e}")