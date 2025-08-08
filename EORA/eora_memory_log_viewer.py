
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
import json
import os

class EmotionMemoryLogViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)
        self.setLayout(self.layout)
        self.load_emotion_log()

    def load_emotion_log(self):
        path = "EORA/memory/emotion_memory.json"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    lines = []
                    for i, item in enumerate(data[-30:], 1):
                        line = f"[{i}] {item.get('time', '?')} :: {item.get('content', '')}"
                        lines.append(line)
                    self.output.setPlainText("\n".join(lines))
                else:
                    self.output.setPlainText("⚠️ 올바르지 않은 감정 메모리 형식입니다.")
            except Exception as e:
                self.output.setPlainText(f"[불러오기 오류] {e}")
        else:
            self.output.setPlainText("⚠️ 감정 메모리 파일이 없습니다.")
