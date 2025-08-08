from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List, Union
import json

def safe_serialize(obj: Any) -> Any:
    """모든 타입의 객체를 JSON 직렬화 가능한 형태로 변환"""
    try:
        if isinstance(obj, dict):
            return {k: safe_serialize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [safe_serialize(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)
    except Exception as e:
        print(f"⚠️ 직렬화 중 오류: {str(e)}")
        return {}

def safe_mongo_doc(doc: Dict) -> Dict:
    """MongoDB 문서를 안전하게 직렬화"""
    try:
        serialized = safe_serialize(doc)
        if "_id" in serialized and isinstance(doc["_id"], ObjectId):
            serialized["_id"] = str(doc["_id"])
        return serialized
    except Exception as e:
        print(f"⚠️ MongoDB 문서 직렬화 중 오류: {str(e)}")
        return {}

def safe_redis_value(value: Any) -> str:
    """Redis에 저장할 값을 안전하게 직렬화"""
    try:
        return json.dumps(safe_serialize(value), ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Redis 값 직렬화 중 오류: {str(e)}")
        return "{}"

def safe_deserialize_datetime(value: str) -> datetime:
    """ISO 형식 문자열을 datetime 객체로 안전하게 변환"""
    try:
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value
    except Exception as e:
        print(f"⚠️ datetime 역직렬화 중 오류: {str(e)}")
        return datetime.utcnow()

def safe_deserialize_objectid(value: str) -> ObjectId:
    """문자열을 ObjectId로 안전하게 변환"""
    try:
        if isinstance(value, str):
            return ObjectId(value)
        return value
    except Exception as e:
        print(f"⚠️ ObjectId 역직렬화 중 오류: {str(e)}")
        return None 