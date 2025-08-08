import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QTextEdit, QHBoxLayout
)
from PyQt5.QtCore import Qt
import json

class SimulationFileLoader(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.label = QLabel("📂 파일 불러오기: JSON, TXT, DOCX, PDF, HWP")
        self.label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        btn_row = QHBoxLayout()
        self.load_btn = QPushButton("📁 대화 파일 열기")
        self.load_btn.clicked.connect(self.load_conversation_file)
        btn_row.addWidget(self.load_btn)

        self.clear_btn = QPushButton("🧹 로그 지우기")
        self.clear_btn.clicked.connect(self.log.clear)
        btn_row.addWidget(self.clear_btn)

        layout.addLayout(btn_row)

    def load_conversation_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "대화 파일 선택", "", "모든 파일 (*.*)")
        if not file_path:
            return

        ext = os.path.splitext(file_path)[-1].lower()

        try:
            if ext == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.log.append("✅ JSON 대화 불러오기 완료:")
                        for d in data:
                            self.log.append(f"👤 {d.get('user', '')}")
                            self.log.append(f"🤖 {d.get('reply', '')}")
                            self.log.append("-" * 30)
                    else:
                        self.log.append("⚠️ JSON 구조가 리스트가 아닙니다.")
            elif ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    self.log.append("📄 텍스트 불러오기:")
                    self.log.append(f.read())
            elif ext == ".pdf":
                from PyPDF2 import PdfReader
                reader = PdfReader(file_path)
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                self.log.append("📘 PDF 내용:")
                self.log.append(text)
            elif ext == ".docx":
                from docx import Document
                doc = Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs])
                self.log.append("📄 워드 문서:")
                self.log.append(text)
            elif ext == ".hwp":
                import olefile
                if not olefile.isOleFile(file_path):
                    self.log.append("⚠️ HWP 포맷이 올바르지 않습니다.")
                    return
                ole = olefile.OleFileIO(file_path)
                encoded_text = ole.openstream("PrvText").read().decode("utf-16")
                self.log.append("📄 한글 HWP 문서:")
                self.log.append(encoded_text)
            else:
                self.log.append("❌ 지원되지 않는 파일 형식입니다.")
        except Exception as e:
            self.log.append(f"❌ 불러오기 오류: {str(e)}")