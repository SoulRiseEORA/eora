from PyQt5.QtCore import QThread, pyqtSignal
from ai_chat import get_eora_instance

class GPTWorker(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, user_input: str, system_message: str = ""):
        super().__init__()
        self.user_input = user_input
        self.system_message = system_message

    def run(self):
        try:
            eora = get_eora_instance()
            result = eora.ask(self.user_input, self.system_message)
            self.result_ready.emit(result)
        except Exception as e:
            self.result_ready.emit(f"❌ GPT 호출 실패: {str(e)}")
