
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
import json, os

class ProfileEditorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.editor = QTextEdit()
        self.layout.addWidget(self.editor)
        self.setLayout(self.layout)
        self.load_profile()

    def load_profile(self):
        path = "EORA/profile/self_profile.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.editor.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            self.editor.setPlainText("⚠️ 자기소개 프로필 파일이 없습니다.")
