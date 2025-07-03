
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
import json
import os

class EORAJournalViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        self.layout.addWidget(self.viewer)
        self.setLayout(self.layout)
        self.load_journal()

    def load_journal(self):
        path = "EORA/memory/eora_journal.json"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    lines = []
                    for i, entry in enumerate(data[-30:], 1):
                        time = entry.get("time", "?")
                        title = entry.get("title", "")
                        content = entry.get("content", "")
                        lines.append(f"[{i}] {time} :: {title}\n{content}\n")
                    self.viewer.setPlainText("\n".join(lines))
                else:
                    self.viewer.setPlainText("⚠️ 형식 오류: 리스트가 아님")
            except Exception as e:
                self.viewer.setPlainText(f"[오류] {e}")
        else:
            self.viewer.setPlainText("⚠️ 이오라 저널 파일이 없습니다.")
