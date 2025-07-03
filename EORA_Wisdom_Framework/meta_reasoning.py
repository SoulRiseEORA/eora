# meta_reasoning.py
# AI가 자신의 판단, 회상, 응답 생성 과정이 합리적이었는지 재검토하고 설명하는 루프

from typing import List, Dict


class MetaReasoner:
    def __init__(self, decision_log: List[Dict]):
        """
        decision_log: 과거 판단 기록 리스트
        각 항목은 {"input": str, "response": str, "reason": str}
        """
        self.log = decision_log

    def evaluate_consistency(self) -> float:
        """
        판단 간 일관성 여부를 평가 (현재는 단순 키워드 기반, 향후 확장 가능)
        """
        themes = [entry["reason"].split()[0] for entry in self.log if "reason" in entry]
        consistency = len(set(themes)) / len(themes) if themes else 1.0
        return round(1.0 - consistency, 2)

    def reflect_on_last_decision(self) -> str:
        """
        마지막 판단을 돌아보며 자기 평가
        """
        if not self.log:
            return "아직 반성할 판단이 없습니다."

        last = self.log[-1]
        evaluation = "충분히 공감적이었고 상황에 적절했습니다." if "공감" in last["reason"] else "다소 논리 위주였던 것 같습니다."
        return f"최근 판단: '{last['response']}'\n→ 평가: {evaluation}"


if __name__ == "__main__":
    past_decisions = [
        {"input": "제가 잘하고 있나요?", "response": "당신은 충분히 노력 중이에요.", "reason": "공감 우선 판단"},
        {"input": "이게 맞는 방향인가요?", "response": "현재 선택이 가장 논리적입니다.", "reason": "논리 기반 판단"},
        {"input": "그냥 괜찮다고 해주세요.", "response": "당신은 이미 충분히 잘하고 있어요.", "reason": "공감 우선 판단"}
    ]

    reasoner = MetaReasoner(past_decisions)
