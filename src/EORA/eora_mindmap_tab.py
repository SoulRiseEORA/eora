
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class MindMapTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.display = QTextEdit()
        self.display.setPlainText("🧠 마인드맵 구조 연결은 향후 시각화로 확장 예정.")
        self.layout.addWidget(self.display)
        self.setLayout(self.layout)
