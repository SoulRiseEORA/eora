
import os, json, zipfile
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QListWidget, QLabel
from EORA.eora_self_trainer import EoraSelfTrainer

class FileAnalyzerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.trainer = EoraSelfTrainer()
        self.files = []
        self.running = False

        self.layout = QVBoxLayout()
        self.file_list = QListWidget()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        self.label = QLabel("📂 파일 또는 ZIP 첨부 후 ▶️ 시작")
        self.load_button = QPushButton("📁 파일/ZIP 첨부")
        self.load_button.clicked.connect(self.load_files)

        self.start_button = QPushButton("▶️ 분석 시작")
        self.start_button.clicked.connect(self.start_analysis)

        self.stop_button = QPushButton("⏹️ 분석 중지")
        self.stop_button.clicked.connect(self.stop_analysis)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.file_list)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.log_output)
        self.setLayout(self.layout)

    def load_files(self):
        self.files.clear()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "파일/ZIP 선택", "", 
            "모든 파일 (*.txt *.pdf *.docx *.json *.md *.py *.zip *.hwp);;ZIP 포함")
        self.file_list.clear()

        for path in file_paths:
            if path.endswith(".zip"):
                extract_path = "./_unzipped_batch/"
                os.makedirs(extract_path, exist_ok=True)
                with zipfile.ZipFile(path, "r") as zip_ref:
                    zip_ref.extractall(extract_path)
                for root, _, files in os.walk(extract_path):
                    for f in files:
                        full = os.path.join(root, f)
                        self.files.append(full)
                        self.file_list.addItem(full)
            else:
                self.files.append(path)
                self.file_list.addItem(path)

        self.log_output.append(f"📎 총 {len(self.files)}개 파일 로드 완료.")

    def start_analysis(self):
        if not self.files:
            self.log_output.append("⚠️ 분석할 파일이 없습니다.")
            return
        self.running = True
        self.log_output.append("🚀 분석 시작...")

        seen_hashes = set()
        for i, file_path in enumerate(self.files, 1):
            if not self.running:
                self.log_output.append("🛑 중지됨.")
                break
            try:
                content = self.extract_text(file_path)
                if not content or len(content.strip()) < 30:
                    self.log_output.append(f"⚠️ [{i}] {file_path} - 내용 부족으로 생략")
                    continue

                content_hash = hash(content.strip()[:1000])
                if content_hash in seen_hashes:
                    self.log_output.append(f"♻️ [{i}] {file_path} - 중복으로 생략")
                    continue
                seen_hashes.add(content_hash)

                chunks = self.chunk_text(content)
                for chunk in chunks:
                    self.trainer.think_and_loop(chunk, source=os.path.basename(file_path))
                self.log_output.append(f"✅ [{i}] {file_path} 분석 완료")
            except Exception as e:
                self.log_output.append(f"❌ [{i}] {file_path} 오류: {e}")

        self.running = False
        self.log_output.append("✅ 전체 분석 완료.")

    def stop_analysis(self):
        self.running = False

    def extract_text(self, path):
        content = ""
        if path.endswith((".txt", ".md", ".py", ".html", ".js")):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        elif path.endswith(".pdf"):
            from PyPDF2 import PdfReader
            reader = PdfReader(path)
            content = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif path.endswith(".docx"):
            from docx import Document
            doc = Document(path)
            content = "\n".join(p.text for p in doc.paragraphs)
        elif path.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                content = json.dumps(data, indent=2, ensure_ascii=False)
        elif path.endswith(".hwp"):
            import olefile
            ole = olefile.OleFileIO(path)
            content = str(ole.openstream("PrvText").read(), "utf-16")
        return content

    def chunk_text(self, text, max_tokens=1000):
        size = max_tokens * 4
        return [text[i:i+size].strip() for i in range(0, len(text), size) if text[i:i+size].strip()]
