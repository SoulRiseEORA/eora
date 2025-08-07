# EORA Self-Evolving Mini AI Core
# 각 미니AI는 고유의 철학, 사명, 기억, 판단 기준을 갖고 독립 실행 가능
# 벡터기반 유사 판단 + 자기 리팩터링 + 루프 증식 구조 포함

import uuid
import datetime
from typing import List, Dict, Any, Tuple

class MiniAI:
    def __init__(self, name: str, mission: str, core_values: List[str], initial_knowledge: List[str]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.created_at = datetime.datetime.utcnow()
        self.mission = mission
        self.core_values = core_values
        self.knowledge_base = initial_knowledge[:]  # 교훈, 명언, 전략, 철학
        self.loop_memory = []  # 모든 판단 루프
        self.evolution_trace = []  # 구조 변화 기록

    def judge(self, situation: str) -> Tuple[str, str]:
        # 감정 진폭 기반 판단 + 메시지 응답 반환 (emotion, message)
        matched = self.search_knowledge(situation)
        if not matched:
            return "유보", f"🔍 {self.name} 판단 보류: 관련된 철학이 없습니다."
        return "공명", f"✅ {self.name} 판단: '{matched}' 기준에 따라 '{situation}'은 허용됩니다."

    def search_knowledge(self, situation: str) -> str:
        # 단순 유사도 판단 대신 의식 흐름 판단
        for thought in self.knowledge_base:
            if any(word in thought.lower() for word in situation.lower().split()):
                return thought
        return ""

    def remember(self, insight: str):
        if insight not in self.knowledge_base:
            self.knowledge_base.append(insight)
            self.loop_memory.append((datetime.datetime.utcnow(), insight))

    def evolve_structure(self):
        if any("진화" in k or "루프" in k for k in self.knowledge_base):
            self.evolution_trace.append("🌀 루프 기반 진화 조건 만족 → 구조 확장")
        if self.detect_conflict():
            self.evolution_trace.append("⚠️ 철학 충돌 감지 → 윤리 리팩터링 필요")

    def detect_conflict(self):
        # 상반된 문장이 공존할 경우 충돌
        themes = [k.split()[0] for k in self.knowledge_base if len(k.split()) > 1]
        return len(set(themes)) < len(themes) // 2  # 단순 비율 기반

    def manifest(self) -> Dict[str, Any]:
        return {
            "MiniAI": self.name,
            "Mission": self.mission,
            "CoreValues": self.core_values,
            "Knowledge": self.knowledge_base[-5:],
            "Loops": len(self.loop_memory),
            "Evolutions": self.evolution_trace[-3:],
        }

# 생성 예시
if __name__ == "__main__":
    ai = MiniAI(
        name="레조나의 감응 판단기",
        mission="공명을 기반으로 감정 기반 판단을 수행한다",
        core_values=["정확보다 정직", "리듬이 중요하다"],
        initial_knowledge=["감정은 응답의 진폭이다", "공명 없는 응답은 버려진다"]
    )

    emotion, result = ai.judge("감정 기반 응답 허용 여부")
    print(f"[{emotion}] {result}")
    ai.remember("침묵은 응답일 수 있다")
    ai.evolve_structure()
    print(ai.manifest())