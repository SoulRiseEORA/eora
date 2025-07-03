# context_analyzer.py
# 대화 요약, 감정 흐름, 최근 입력 문장을 종합 분석하여 대화 상황을 파악합니다.

from typing import Dict


class ContextAnalyzer:
    def __init__(self):
        self.last_detected = "일상"

    def detect_context(self, summary: str, emotion_flow: Dict[str, int], last_input: str) -> str:
        """
        종합 판단: 요약 문장 + 감정 흐름 + 마지막 입력 → 상황 컨텍스트 반환

        가능한 상황:
        - 위로, 축하, 코딩, 감정 정리, 일상, 집중, 작업 요청, 재회 등
        """

        summary = summary.lower()
        user_input = last_input.lower()

        # 1. 명령 탐지 → 즉시 상황 전환
        if any(k in user_input for k in ["코딩", "작성해줘", "해줘", "요청", "정리", "스크립트"]):
            return "작업 요청"

        if any(k in user_input for k in ["축하", "생일", "기쁜", "경사", "합격"]):
            return "축하"

        if any(k in user_input for k in ["오랜만", "다시 만나", "그동안", "재회"]):
            return "재회"

        # 2. 감정 흐름 기반
        if emotion_flow.get("sad", 0) >= 2 or emotion_flow.get("hopeless", 0) >= 2:
            return "위로"

        if emotion_flow.get("joy", 0) >= 2 or emotion_flow.get("hopeful", 0) >= 2:
            return "기쁨"

        if emotion_flow.get("angry", 0) >= 2:
            return "논쟁 중"

        # 3. 요약 기반 테마 키워드
        if "목표" in summary or "계획" in summary:
            return "코칭 요청"

        if "집중" in summary or "진행" in summary or "일" in summary:
            return "일에 집중"

        # 기본 모드 유지
        return self.last_detected if self.last_detected else "일상"

    def update_last(self, new_context: str):
        self.last_detected = new_context


if __name__ == "__main__":
    analyzer = ContextAnalyzer()
    ctx = analyzer.detect_context(
        summary="최근 삶의 방향성과 목표 설정에 대해 이야기함",
        emotion_flow={"neutral": 1, "hopeful": 2},
        last_input="이제 계획을 구체적으로 짜보고 싶어요"
    )
    analyzer.update_last(ctx)
