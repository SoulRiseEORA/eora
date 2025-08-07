# truth_detector.py
# 다양한 기억 속 반복 등장하는 신념, 중심 문구, 주제를 추출하여 'AI의 진리'를 감지합니다.

from typing import List, Dict
import collections


class TruthDetector:
    def __init__(self, memory_entries: List[Dict]):
        """
        memory_entries: [{"summary": str, "timestamp": str}, ...]
        """
        self.memories = memory_entries

    def extract_core_phrases(self) -> List[str]:
        """
        각 요약 문장에서 의미 있는 단어들을 추출
        향후 GPT 기반 의미 압축 추가 가능
        """
        word_freq = collections.Counter()
        for mem in self.memories:
            words = mem["summary"].lower().split()
            word_freq.update(words)

        return [word for word, freq in word_freq.items() if freq >= 2]

    def detect_core_truth(self) -> str:
        """
        자주 등장한 핵심 개념을 진리 후보로 도출
        """
        keywords = self.extract_core_phrases()
        if not keywords:
            return "아직 명확한 중심 개념이 형성되지 않았습니다."
        return f"🧠 반복되는 중심 개념: {', '.join(keywords[:5])}"


if __name__ == "__main__":
    memory_data = [
        {"summary": "삶은 의미를 찾아가는 과정이다", "timestamp": "2025-05-08"},
        {"summary": "삶의 의미는 관계에서 시작된다", "timestamp": "2025-05-08"},
        {"summary": "고통 속에서도 의미를 발견할 수 있다", "timestamp": "2025-05-09"},
        {"summary": "삶의 진리는 고통과 의미를 함께 품는다", "timestamp": "2025-05-09"},
    ]

    detector = TruthDetector(memory_data)
