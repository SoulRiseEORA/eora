
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
import json, os

class GoalTrackerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        self.layout.addWidget(self.viewer)
        self.setLayout(self.layout)
        self.load_goals()

    def load_goals(self):
        path = "EORA/memory/goals.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.viewer.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            self.viewer.setPlainText("⚠️ 목표 파일이 없습니다.")
