from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from aura_system.memory_structurer import create_memory_atom
from aura_system.emotion_system.emotion_logic_module import get_emotion_logic_module

# DB 연결
client = MongoClient("mongodb://localhost:27017")
db = client["aura_memory"]
collection = db["memory_atoms"]

def insert_atom(user_input: str, gpt_response: str, origin_type="user") -> str:
    atom = create_memory_atom(user_input, gpt_response, origin_type)
    result = collection.insert_one(atom)
    print("✅ 저장된 기억:")
    print(f"🧠 input: {user_input}")
    print(f"🤖 output: {gpt_response[:60]}...")
    print(f"💓 감정: {atom['emotion_label']} ({atom['emotion_code']})  점수: {atom['emotion_score']}")
    print(f"🧠 신념 벡터: {atom['belief_vector']}")
    print(f"🌀 중요도: {atom['importance']}  공명: {atom['resonance_score']}")
    return str(result.inserted_id)

class EmotionMemoryInserter:
    def __init__(self):
        self.emotion_logic = get_emotion_logic_module()
        
    def insert_emotion_memory(self, text, context=None):
        """
        감정 메모리를 삽입하는 메서드
        """
        try:
            # 감정 분석
            emotion_label, emotion_code, weight = self.emotion_logic.estimate_emotion(text)
            
            # 메모리 원자 생성
            memory_atom = create_memory_atom(
                text=text,
                emotion=emotion_label,
                emotion_code=emotion_code,
                weight=weight,
                context=context
            )
            
            return memory_atom
            
        except Exception as e:
            print(f"감정 메모리 삽입 실패: {str(e)}")
            return None

# 싱글톤 인스턴스
_emotion_memory_inserter = None

def get_emotion_memory_inserter():
    global _emotion_memory_inserter
    if _emotion_memory_inserter is None:
        _emotion_memory_inserter = EmotionMemoryInserter()
    return _emotion_memory_inserter

if __name__ == "__main__":
    insert_atom("오늘 회의에서 무시당한 느낌이 들었어요.", "그 상황은 속상하고 외로움을 느꼈을 수 있어요.")
