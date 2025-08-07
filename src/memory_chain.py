# memory_chain.py
# EORA 기억 사슬 기반 회상 시스템 (1단계 구조)

import uuid
from datetime import datetime
from typing import List, Dict, Optional
import hashlib

class MemoryNode:
    def __init__(self, user, gpt, emotion, belief_tags, event_score, resonance_score=0.0, intuition_vector=None, parent_id=None):
        self.user = user
        self.gpt = gpt
        self.emotion = emotion
        self.belief_tags = belief_tags
        self.event_score = event_score
        self.recall_priority = event_score * 0.7 + len(belief_tags) * 0.3
        self.emotional_intensity = 0.9 if emotion == "positive" else 0.5
        self.resonance_score = resonance_score
        self.intuition_vector = intuition_vector or []
        self.timestamp = datetime.now().isoformat()
        self.parent_id = parent_id
        self.memory_id = self.generate_id()

    def generate_id(self):
        base = f"{self.user}{self.gpt}{self.timestamp}"
        return hashlib.sha256(base.encode()).hexdigest()

    def to_dict(self):
        return {
            "user": self.user,
            "gpt": self.gpt,
            "emotion": self.emotion,
            "belief_tags": self.belief_tags,
            "event_score": self.event_score,
            "recall_priority": self.recall_priority,
            "emotional_intensity": self.emotional_intensity,
            "resonance_score": self.resonance_score,
            "intuition_vector": self.intuition_vector,
            "timestamp": self.timestamp,
            "parent_id": self.parent_id,
            "memory_id": self.memory_id,
        }

# MemoryChainManager (기억 연결 및 회상 로직 - 초기 버전)
class MemoryChainManager:
    def __init__(self):
        self.memory_list: List[MemoryNode] = []

    def add_memory(self, node: MemoryNode):
        self.memory_list.append(node)

    def recall(self, user_input: str) -> Optional[MemoryNode]:
        # 간단한 키워드 유사도 또는 길이 기준 예시 회상
        for node in reversed(self.memory_list):
            if any(tag in user_input for tag in node.belief_tags):
                return node
        return None

    def to_dict_list(self) -> List[Dict]:
        return [node.to_dict() for node in self.memory_list]
