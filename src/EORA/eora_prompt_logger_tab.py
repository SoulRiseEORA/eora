
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
import json
import os

class PromptLoggerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.layout.addWidget(self.log_viewer)
        self.setLayout(self.layout)
        self.load_prompt_log()

    def load_prompt_log(self):
        path = "EORA/logs/prompt_history_log.json"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    logs = []
                    for i, entry in enumerate(data[-50:], 1):
                        line = f"[{i}] {entry.get('timestamp', '?')} :: {entry.get('section', '?')} → {entry.get('content', '')}"
                        logs.append(line)
                    self.log_viewer.setPlainText("\n".join(logs))
                else:
                    self.log_viewer.setPlainText("⚠️ 올바르지 않은 로그 형식입니다.")
            except Exception as e:
                self.log_viewer.setPlainText(f"[불러오기 오류] {e}")
        else:
            self.log_viewer.setPlainText("⚠️ 프롬프트 로그 파일이 없습니다.")
