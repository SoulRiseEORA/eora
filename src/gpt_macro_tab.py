
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class GPTMacroTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("⚙️ 매크로 자동화 기능")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin: 12px 0;")
        layout.addWidget(title)

        self.record_btn = QPushButton("🔴 매크로 녹화 시작")
        self.stop_btn = QPushButton("⏹️ 녹화 종료")
        self.play_btn = QPushButton("▶️ 재실행")
        self.export_btn = QPushButton("📤 내보내기")
        self.import_btn = QPushButton("📥 불러오기")

        for btn in [self.record_btn, self.stop_btn, self.play_btn, self.export_btn, self.import_btn]:
            btn.setFixedHeight(40)
            layout.addWidget(btn)
