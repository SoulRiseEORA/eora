
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
import json
import os

class PromptStorageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        self.layout.addWidget(self.viewer)
        self.setLayout(self.layout)
        self.load_prompts()

    def load_prompts(self):
        path = "ai_brain/ai_prompts.json"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.viewer.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
            except Exception as e:
                self.viewer.setPlainText(f"[불러오기 오류] {e}")
        else:
            self.viewer.setPlainText("⚠️ 프롬프트 저장소 파일이 없습니다.")
