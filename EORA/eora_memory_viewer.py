
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QPushButton
from EORA.eora_memory import load_memory_chunks

class MemoryViewerTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.view = QTextBrowser()
        self.refresh_btn = QPushButton("🔄 기억 다시 불러오기")
        self.refresh_btn.clicked.connect(self.refresh_memory)

        layout.addWidget(self.view)
        layout.addWidget(self.refresh_btn)
        self.setLayout(layout)

        self.refresh_memory()

    def refresh_memory(self):
        chunks = load_memory_chunks("EORA_요약")
        display = "\n\n".join(f"🧠 {i+1}. {chunk}" for i, chunk in enumerate(chunks))
        self.view.setPlainText(display if display else "🕳️ 아직 기억된 내용이 없습니다.")
