class AutoLoopEvaluator:
    def __init__(self):
        self.previous_inputs = []

    def detect_loop(self, current_input):
        self.previous_inputs.append(current_input)
        if len(self.previous_inputs) > 5:
            recent = self.previous_inputs[-5:]
            if all(q == recent[0] for q in recent):
                print("🔁 루프 감지됨: 동일한 질문이 반복되고 있습니다.")
                return True
        return False