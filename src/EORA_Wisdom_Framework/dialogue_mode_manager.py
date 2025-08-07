# dialogue_mode_manager.py
# AI의 현재 대화 모드를 관리하며, 감지된 상황에 따라 전환 여부를 판단합니다.

class DialogueModeManager:
    def __init__(self):
        self.current_mode = "일상"
        self.last_stable_context = "일상"
        self.turns_since_last_change = 0
        self.change_threshold = 7  # 7턴마다만 상황 전환 허용 (급변 방지)

    def should_change_mode(self, new_context: str) -> bool:
        """
        새로운 상황과 기존 모드를 비교하여 전환 여부 결정
        - 명확히 다른 명령(작업 요청 등)이면 즉시 전환
        - 그 외는 최소 7턴 유지
        """
        if new_context == "작업 요청":
            return True  # 즉시 전환

        if new_context != self.current_mode:
            if self.turns_since_last_change >= self.change_threshold:
                return True

        return False

    def update_mode(self, new_context: str):
        """
        모드 전환 수행 및 내부 상태 갱신
        """
        if new_context != self.current_mode:
            self.current_mode = new_context
            self.turns_since_last_change = 0
        else:
            self.turns_since_last_change += 1

    def get_mode(self) -> str:
        return self.current_mode


if __name__ == "__main__":
    manager = DialogueModeManager()
    context_sequence = ["일상", "일상", "코칭 요청", "코칭 요청", "코칭 요청", "코칭 요청", "코칭 요청", "코칭 요청", "코칭 요청"]

    for ctx in context_sequence:
        if manager.should_change_mode(ctx):
            manager.update_mode(ctx)
        else:
            pass

