import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils_lightweight import simple_embed, cosine_similarity, simple_emotion
from datetime import datetime
from typing import List, Dict, Any, Optional

class RecallEngineV3:
    """
    EORA 고급 회상 엔진 v3 (경량화)
    - 신념, 감정, 임베딩, 키워드, 사슬, 공명, 직감 기반 회상
    - 외부 DB/대형 라이브러리 없이 메모리 내 자료구조와 경량 함수만 사용
    """
    def __init__(self):
        self.memory_list: List[Dict[str, Any]] = []

    def get_embedding(self, text: str) -> List[float]:
        return simple_embed(text)

    def store_memory(self, user: str, gpt: str, emotion: str, belief_tags: List[str], parent_id: Optional[str] = None, memory_type: str = "general", source: str = "self") -> str:
        embedding = self.get_embedding(user + " " + gpt)
        memory_id = str(len(self.memory_list) + 1)
        doc = {
            "user": user,
            "gpt": gpt,
            "emotion": emotion,
            "belief_tags": belief_tags,
            "event_score": 0.5,
            "recall_priority": 0.5,
            "emotional_intensity": 0.5,
            "resonance_score": 0.5,
            "intuition_vector": embedding,
            "timestamp": datetime.utcnow().isoformat(),
            "parent_id": parent_id,
            "memory_id": memory_id,
            "fade_score": 0.0,
            "memory_type": memory_type,
            "source": source
        }
        self.memory_list.append(doc)
        return memory_id

    def recall_memories(self, query: str, top_n: int = 3) -> List[Dict[str, Any]]:
        query_emb = self.get_embedding(query)
        scored = []
        for mem in self.memory_list:
            emb = mem.get("intuition_vector")
            if emb:
                sim = cosine_similarity(query_emb, emb)
                tag_overlap = len(set(mem.get("belief_tags", [])) & set(query.split()))
                resonance = mem.get("resonance_score", 0.0)
                if sim > 0.85 or tag_overlap >= 2 or resonance >= 0.7:
                    scored.append((sim + resonance + tag_overlap, mem))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:top_n]]

    def recall_by_belief(self, user_text: str) -> List[Dict[str, Any]]:
        # 신념 태그 기반 회상 (간단 버전)
        return [mem for mem in self.memory_list if any(tag in user_text for tag in mem.get("belief_tags", []))]

    def recall_by_emotion(self, emotion: str) -> List[Dict[str, Any]]:
        return [mem for mem in self.memory_list if mem.get("emotion") == emotion]

    def recall_chain(self, memory_id: str) -> List[Dict[str, Any]]:
        chain = []
        current = next((m for m in self.memory_list if m["memory_id"] == memory_id), None)
        while current:
            chain.append(current)
            if current.get("parent_id"):
                current = next((m for m in self.memory_list if m["memory_id"] == current["parent_id"]), None)
            else:
                break
        return chain[::-1]

    def recall_summary(self) -> List[str]:
        # 저장된 모든 메모리 요약 (간단 버전)
        return [f"{m['user']} → {m['gpt']}" for m in self.memory_list]

    def recall_by_intuition(self, query: str, min_score: float = 0.25) -> List[Dict[str, Any]]:
        query_emb = self.get_embedding(query)
        scored = []
        for mem in self.memory_list:
            emb = mem.get("intuition_vector")
            if emb:
                sim = cosine_similarity(query_emb, emb)
                if sim >= min_score:
                    scored.append((sim, mem))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:3]]

    def recall_by_emotion_analysis(self, user_text: str) -> List[Dict[str, Any]]:
        emotion = simple_emotion(user_text)
        if not emotion:
            return []
        return self.recall_by_emotion(emotion)

# 사용 예시 (테스트)
if __name__ == "__main__":
    engine = RecallEngineV3()
    mem_id = engine.store_memory("나는 실패할까 두려워", "실패는 성장의 일부입니다.", "fear", ["실패", "두려움"])
    recalls = engine.recall_memories("실패 두려움")
    print("[회상 결과]", recalls)
    belief_recalls = engine.recall_by_belief("나는 실패자야")
    print("[신념 회상]", belief_recalls)
    emotion_recalls = engine.recall_by_emotion("fear")
    print("[감정 회상]", emotion_recalls)
    chain = engine.recall_chain(mem_id)
    print("[사슬 회상]", chain)
    summary = engine.recall_summary()
    print("[요약]", summary)
    intuition = engine.recall_by_intuition("실패")
    print("[직감 회상]", intuition)
    emo_ana = engine.recall_by_emotion_analysis("나는 너무 불안하고 두려워")
    print("[감정 분석 회상]", emo_ana) 