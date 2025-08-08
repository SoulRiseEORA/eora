
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class PromptGraphEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.graph = QTextEdit()
        self.graph.setPlainText("📊 프롬프트 관계 그래프는 추후 GPT 기반으로 시각화 가능합니다.")
        self.layout.addWidget(self.graph)
        self.setLayout(self.layout)
