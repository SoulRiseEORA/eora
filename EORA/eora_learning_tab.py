from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTextBrowser,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QListWidget
)
from docx import Document
import os
from EORA.trainer_engine import simulate_training
from EORA.file_analyzer import analyze_file
from EORA.eora_journal_writer import write_journal_entry
from EORA.eora_memory import remember_eora
from markdown2 import markdown

class EORALearningTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EORA 학습 탭")
        self.files = []

        layout = QVBoxLayout(self)
        self.add_btn = QPushButton("📂 학습할 문서 등록")
        self.add_btn.clicked.connect(self.load_docs)
        layout.addWidget(self.add_btn)

        self.file_list = QListWidget()
        layout.addWidget(QLabel("📎 첨부 문서 목록"))
        layout.addWidget(self.file_list)

        self.start_btn = QPushButton("🧠 학습시작")
        layout.addWidget(self.start_btn)

        self.log_output = QTextBrowser()
        self.log_output.setFixedHeight(200)
        self.log_output.setStyleSheet("background-color:#fefefe; font-size:14px; font-family:'NanumGothic'; padding:10px; border:1px solid #ddd;")
        layout.addWidget(QLabel("💬 학습 로그"))
        layout.addWidget(self.log_output)

        self.start_btn.clicked.connect(self.start_learning)

    def load_docs(self):
        from PyQt5.QtWidgets import QFileDialog
        paths, _ = QFileDialog.getOpenFileNames(self, "EORA 학습 파일 선택", "", "문서 파일 (*.docx *.txt *.py *.md *.xlsx *.xls *.pdf)")
        for path in paths:
            if path not in self.files:
                self.files.append(path)
                self.file_list.addItem(path)

    def start_learning(self):
        from datetime import datetime
        from EORA.memory_db import save_chunk
        import os
        self.log_output.clear()
        for file_idx, path in enumerate(self.files):
            self.log_output.append(f"\n📄 [{file_idx+1}/{len(self.files)}] {os.path.basename(path)}: 학습 시작...")
            text = ""
            try:
                if path.endswith(".docx"):
                    from docx import Document
                    doc = Document(path)
                    text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                elif path.endswith(".xlsx") or path.endswith(".xls"):
                    import pandas as pd
                    df = pd.read_excel(path, sheet_name=None)
                    for sheet, data in df.items():
                        text += f"[시트: {sheet}]\n"
                        text += data.to_string(index=False)
                        text += "\n"
                elif path.endswith(".pdf"):
                    import PyPDF2
                    text = ""
                    with open(path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                else:
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read()
            except Exception as e:
                self.log_output.append(f"❌ {os.path.basename(path)} 텍스트 추출 오류: {e}")
                continue
            if not text.strip():
                self.log_output.append(f"⚠️ {os.path.basename(path)}: 추출된 텍스트가 없습니다.")
                continue
            chunk_size = 500
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            for idx, chunk in enumerate(chunks):
                meta = {
                    "type": "file_chunk",
                    "chunk_index": idx,
                    "source": path,
                    "timestamp": datetime.utcnow().isoformat()
                }
                save_chunk("첨부파일", chunk, meta)
                self.log_output.append(f"✅ {os.path.basename(path)} - 청크 {idx+1}/{len(chunks)} 저장 완료.")
            self.log_output.append(f"🎉 {os.path.basename(path)}: 학습 완료! (총 {len(chunks)}개 청크 저장)")
