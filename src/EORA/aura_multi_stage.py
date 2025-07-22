"""
aura_multi_stage.py

다단계 회상 선택기 모듈
- user_id, 최신 user_input을 바탕으로 관련 메모리_atom을 조회/반환합니다.
"""

from pymongo import MongoClient

# MongoDB 설정
_client = MongoClient("mongodb://localhost:27017/")
_db = _client["EORA"]

def multi_stage_selector(user_id: str, user_input: str, max_atoms: int = 5):
    """
    회상할 메모리 atom을 선택하여 반환합니다.
    :param user_id: 사용자 ID
    :param user_input: 현재 입력 문장
    :param max_atoms: 최대 회상 개수
    :return: [{"content": str, ...}, ...]
    """
    # 예: 최근 memory_atoms 중 user_id, 유사 태그 match, timestamp 내림차순으로 조회
    # 간단화하여 사용자 ID 기반으로 최근 문서만 리턴
    records = _db.memory_atoms.find({"user_id": user_id}).sort("timestamp", -1).limit(max_atoms)
    return [{"content": rec.get("content", ""), "timestamp": rec.get("timestamp")} for rec in records]