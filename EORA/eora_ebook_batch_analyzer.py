
import os, json, zipfile
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog
from EORA.eora_self_trainer import EoraSelfTrainer

class EBookBatchAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.trainer = EoraSelfTrainer()
        self.layout = QVBoxLayout()
        self.result = QTextEdit()
        self.result.setReadOnly(True)

        self.select_button = QPushButton("📚 전자책 및 문서 파일 분석 실행")
        self.select_button.clicked.connect(self.batch_process)

        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.result)
        self.setLayout(self.layout)

    def batch_process(self):
        path, _ = QFileDialog.getOpenFileName(self, "파일 선택 (ZIP or 단일 파일)", "", "ZIP 파일 (*.zip);;모든 파일 (*)")
        if not path:
            return

        books = []
        if path.endswith(".zip"):
            extract_path = "./_unzipped_books/"
            os.makedirs(extract_path, exist_ok=True)
            with zipfile.ZipFile(path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
            for root, _, files in os.walk(extract_path):
                for f in files:
                    books.append(os.path.join(root, f))
        else:
            books = [path]

        total = len(books)
        success = 0

        for i, file_path in enumerate(books, 1):
            try:
                content = self.extract_text(file_path)
                chunks = self.chunk_text(content)
                for chunk in chunks:
                    self.trainer.think_and_loop(chunk, source=f"{os.path.basename(file_path)}_chunk")
                success += 1
                self.result.append(f"✅ [{i}/{total}] {file_path} 분석 및 저장 완료.")
            except Exception as e:
                self.result.append(f"❌ [{i}/{total}] {file_path} 실패: {e}")

        self.result.append(f"📘 총 {total}개 중 {success}개 성공.")

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
