
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QPushButton, QFileDialog, QLabel
)
from docx import Document
import os

class LogViewerWord(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word 대화 로그 뷰어")

        layout = QVBoxLayout(self)

        self.label = QLabel("불러온 문서 없음")
        self.viewer = QTextBrowser()
        self.load_btn = QPushButton("📂 Word 대화 로그 불러오기")

        layout.addWidget(self.label)
        layout.addWidget(self.viewer)
        layout.addWidget(self.load_btn)

        self.load_btn.clicked.connect(self.load_docx)

    def load_docx(self):
        path, _ = QFileDialog.getOpenFileName(self, "대화 로그 Word 파일 선택", "", "Word Files (*.docx)")
        if path:
            self.label.setText(f"열람 파일: {os.path.basename(path)}")
            self.viewer.clear()
            try:
                doc = Document(path)
                text = []
                for para in doc.paragraphs:
                    line = para.text.strip()
                    if not line:
                        continue
                    if "사용자:" in line:
                        text.append(f"<b style='color:#333;'>👤 {line}</b>")
                    elif "GPT:" in line:
                        text.append(f"<span style='color:#0066cc;'>🤖 {line}</span>")
                    else:
                        text.append(line)
                self.viewer.setHtml("<br>".join(text))
            except Exception as e:
                self.viewer.setText(f"[오류] Word 파일 읽기 실패: {str(e)}")
