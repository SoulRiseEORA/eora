"""
aura_structurer.py

회상 및 메모리 저장 관련 핵심 함수 모듈
"""

from pymongo import MongoClient

# MongoDB 설정
_client = MongoClient("mongodb://localhost:27017/")
_db = _client["EORA"]

def store_memory_atom(user_id: str, conversation_id: str, content: str, source: str, timestamp):
    """
    새로운 memory_atom을 DB에 저장합니다.
    :param user_id: 사용자 ID
    :param conversation_id: 대화 세션 ID
    :param content: 저장할 내용
    :param source: 'assistant' 또는 'user' 등
    :param timestamp: datetime 객체
    """
    atom = {
        "memory_id": f"{conversation_id}_{source}",
        "user_id": user_id,
        "conversation_id": conversation_id,
        "content": content,
        "source": source,
        "tags": [],  # 태그는 추후 분석하여 채울 수 있음
        "resonance_score": None,
        "timestamp": timestamp
    }
    _db.memory_atoms.insert_one(atom)
    return atom