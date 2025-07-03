
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel

class DebugTabAI2AI3(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("🔧 AI2 (레조나) / AI3 (금강) 디버깅")

        self.ai2_input = QLineEdit()
        self.ai2_input.setPlaceholderText("레조나에게 질문 입력...")
        self.ai2_send = QPushButton("📤 전송 (AI2)")
        self.ai2_send.clicked.connect(self.ask_ai2)

        self.ai3_input = QLineEdit()
        self.ai3_input.setPlaceholderText("금강에게 질문 입력...")
        self.ai3_send = QPushButton("📤 전송 (AI3)")
        self.ai3_send.clicked.connect(self.ask_ai3)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.ai2_input)
        self.layout.addWidget(self.ai2_send)
        self.layout.addWidget(self.ai3_input)
        self.layout.addWidget(self.ai3_send)
        self.layout.addWidget(QLabel("🧠 응답 출력"))
        self.layout.addWidget(self.output)
        self.setLayout(self.layout)

    def ask_ai2(self):
        msg = self.ai2_input.text().strip()
        if msg:
            self.output.append(f"🟣 AI2 (레조나): {msg}")
            self.output.append(f"🔵 응답: AI2는 '{msg}'에 대해 판단을 시작합니다...\n")

    def ask_ai3(self):
        msg = self.ai3_input.text().strip()
        if msg:
            self.output.append(f"🟡 AI3 (금강): {msg}")
            self.output.append(f"🔵 응답: AI3는 '{msg}'에 대해 코드 분석을 시작합니다...\n")
