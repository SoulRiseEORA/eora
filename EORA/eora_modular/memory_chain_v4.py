import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recall_engine_v3 import RecallEngineV3

# RecallEngineV3 인스턴스 생성 (전역)
recall_engine = RecallEngineV3()

# 벡터화기 및 코퍼스(전체 기억 텍스트) 관리
vectorizer = TfidfVectorizer()
corpus = []  # 전체 기억 텍스트 저장용

class MemoryNode:
    """
    EORA 기억 노드 구조체
    """
    def __init__(self, user: str, gpt: str, emotion: str, belief_tags: List[str], event_score: float,
                 recall_priority: float, emotional_intensity: float, resonance_score: float,
                 intuition_vector: List[float], timestamp: Optional[str] = None, parent_id: Optional[str] = None,
                 memory_id: Optional[str] = None, fade_score: float = 0.0, memory_type: str = "general", source: str = "self"):
        self.user = user
        self.gpt = gpt
        self.emotion = emotion
        self.belief_tags = belief_tags
        self.event_score = event_score
        self.recall_priority = recall_priority
        self.emotional_intensity = emotional_intensity
        self.resonance_score = resonance_score
        self.intuition_vector = intuition_vector
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.parent_id = parent_id
        self.memory_id = memory_id or str(uuid.uuid4())
        self.fade_score = fade_score
        self.memory_type = memory_type
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class MemoryChain:
    """
    기억 사슬(그래프) 관리
    """
    def __init__(self):
        self.nodes: Dict[str, MemoryNode] = {}
        self.edges: Dict[str, List[str]] = {}  # parent_id -> [child_id,...]

    def add_memory(self, node: MemoryNode):
        self.nodes[node.memory_id] = node
        if node.parent_id:
            self.edges.setdefault(node.parent_id, []).append(node.memory_id)

    def get_memory(self, memory_id: str) -> Optional[MemoryNode]:
        return self.nodes.get(memory_id)

    def get_chain(self, start_id: str) -> List[MemoryNode]:
        chain = []
        current = self.get_memory(start_id)
        while current:
            chain.append(current)
            if current.parent_id:
                current = self.get_memory(current.parent_id)
            else:
                break
        return chain[::-1]  # root부터

    def find_by_belief_tag(self, tag: str) -> List[MemoryNode]:
        return [n for n in self.nodes.values() if tag in n.belief_tags]

# 임베딩 생성 함수 (TF-IDF 기반)
def get_embedding(text: str) -> np.ndarray:
    global corpus, vectorizer
    corpus.append(text)
    vectorizer.fit(corpus)
    return vectorizer.transform([text]).toarray()[0]

# 코사인 유사도 함수 (numpy 기반)
def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

# 기억 저장 (recall_engine_v3 기반)
def store_memory(user, gpt, emotion, belief_tags, parent_id=None, memory_type="general", source="self"):
    return recall_engine.store_memory(user, gpt, emotion, belief_tags, parent_id, memory_type, source)

def recall_memories(query, top_n=3):
    return recall_engine.recall_memories(query, top_n=top_n)

def recall_by_belief(user_text):
    return recall_engine.recall_by_belief(user_text)

def recall_by_emotion(emotion):
    return recall_engine.recall_by_emotion(emotion)

def recall_chain(memory_id):
    return recall_engine.recall_chain(memory_id)

def recall_by_intuition(query, min_score=0.25):
    return recall_engine.recall_by_intuition(query, min_score)

def recall_by_emotion_analysis(user_text):
    return recall_engine.recall_by_emotion_analysis(user_text)

def recall_summary(user_id=None):
    return recall_engine.recall_summary()

# 통찰 도출
def infer_insight(memories):
    engine = InsightEngine()
    return engine.infer(memories)

# 지혜 판단
def generate_wise_response(memories, context, user_emotion):
    engine = WisdomEngine()
    insight = infer_insight(memories)
    return engine.judge(insight, context, user_emotion)

# 진리 인식
def detect_core_truth(memories):
    engine = TruthSense()
    return engine.detect(memories)

# 존재 감각
def realize_identity(memories):
    engine = SelfRealizer()
    return engine.generate_identity(memories)

# PyQt UI 연동 예시
def create_ui():
    app = QApplication([])
    log = QTextEdit()
    log.setReadOnly(True)
    input_field = QLineEdit()
    input_field.setPlaceholderText("👤 사용자 응답 또는 /첨부:파일명 입력")
    log.append("EORA 시스템이 시작되었습니다.")
    input_field.returnPressed.connect(lambda: log.append(f"입력: {input_field.text()}"))
    log.show()
    input_field.show()
    app.exec_()

# 테스트 예시 (실제 사용 시 별도 테스트 파일 권장)
if __name__ == "__main__":
    # 1. 기억 저장
    mem_id = store_memory("오늘은 의미를 찾고 싶어요.", "삶의 의미에 대해 생각해볼 수 있어요.", "curious", ["의미", "삶"])
    # 2. 회상
    recalls = recall_memories("의미 삶")
    print("[회상 결과]", recalls)
    # 3. 신념 기반 회상
    belief_recalls = recall_by_belief("나는 실패자야")
    print("[신념 회상]", belief_recalls)
    # 4. 감정 기반 회상
    emotion_recalls = recall_by_emotion("curious")
    print("[감정 회상]", emotion_recalls)
    # 5. 사슬 기반 회상
    chain = recall_chain(mem_id)
    print("[사슬 회상]", chain)
    # 6. 직감 기반 회상
    intuition = recall_by_intuition("의미")
    print("[직감 회상]", intuition)
    # 7. 감정 분석 기반 회상
    emo_ana = recall_by_emotion_analysis("나는 너무 불안하고 두려워")
    print("[감정 분석 회상]", emo_ana)
    # 8. 요약/철학 분석
    summary = recall_summary()
    print("[요약/철학 분석]", summary)
    # 9. 통찰
    insight = infer_insight(recalls)
    print("[통찰]", insight)
    # 10. 지혜
    wise = generate_wise_response(recalls, context="일상", user_emotion="curious")
    print("[지혜]", wise)
    # 11. 진리
    truth = detect_core_truth(recalls)
    print("[진리]", truth)
    # 12. 존재
    identity = realize_identity(recalls)
    print("[존재]", identity)
    # 13. PyQt UI 예시
    # create_ui() 