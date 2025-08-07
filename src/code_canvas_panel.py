from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
import os

class CodeCanvasPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("여기에 코드 또는 문서가 표시됩니다...")
        self.editor.setStyleSheet("font-family: Consolas; font-size: 14px;")
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def load_file(self, filepath):
        if not os.path.exists(filepath):
            self.editor.setPlainText("❌ 파일을 찾을 수 없습니다.")
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            self.editor.setPlainText(text)
        except Exception as e:
            self.editor.setPlainText(f"❌ 파일 열기 실패: {e}")
